#include "Causality/GenesisCausality.h"

#include "Engine/GameInstance.h"
#include "Genesis.h"
#include "Npc/GenesisNpc.h"
#include "Save/GenesisSaveSubsystem.h"
#include "World/GenesisWorld.h"

const FGenesisEventTypeDef* UGenesisCausalitySettings::FindType(FName EventType) const
{
	return EventTypes.FindByPredicate([EventType](const FGenesisEventTypeDef& Def) { return Def.EventType == EventType; });
}

namespace
{
	FGenesisNpcState& FindOrAddNpc(FGenesisSaveBundle& Bundle, FName NpcId)
	{
		if (FGenesisNpcState* Existing = Bundle.World.Npcs.FindByPredicate([NpcId](const FGenesisNpcState& S) { return S.NpcId == NpcId; }))
		{
			return *Existing;
		}
		FGenesisNpcState& Added = Bundle.World.Npcs.AddDefaulted_GetRef();
		Added.NpcId = NpcId;
		return Added;
	}

	/** Wer schon eine starke Meinung hat, aendert sie langsamer. */
	float Nudge(float Current, float Delta)
	{
		return FMath::Clamp(Current + Delta * (1.f - 0.5f * FMath::Abs(Current)), -1.f, 1.f);
	}

	void ApplyAttitude(FGenesisNpcState& Npc, FName SubjectId, const FGenesisEventTypeDef& Def, float Factor)
	{
		FGenesisAttitude& Attitude = Npc.Attitudes.FindOrAdd(SubjectId);
		Attitude.Trust = Nudge(Attitude.Trust, Def.TrustDelta * Factor);
		Attitude.Affinity = Nudge(Attitude.Affinity, Def.AffinityDelta * Factor);
	}

	void AddMemory(FGenesisNpcState& Npc, const FGenesisCausalEvent& Event, EGenesisMemorySource Source, float Salience, float PerceivedValence, FName HeardFrom)
	{
		FGenesisNpcMemory& Memory = Npc.Memories.AddDefaulted_GetRef();
		Memory.EventId = Event.EventId;
		Memory.Source = Source;
		Memory.HeardFrom = HeardFrom;
		Memory.InitialSalience = FMath::Clamp(Salience, 0.f, 1.f);
		Memory.PerceivedValence = FMath::Clamp(PerceivedValence, -1.f, 1.f);
		Memory.FormedAt = Event.WorldTime;
	}

	bool IsPlayerId(FName Id)
	{
		return Id.ToString().StartsWith(TEXT("PLAYER_L"));
	}
}

FName FGenesisCausality::PlayerSubjectId(int32 LifeIndex)
{
	return FName(*FString::Printf(TEXT("PLAYER_L%d"), LifeIndex));
}

const FGenesisCausalEvent* FGenesisCausality::FindEvent(const FGenesisSaveBundle& Bundle, FName EventId)
{
	return Bundle.World.CausalEvents.FindByPredicate([EventId](const FGenesisCausalEvent& E) { return E.EventId == EventId; });
}

const FGenesisNpcState* FGenesisCausality::FindNpc(const FGenesisSaveBundle& Bundle, FName NpcId)
{
	return Bundle.World.Npcs.FindByPredicate([NpcId](const FGenesisNpcState& S) { return S.NpcId == NpcId; });
}

FName FGenesisCausality::RecordEvent(FGenesisSaveBundle& Bundle, const FGenesisEventSpec& Spec, const UGenesisCausalitySettings& Settings, FString* OutError)
{
	auto Fail = [OutError](const FString& Message)
	{
		if (OutError)
		{
			*OutError = Message;
		}
		UE_LOG(LogGenesis, Warning, TEXT("Kausalgraph: Ereignis abgelehnt: %s"), *Message);
		return NAME_None;
	};

	const FGenesisEventTypeDef* Def = Settings.FindType(Spec.EventType);
	if (!Def)
	{
		return Fail(FString::Printf(TEXT("unbekannter Ereignistyp '%s'"), *Spec.EventType.ToString()));
	}
	if (Spec.ActorId.IsNone())
	{
		return Fail(TEXT("kein Handelnder"));
	}
	for (const FName Cause : Spec.CauseEventIds)
	{
		const FGenesisCausalEvent* CauseEvent = FindEvent(Bundle, Cause);
		if (!CauseEvent)
		{
			return Fail(FString::Printf(TEXT("Ursache '%s' existiert nicht"), *Cause.ToString()));
		}
		if (CauseEvent->WorldTime > Bundle.World.WorldDateTime)
		{
			return Fail(FString::Printf(TEXT("Ursache '%s' liegt in der Zukunft"), *Cause.ToString()));
		}
	}

	FGenesisCausalEvent& Event = Bundle.World.CausalEvents.AddDefaulted_GetRef();
	Event.EventId = FName(*FString::Printf(TEXT("EV_%06lld"), Bundle.World.NextEventSerial++));
	Event.EventType = Spec.EventType;
	Event.WorldTime = Bundle.World.WorldDateTime;
	Event.LocationId = Spec.LocationId.IsNone() ? Bundle.Life.LocationId : Spec.LocationId;
	Event.LifeIndex = Bundle.Life.LifeIndex;
	Event.ActorId = Spec.ActorId;
	Event.TargetIds = Spec.TargetIds;
	Event.WitnessIds = Spec.WitnessIds;
	Event.CauseEventIds = Spec.CauseEventIds;
	Event.Valence = Def->DefaultValence;
	Event.Magnitude = Spec.MagnitudeOverride >= 0.f ? FMath::Clamp(Spec.MagnitudeOverride, 0.f, 1.f) : Def->DefaultMagnitude;
	Event.ContextTag = Spec.ContextTag;
	const FGenesisCausalEvent EventCopy = Event; // Referenz kann durch weitere Eintraege ungueltig werden

	// Betroffene: volle Wirkung. Zeugen: abgeschwaecht. Der Spieler selbst hat keinen NPC-Zustand.
	for (const FName Target : EventCopy.TargetIds)
	{
		if (Target == EventCopy.ActorId || IsPlayerId(Target) || FGenesisWorldStateLib::IsWorldObjectId(Target))
		{
			continue;
		}
		FGenesisNpcState& Npc = FindOrAddNpc(Bundle, Target);
		AddMemory(Npc, EventCopy, EGenesisMemorySource::Experienced, EventCopy.Magnitude, EventCopy.Valence, NAME_None);
		ApplyAttitude(Npc, EventCopy.ActorId, *Def, 1.f);
	}
	for (const FName Witness : EventCopy.WitnessIds)
	{
		if (Witness == EventCopy.ActorId || EventCopy.TargetIds.Contains(Witness) || IsPlayerId(Witness) || FGenesisWorldStateLib::IsWorldObjectId(Witness))
		{
			continue;
		}
		FGenesisNpcState& Npc = FindOrAddNpc(Bundle, Witness);
		AddMemory(Npc, EventCopy, EGenesisMemorySource::Witnessed, EventCopy.Magnitude * Settings.WitnessFactor, EventCopy.Valence, NAME_None);
		ApplyAttitude(Npc, EventCopy.ActorId, *Def, Settings.WitnessFactor);
	}
	// Eine handelnde Figur erinnert sich an das, was sie getan hat.
	if (!IsPlayerId(EventCopy.ActorId) && !FGenesisWorldStateLib::IsWorldObjectId(EventCopy.ActorId))
	{
		AddMemory(FindOrAddNpc(Bundle, EventCopy.ActorId), EventCopy, EGenesisMemorySource::Experienced, EventCopy.Magnitude, EventCopy.Valence, NAME_None);
	}
	// Verdecktes Verhaltensprofil nur fuer den Spieler des aktuellen Lebens.
	if (EventCopy.ActorId == PlayerSubjectId(Bundle.Life.LifeIndex))
	{
		for (const TPair<FName, float>& Delta : Def->ConductDeltas)
		{
			float& Value = Bundle.Life.ConductProfile.FindOrAdd(Delta.Key);
			Value = FMath::Clamp(Value + Delta.Value, -1.f, 1.f);
		}
	}
	return EventCopy.EventId;
}

bool FGenesisCausality::ShareMemory(FGenesisSaveBundle& Bundle, FName FromNpc, FName ToNpc, FName EventId, const UGenesisCausalitySettings& Settings)
{
	const FGenesisCausalEvent* Event = FindEvent(Bundle, EventId);
	const FGenesisNpcState* From = FindNpc(Bundle, FromNpc);
	const FGenesisNpcMemory* Told = From ? From->Memories.FindByPredicate([EventId](const FGenesisNpcMemory& M) { return M.EventId == EventId; }) : nullptr;
	if (!Event || !Told || FromNpc == ToNpc)
	{
		return false;
	}
	const FGenesisNpcState* ExistingTo = FindNpc(Bundle, ToNpc);
	if (ExistingTo && ExistingTo->Memories.ContainsByPredicate([EventId](const FGenesisNpcMemory& M) { return M.EventId == EventId; }))
	{
		return false;
	}

	// Glaubwuerdigkeit: wem man nicht traut, dem glaubt man weniger.
	const float TrustInTeller = GetAttitude(Bundle, ToNpc, FromNpc).Trust;
	const float Credibility = FMath::Clamp(0.5f + 0.5f * TrustInTeller, 0.f, 1.f);
	const float TellerSalience = GetCurrentSalience(*Told, *Event, Bundle.World.WorldDateTime, Settings);
	const float PerceivedValence = Told->PerceivedValence;
	const FGenesisCausalEvent EventCopy = *Event;

	FGenesisNpcState& To = FindOrAddNpc(Bundle, ToNpc);
	FGenesisNpcMemory& Memory = To.Memories.AddDefaulted_GetRef();
	Memory.EventId = EventId;
	Memory.Source = EGenesisMemorySource::Heard;
	Memory.HeardFrom = FromNpc;
	Memory.InitialSalience = FMath::Clamp(TellerSalience * Settings.HeardFactor * 2.f * Credibility, 0.f, 1.f);
	Memory.PerceivedValence = PerceivedValence;
	Memory.FormedAt = Bundle.World.WorldDateTime;

	if (const FGenesisEventTypeDef* Def = Settings.FindType(EventCopy.EventType))
	{
		if (EventCopy.ActorId != ToNpc)
		{
			ApplyAttitude(To, EventCopy.ActorId, *Def, Settings.HeardFactor * Credibility);
		}
	}
	return true;
}

float FGenesisCausality::GetCurrentSalience(const FGenesisNpcMemory& Memory, const FGenesisCausalEvent& Event, const FDateTime& Now, const UGenesisCausalitySettings& Settings)
{
	const double AgeDays = FMath::Max(0.0, (Now - Memory.FormedAt).GetTotalDays());
	const double HalfLife = Settings.BaseHalfLifeDays * (1.0 + Settings.MagnitudeHalfLifeScale * FMath::Square(Event.Magnitude));
	return float(Memory.InitialSalience * FMath::Pow(0.5, AgeDays / FMath::Max(HalfLife, 1.0)));
}

TArray<FGenesisNpcMemory> FGenesisCausality::GetMemories(const FGenesisSaveBundle& Bundle, FName NpcId, const FDateTime& Now, const UGenesisCausalitySettings& Settings, float MinSalience)
{
	TArray<TPair<float, FGenesisNpcMemory>> Scored;
	if (const FGenesisNpcState* Npc = FindNpc(Bundle, NpcId))
	{
		for (const FGenesisNpcMemory& Memory : Npc->Memories)
		{
			if (const FGenesisCausalEvent* Event = FindEvent(Bundle, Memory.EventId))
			{
				const float Salience = GetCurrentSalience(Memory, *Event, Now, Settings);
				if (Salience >= MinSalience)
				{
					Scored.Emplace(Salience, Memory);
				}
			}
		}
	}
	Scored.StableSort([](const TPair<float, FGenesisNpcMemory>& A, const TPair<float, FGenesisNpcMemory>& B) { return A.Key > B.Key; });
	TArray<FGenesisNpcMemory> Result;
	for (const TPair<float, FGenesisNpcMemory>& Entry : Scored)
	{
		Result.Add(Entry.Value);
	}
	return Result;
}

FGenesisAttitude FGenesisCausality::GetAttitude(const FGenesisSaveBundle& Bundle, FName NpcId, FName SubjectId)
{
	const FGenesisNpcState* Npc = FindNpc(Bundle, NpcId);
	const FGenesisAttitude* Attitude = Npc ? Npc->Attitudes.Find(SubjectId) : nullptr;
	return Attitude ? *Attitude : FGenesisAttitude();
}

EGenesisDisposition FGenesisCausality::ToDisposition(const FGenesisAttitude& Attitude)
{
	const float Score = 0.6f * Attitude.Trust + 0.4f * Attitude.Affinity;
	if (Score <= -0.5f) { return EGenesisDisposition::Hostile; }
	if (Score <= -0.15f) { return EGenesisDisposition::Wary; }
	if (Score < 0.15f) { return EGenesisDisposition::Neutral; }
	if (Score < 0.5f) { return EGenesisDisposition::Warm; }
	return EGenesisDisposition::Close;
}

TArray<FName> FGenesisCausality::GetCauseChain(const FGenesisSaveBundle& Bundle, FName EventId)
{
	TArray<FName> Result;
	TArray<FName> Queue;
	if (const FGenesisCausalEvent* Start = FindEvent(Bundle, EventId))
	{
		Queue = Start->CauseEventIds;
	}
	for (int32 i = 0; i < Queue.Num(); ++i)
	{
		const FName Id = Queue[i];
		if (Result.Contains(Id))
		{
			continue;
		}
		Result.Add(Id);
		if (const FGenesisCausalEvent* Event = FindEvent(Bundle, Id))
		{
			Queue.Append(Event->CauseEventIds);
		}
	}
	return Result;
}

int32 FGenesisCausality::PruneForgotten(FGenesisSaveBundle& Bundle, const FDateTime& Now, const UGenesisCausalitySettings& Settings)
{
	int32 Removed = 0;
	for (FGenesisNpcState& Npc : Bundle.World.Npcs)
	{
		Removed += Npc.Memories.RemoveAll([&](const FGenesisNpcMemory& Memory)
		{
			const FGenesisCausalEvent* Event = FindEvent(Bundle, Memory.EventId);
			return Event && Event->Magnitude < Settings.PermanentMagnitude
				&& GetCurrentSalience(Memory, *Event, Now, Settings) < Settings.ForgetThreshold;
		});
	}
	return Removed;
}

TArray<FString> FGenesisCausality::ValidateGraph(const FGenesisSaveBundle& Bundle)
{
	TArray<FString> Errors;
	TMap<FName, const FGenesisCausalEvent*> ById;
	for (const FGenesisCausalEvent& Event : Bundle.World.CausalEvents)
	{
		if (ById.Contains(Event.EventId))
		{
			Errors.Add(FString::Printf(TEXT("Doppelte EventId %s"), *Event.EventId.ToString()));
		}
		ById.Add(Event.EventId, &Event);
	}
	for (const FGenesisCausalEvent& Event : Bundle.World.CausalEvents)
	{
		for (const FName Cause : Event.CauseEventIds)
		{
			const FGenesisCausalEvent* const* CauseEvent = ById.Find(Cause);
			if (!CauseEvent)
			{
				Errors.Add(FString::Printf(TEXT("%s: Ursache %s fehlt"), *Event.EventId.ToString(), *Cause.ToString()));
			}
			else if ((*CauseEvent)->WorldTime > Event.WorldTime)
			{
				Errors.Add(FString::Printf(TEXT("%s: Ursache %s liegt spaeter"), *Event.EventId.ToString(), *Cause.ToString()));
			}
		}
	}

	// Zyklen per Tiefensuche (0 = neu, 1 = in Arbeit, 2 = fertig).
	TMap<FName, int32> State;
	TFunction<bool(FName)> HasCycle = [&](FName Id) -> bool
	{
		int32& Mark = State.FindOrAdd(Id);
		if (Mark == 1) { return true; }
		if (Mark == 2) { return false; }
		Mark = 1;
		if (const FGenesisCausalEvent* const* Event = ById.Find(Id))
		{
			for (const FName Cause : (*Event)->CauseEventIds)
			{
				if (HasCycle(Cause))
				{
					return true;
				}
			}
		}
		State.FindOrAdd(Id) = 2;
		return false;
	};
	for (const FGenesisCausalEvent& Event : Bundle.World.CausalEvents)
	{
		if (State.FindRef(Event.EventId) == 0 && HasCycle(Event.EventId))
		{
			Errors.Add(FString::Printf(TEXT("Zyklus im Kausalgraphen bei %s"), *Event.EventId.ToString()));
			break;
		}
	}

	for (const FGenesisNpcState& Npc : Bundle.World.Npcs)
	{
		for (const FGenesisNpcMemory& Memory : Npc.Memories)
		{
			if (!ById.Contains(Memory.EventId))
			{
				Errors.Add(FString::Printf(TEXT("%s erinnert unbelegtes Ereignis %s"), *Npc.NpcId.ToString(), *Memory.EventId.ToString()));
			}
		}
		for (const TPair<FName, FGenesisAttitude>& Attitude : Npc.Attitudes)
		{
			if (FMath::Abs(Attitude.Value.Trust) > 1.f || FMath::Abs(Attitude.Value.Affinity) > 1.f)
			{
				Errors.Add(FString::Printf(TEXT("%s: Haltung zu %s ausserhalb -1..1"), *Npc.NpcId.ToString(), *Attitude.Key.ToString()));
			}
		}
	}
	return Errors;
}

FGenesisSaveBundle* UGenesisCausalitySubsystem::GetBundle() const
{
	UGenesisSaveSubsystem* Save = GetGameInstance()->GetSubsystem<UGenesisSaveSubsystem>();
	return Save ? &Save->GetMutable() : nullptr;
}

FName UGenesisCausalitySubsystem::RecordEvent(const FGenesisEventSpec& Spec)
{
	FGenesisSaveBundle* Bundle = GetBundle();
	const FName Id = Bundle ? FGenesisCausality::RecordEvent(*Bundle, Spec, *GetDefault<UGenesisCausalitySettings>()) : NAME_None;
	if (!Id.IsNone())
	{
		OnEventRecorded.Broadcast(Id);
	}
	return Id;
}

bool UGenesisCausalitySubsystem::ShareMemory(FName FromNpc, FName ToNpc, FName EventId)
{
	FGenesisSaveBundle* Bundle = GetBundle();
	return Bundle && FGenesisCausality::ShareMemory(*Bundle, FromNpc, ToNpc, EventId, *GetDefault<UGenesisCausalitySettings>());
}

FName UGenesisCausalitySubsystem::GetCurrentPlayerId() const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	return FGenesisCausality::PlayerSubjectId(Bundle ? Bundle->Life.LifeIndex : 0);
}

FGenesisAttitude UGenesisCausalitySubsystem::GetAttitude(FName NpcId, FName SubjectId) const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	return Bundle ? FGenesisCausality::GetAttitude(*Bundle, NpcId, SubjectId) : FGenesisAttitude();
}

TArray<FName> UGenesisCausalitySubsystem::GetCauseChain(FName EventId) const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	return Bundle ? FGenesisCausality::GetCauseChain(*Bundle, EventId) : TArray<FName>();
}

FName UGenesisCausalitySubsystem::RecordEventAt(const FGenesisEventSpec& Spec, FVector Location, AActor* ActorInWorld)
{
	FGenesisEventSpec WithWitnesses = Spec;
	TArray<FName> Exclude = Spec.TargetIds;
	Exclude.Add(Spec.ActorId);
	for (const FName Witness : FGenesisPerception::FindWitnesses(GetGameInstance()->GetWorld(), Location, ActorInWorld, Exclude))
	{
		WithWitnesses.WitnessIds.AddUnique(Witness);
	}
	return RecordEvent(WithWitnesses);
}
