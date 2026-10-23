#include "World/GenesisFlussdorf.h"

#include "Causality/GenesisCausality.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Genesis.h"
#include "NavigationPath.h"
#include "NavigationSystem.h"
#include "Npc/GenesisNpc.h"
#include "Npc/GenesisNpcTypes.h"
#include "Save/GenesisSaveSubsystem.h"
#include "Story/GenesisStory.h"
#include "World/GenesisWorld.h"

#define LOCTEXT_NAMESPACE "GenesisFlussdorf"

namespace GenesisFlussdorf
{
	const FName Weather(TEXT("WEATHER"));
	const FName PhaseKey(TEXT("WX.Phase"));
	const FName PublicWarningKey(TEXT("WX.PublicWarning"));
	const FName RiverCmKey(TEXT("WX.RiverCm"));
	const FName Context(TEXT("VS01"));

	const FName Home(TEXT("Home"));
	const FName Sleep(TEXT("Sleep"));
	const FName Secure(TEXT("Secure"));
	const FName Deliver(TEXT("Deliver"));

	FGenesisEventSpec Spec(FName Type, FName Actor, TArray<FName> Targets, TArray<FName> Causes, FName Location)
	{
		FGenesisEventSpec S;
		S.EventType = Type;
		S.ActorId = Actor;
		S.TargetIds = MoveTemp(Targets);
		S.CauseEventIds = MoveTemp(Causes);
		S.CauseEventIds.Remove(NAME_None);
		S.LocationId = Location;
		S.ContextTag = Context;
		return S;
	}

	TArray<FName> Causes(FName A, FName B = NAME_None)
	{
		TArray<FName> Result;
		if (!A.IsNone()) { Result.Add(A); }
		if (!B.IsNone()) { Result.Add(B); }
		return Result;
	}

	FName Key(FName Object, const TCHAR* Value)
	{
		return FName(*FString::Printf(TEXT("%s.%s"), *Object.ToString(), Value));
	}

	int32 DayStamp(const FDateTime& Time)
	{
		return Time.GetYear() * 10000 + Time.GetMonth() * 100 + Time.GetDay();
	}
}

// ---------------------------------------------------------------- Regeln

bool FGenesisFlussdorfRules::Knows(const FGenesisSaveBundle& Bundle, FName NpcId, FName EventType)
{
	const FGenesisNpcState* Npc = FGenesisCausality::FindNpc(Bundle, NpcId);
	if (!Npc)
	{
		return false;
	}
	for (const FGenesisNpcMemory& Memory : Npc->Memories)
	{
		const FGenesisCausalEvent* Event = FGenesisCausality::FindEvent(Bundle, Memory.EventId);
		if (Event && Event->EventType == EventType)
		{
			return true;
		}
	}
	return false;
}

bool FGenesisFlussdorfRules::KnowsWarning(const FGenesisSaveBundle& Bundle, FName NpcId)
{
	return Knows(Bundle, NpcId, TEXT("WARNING_RECEIVED")) || Knows(Bundle, NpcId, TEXT("PUBLIC_WARNING"));
}

FName FGenesisFlussdorfRules::FindLatestEvent(const FGenesisSaveBundle& Bundle, FName EventType)
{
	for (int32 i = Bundle.World.CausalEvents.Num() - 1; i >= 0; --i)
	{
		if (Bundle.World.CausalEvents[i].EventType == EventType)
		{
			return Bundle.World.CausalEvents[i].EventId;
		}
	}
	return NAME_None;
}

EGenesisWeatherPhase FGenesisFlussdorfRules::GetProcessedPhase(const FGenesisSaveBundle& Bundle)
{
	return EGenesisWeatherPhase(FMath::Clamp(Bundle.World.EventFlags.FindRef(GenesisFlussdorf::PhaseKey), 0, int32(EGenesisWeatherPhase::Settled)));
}

bool FGenesisFlussdorfRules::IsBridgeBlocked(const FGenesisSaveBundle& Bundle)
{
	const UGenesisFlussdorfSettings& S = *GetDefault<UGenesisFlussdorfSettings>();
	return FGenesisWorldStateLib::GetObjectValue(Bundle, S.Bridge, TEXT("Blocked")) != 0;
}

void FGenesisFlussdorfRules::AdvanceWeather(FGenesisSaveBundle& Bundle, const FGenesisStormTimeline& Timeline, const FDateTime& From, const FDateTime& To,
	FRecord Record, TArray<FName>& OutTriggers)
{
	using namespace GenesisFlussdorf;
	const UGenesisFlussdorfSettings& S = *GetDefault<UGenesisFlussdorfSettings>();
	const UGenesisWeatherSettings& W = *GetDefault<UGenesisWeatherSettings>();

	// 1. Phasenwechsel in Reihenfolge (ein Zeitraffer kann mehrere ueberspringen, keiner wird doppelt gebucht).
	const EGenesisWeatherPhase Target = Timeline.GetPhase(To);
	for (int32 P = int32(GetProcessedPhase(Bundle)) + 1; P <= int32(Target); ++P)
	{
		Bundle.World.EventFlags.Add(PhaseKey, P);
		switch (EGenesisWeatherPhase(P))
		{
		case EGenesisWeatherPhase::Precursor:
			Record(Spec(TEXT("WEATHER_PRECURSOR"), Weather, {}, {}, TEXT("R06")));
			OutTriggers.Add(TEXT("WX_PRECURSOR"));
			break;
		case EGenesisWeatherPhase::Alert:
		{
			const FName Alert = Record(Spec(TEXT("WEATHER_ALERT"), S.Station, {}, Causes(FindLatestEvent(Bundle, TEXT("WEATHER_PRECURSOR"))), TEXT("R06")));
			FGenesisWorldStateLib::SetObjectValue(Bundle, S.Station, TEXT("Alert"), 1, Alert);
			OutTriggers.Add(TEXT("WX_ALERT"));
			break;
		}
		case EGenesisWeatherPhase::Storm:
			Record(Spec(TEXT("STORM"), Weather, {}, Causes(FindLatestEvent(Bundle, TEXT("WEATHER_PRECURSOR"))), TEXT("R04")));
			OutTriggers.Add(TEXT("WX_STORM"));
			break;
		case EGenesisWeatherPhase::Receding:
			Record(Spec(TEXT("STORM_RECEDED"), Weather, {}, Causes(FindLatestEvent(Bundle, TEXT("STORM"))), TEXT("R04")));
			OutTriggers.Add(TEXT("WX_RECEDED"));
			break;
		case EGenesisWeatherPhase::Over:
			FGenesisWorldStateLib::SetObjectValue(Bundle, S.Station, TEXT("Alert"), 0, FindLatestEvent(Bundle, TEXT("STORM_RECEDED")));
			OutTriggers.Add(TEXT("WX_OVER"));
			break;
		case EGenesisWeatherPhase::Settled:
			OutTriggers.Add(TEXT("WX_SETTLED"));
			break;
		default:
			break;
		}
	}

	// 2. Stationsalarm erreicht N05 nach der Meldezeit (Ersatz fuer die fehlende Rolle N06, siehe Einstellungen).
	const FName AlertEvent = FindLatestEvent(Bundle, TEXT("WEATHER_ALERT"));
	if (const FGenesisCausalEvent* Alert = FGenesisCausality::FindEvent(Bundle, AlertEvent))
	{
		const bool bKnown = Knows(Bundle, S.CommunityCoordinator, TEXT("ALERT_RELAYED")) || Knows(Bundle, S.CommunityCoordinator, TEXT("ALERT_REPORTED"));
		if (!bKnown && To >= Alert->WorldTime + FTimespan::FromMinutes(S.AlertRelayMinutes))
		{
			Record(Spec(TEXT("ALERT_RELAYED"), S.Station, { S.CommunityCoordinator }, Causes(AlertEvent), TEXT("R01")));
		}
	}

	// 3. Schaeden nur aus gemessenem Pegel und Wind (Hoechstwert im Zeitraum: Zeitraffer ueberspringt keine Schwelle).
	const float River = FGenesisWeather::MaxRiverBetween(Timeline, From, To, W);
	const float Wind = FGenesisWeather::MaxWindBetween(Timeline, From, To, W);
	const FName StormCause = FindLatestEvent(Bundle, TEXT("STORM"));
	const FName WeatherCause = StormCause.IsNone() ? FindLatestEvent(Bundle, TEXT("WEATHER_PRECURSOR")) : StormCause;

	if (River >= S.TrailFloodRiverM && FGenesisWorldStateLib::GetObjectValue(Bundle, S.Trail, TEXT("Open")) == 1)
	{
		const FName E = Record(Spec(TEXT("ROUTE_CLOSED"), Weather, { S.Trail }, Causes(WeatherCause), TEXT("R05")));
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Trail, TEXT("Open"), 0, E);
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Trail, TEXT("Blocked"), 1, E);
	}
	if (River >= S.BridgeDamageRiverM && FGenesisWorldStateLib::GetObjectValue(Bundle, S.Bridge, TEXT("Damage")) == 1)
	{
		const FName E = Record(Spec(TEXT("STORM_DAMAGE"), Weather, { S.Bridge }, Causes(WeatherCause), TEXT("R04")));
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Bridge, TEXT("Damage"), 2, E);
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Bridge, TEXT("Passable"), 0, E);
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Bridge, TEXT("Blocked"), 1, E);
	}
	if (River >= S.BridgeDeckFloodRiverM && FGenesisWorldStateLib::GetObjectValue(Bundle, S.Bridge, TEXT("Flooded")) == 0)
	{
		const FName E = Record(Spec(TEXT("STORM_DAMAGE"), Weather, { S.Bridge }, Causes(WeatherCause), TEXT("R04")));
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Bridge, TEXT("Flooded"), 1, E);
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Bridge, TEXT("Passable"), 0, E);
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Bridge, TEXT("Blocked"), 1, E);
	}
	if (Wind >= S.WorkshopDamageWindMs
		&& FGenesisWorldStateLib::GetObjectValue(Bundle, S.Workshop, TEXT("Secured")) == 0
		&& FGenesisWorldStateLib::GetObjectValue(Bundle, S.Workshop, TEXT("StockDamaged")) == 0)
	{
		const FName E = Record(Spec(TEXT("STORM_DAMAGE"), Weather, { S.Workshop }, Causes(WeatherCause), TEXT("R03")));
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Workshop, TEXT("StockDamaged"), 1, E);
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Workshop, TEXT("AcceptsOrders"), 0, E);
	}

	Bundle.World.EventFlags.Add(RiverCmKey, FMath::RoundToInt(FGenesisWeather::SampleRaw(Timeline, To, W).RiverM * 100.f));
}

void FGenesisFlussdorfRules::EvaluateCoordinator(FGenesisSaveBundle& Bundle, const FGenesisStormTimeline& Timeline, FRecord Record, TArray<FName>& OutTriggers)
{
	using namespace GenesisFlussdorf;
	const UGenesisFlussdorfSettings& S = *GetDefault<UGenesisFlussdorfSettings>();
	const FName N05 = S.CommunityCoordinator;
	const EGenesisWeatherPhase Phase = GetProcessedPhase(Bundle);

	// Oeffentliche Warnung nur von der berechtigten Stelle und nur mit gemessenem Ausloeser (EV24_05).
	const bool bKnowsAlert = Knows(Bundle, N05, TEXT("ALERT_RELAYED")) || Knows(Bundle, N05, TEXT("ALERT_REPORTED"));
	if (bKnowsAlert && Phase < EGenesisWeatherPhase::Over && Bundle.World.EventFlags.FindRef(PublicWarningKey) == 0)
	{
		const FName Source = FindLatestEvent(Bundle, TEXT("ALERT_REPORTED")).IsNone() ? FindLatestEvent(Bundle, TEXT("ALERT_RELAYED")) : FindLatestEvent(Bundle, TEXT("ALERT_REPORTED"));
		const FName E = Record(Spec(TEXT("PUBLIC_WARNING"), N05, {}, Causes(FindLatestEvent(Bundle, TEXT("WEATHER_ALERT")), Source), TEXT("R01")));
		Bundle.World.EventFlags.Add(PublicWarningKey, 1);
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Notice, TEXT("Warning"), 1, E);
		OutTriggers.Add(TEXT("WX_PUBLIC_WARNING"));
	}
	if (Phase >= EGenesisWeatherPhase::Over && FGenesisWorldStateLib::GetObjectValue(Bundle, S.Notice, TEXT("Warning")) == 1)
	{
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Notice, TEXT("Warning"), 0, FindLatestEvent(Bundle, TEXT("STORM_RECEDED")));
	}

	// Risikomeldung zur Bruecke: Pruefauftrag (es gibt noch keine Pruefperson), bei Gefahrenlage Sperrung (EV24_03/06).
	const FName Report = FindLatestEvent(Bundle, TEXT("BRIDGE_DAMAGE_REPORTED"));
	if (!Knows(Bundle, N05, TEXT("BRIDGE_DAMAGE_REPORTED")))
	{
		return;
	}
	if (FGenesisWorldStateLib::GetObjectValue(Bundle, S.Bridge, TEXT("InspectionRequested")) == 0)
	{
		const FName E = Record(Spec(TEXT("INSPECTION_REQUESTED"), N05, { S.Bridge }, Causes(Report), TEXT("R01")));
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Bridge, TEXT("InspectionRequested"), 1, E);
	}
	const bool bDanger = (bKnowsAlert && Phase >= EGenesisWeatherPhase::Alert && Phase < EGenesisWeatherPhase::Over)
		|| FGenesisWorldStateLib::GetObjectValue(Bundle, S.Bridge, TEXT("Damage")) >= 2;
	if (bDanger && FGenesisWorldStateLib::GetObjectValue(Bundle, S.Bridge, TEXT("Closed")) == 0)
	{
		const FName E = Record(Spec(TEXT("BRIDGE_CLOSED"), N05, { S.Bridge }, Causes(Report, FindLatestEvent(Bundle, TEXT("PUBLIC_WARNING"))), TEXT("R04")));
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Bridge, TEXT("Closed"), 1, E);
		FGenesisWorldStateLib::SetObjectValue(Bundle, S.Bridge, TEXT("Blocked"), 1, E);
	}
}

FName FGenesisFlussdorfRules::ReactionFor(const FGenesisSaveBundle& Bundle, FName NpcId, FName Scheduled, EGenesisWeatherPhase Phase)
{
	using namespace GenesisFlussdorf;
	const UGenesisFlussdorfSettings& S = *GetDefault<UGenesisFlussdorfSettings>();
	const bool bDuringStorm = Phase == EGenesisWeatherPhase::Storm || Phase == EGenesisWeatherPhase::Receding;
	const bool bWarned = KnowsWarning(Bundle, NpcId) && Phase >= EGenesisWeatherPhase::Alert && Phase < EGenesisWeatherPhase::Over;

	// Im Sturm selbst sucht jede Figur Schutz - das nimmt sie auch ohne Warnung wahr.
	if (bDuringStorm)
	{
		return Scheduled == Sleep ? Sleep : Home;
	}
	if (NpcId == S.WorkshopOwner && bWarned)
	{
		// N01: Werkstatt sichern und Schutz suchen.
		const bool bOpenWork = FGenesisWorldStateLib::GetObjectValue(Bundle, S.Workshop, TEXT("Secured")) == 0
			&& FGenesisWorldStateLib::GetObjectValue(Bundle, S.Workshop, TEXT("StockDamaged")) == 0;
		return bOpenWork ? Secure : Home;
	}
	if (NpcId == S.DeliveryDriver)
	{
		// N04: Transport aussetzen bei Warnung; nicht ueber eine Bruecke mit gemeldetem Riss ohne Pruefung.
		if (bWarned)
		{
			return Home;
		}
		if (Scheduled == Deliver && Knows(Bundle, NpcId, TEXT("BRIDGE_RISK_TOLD"))
			&& FGenesisWorldStateLib::GetObjectValue(Bundle, S.Bridge, TEXT("Inspected")) == 0)
		{
			return Home;
		}
	}
	return NAME_None;
}

// ---------------------------------------------------------------- Subsystem

bool UGenesisFlussdorfSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
	const UWorld* World = Cast<UWorld>(Outer);
	return World && (World->WorldType == EWorldType::Game || World->WorldType == EWorldType::PIE);
}

TStatId UGenesisFlussdorfSubsystem::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(UGenesisFlussdorfSubsystem, STATGROUP_Tickables);
}

bool UGenesisFlussdorfSubsystem::IsActive() const
{
	const UWorld* World = GetWorld();
	if (!World)
	{
		return false;
	}
	const FString Map = UWorld::RemovePIEPrefix(FPackageName::GetShortName(World->GetOutermost()->GetName()));
	return GetDefault<UGenesisFlussdorfSettings>()->ActiveMaps.Contains(Map);
}

FGenesisSaveBundle* UGenesisFlussdorfSubsystem::GetBundle() const
{
	UGameInstance* GI = GetWorld() ? GetWorld()->GetGameInstance() : nullptr;
	UGenesisSaveSubsystem* Save = GI ? GI->GetSubsystem<UGenesisSaveSubsystem>() : nullptr;
	return Save && Save->HasActiveSoul() ? &Save->GetMutable() : nullptr;
}

void UGenesisFlussdorfSubsystem::EnsureTimeline(const FGenesisSaveBundle& Bundle)
{
	if (bTimelineBuilt && TimelineSeed == Bundle.World.WorldSeed)
	{
		return;
	}
	const UGenesisWeatherSettings& W = *GetDefault<UGenesisWeatherSettings>();
	const FName StormId = GetDefault<UGenesisFlussdorfSettings>()->StormId;
	const FGenesisStormScenario* Scenario = W.Storms.FindByPredicate([StormId](const FGenesisStormScenario& S) { return S.StormId == StormId; });
	Timeline = FGenesisWeather::BuildTimeline(Scenario ? *Scenario : FGenesisStormScenario(), Bundle.World.WorldSeed, W);
	bTimelineBuilt = true;
	TimelineSeed = Bundle.World.WorldSeed;
	UE_LOG(LogGenesis, Display, TEXT("Flussdorf: Sturm %s Wind %.1f m/s Pegel +%.2f m, Vorzeichen %s, Alarm %s, Sturm %s, vorbei %s"),
		*Timeline.StormId.ToString(), Timeline.PeakWindMs, Timeline.RiverRiseM,
		*Timeline.PhaseStart[1].ToString(TEXT("%d.%m. %H:%M")), *Timeline.PhaseStart[2].ToString(TEXT("%d.%m. %H:%M")),
		*Timeline.PhaseStart[3].ToString(TEXT("%d.%m. %H:%M")), *Timeline.PhaseStart[5].ToString(TEXT("%d.%m. %H:%M")));
}

FGenesisWeatherReading UGenesisFlussdorfSubsystem::GetReading() const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	return Bundle && bTimelineBuilt ? FGenesisWeather::Sample(Timeline, Bundle->World.WorldDateTime, *GetDefault<UGenesisWeatherSettings>()) : FGenesisWeatherReading();
}

void UGenesisFlussdorfSubsystem::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	UWorld* World = GetWorld();
	FGenesisSaveBundle* Bundle = GetBundle();
	if (!World || !World->HasBegunPlay() || !Bundle || !IsActive())
	{
		return;
	}
	EnsureTimeline(*Bundle);

	const FDateTime Now = Bundle->World.WorldDateTime;
	if (!bHasLastTime || Now < LastTime)
	{
		// Spielbeginn oder geladener Stand: ab jetzt fortschreiben (der Stand enthaelt alles Fruehere).
		LastTime = Now;
		bHasLastTime = true;
	}
	const double GameMinutes = (Now - LastTime).GetTotalMinutes();

	UGenesisCausalitySubsystem* Causality = World->GetGameInstance()->GetSubsystem<UGenesisCausalitySubsystem>();
	auto Record = [Causality](const FGenesisEventSpec& Spec) { return Causality->RecordEvent(Spec); };

	TArray<FName> Triggers;
	FGenesisFlussdorfRules::AdvanceWeather(*Bundle, Timeline, LastTime, Now, Record, Triggers);
	FGenesisFlussdorfRules::EvaluateCoordinator(*Bundle, Timeline, Record, Triggers);
	const EGenesisWeatherPhase Phase = FGenesisFlussdorfRules::GetProcessedPhase(*Bundle);
	RouteCheckTimer -= DeltaTime;
	UpdateNpcs(*Bundle, Phase, GameMinutes, Triggers.Contains(FName(TEXT("WX_STORM"))));
	LastTime = Now;

	if (UGenesisStorySubsystem* Story = World->GetGameInstance()->GetSubsystem<UGenesisStorySubsystem>())
	{
		for (const FName Trigger : Triggers)
		{
			UE_LOG(LogGenesis, Display, TEXT("Flussdorf %s: %s"), *Now.ToString(TEXT("%d.%m. %H:%M")), *Trigger.ToString());
			Story->FireWorldTrigger(Trigger);
		}
	}
}

bool UGenesisFlussdorfSubsystem::HasDeliveryRoute(const AGenesisNpcCharacter* Npc) const
{
	UWorld* World = GetWorld();
	UNavigationSystemV1* Nav = FNavigationSystem::GetCurrent<UNavigationSystemV1>(World);
	if (!Nav || !Npc)
	{
		return true;
	}
	for (TActorIterator<AGenesisActivitySpot> It(World); It; ++It)
	{
		if (It->ActorHasTag(GenesisFlussdorf::Deliver))
		{
			const UNavigationPath* Path = UNavigationSystemV1::FindPathToLocationSynchronously(World, Npc->GetActorLocation(), It->GetActorLocation(), const_cast<AGenesisNpcCharacter*>(Npc));
			return Path && Path->IsValid() && !Path->IsPartial();
		}
	}
	return true;
}

void UGenesisFlussdorfSubsystem::UpdateNpcs(FGenesisSaveBundle& Bundle, EGenesisWeatherPhase Phase, double GameMinutes, bool bStormStarted)
{
	using namespace GenesisFlussdorf;
	UWorld* World = GetWorld();
	const UGenesisFlussdorfSettings& S = *GetDefault<UGenesisFlussdorfSettings>();
	UGenesisCausalitySubsystem* Causality = World->GetGameInstance()->GetSubsystem<UGenesisCausalitySubsystem>();
	const APawn* Player = World->GetFirstPlayerController() ? World->GetFirstPlayerController()->GetPawn() : nullptr;

	const AGenesisWorldObject* NoticeBoard = nullptr;
	for (TActorIterator<AGenesisWorldObject> It(World); It; ++It)
	{
		if (It->ObjectId == S.Notice && It->bInteractable)
		{
			NoticeBoard = *It;
			break;
		}
	}
	const FName Warning = FGenesisFlussdorfRules::FindLatestEvent(Bundle, TEXT("PUBLIC_WARNING"));

	for (TActorIterator<AGenesisNpcCharacter> It(World); It; ++It)
	{
		AGenesisNpcCharacter* Npc = *It;
		const FName Id = Npc->GetNpcId();

		// Aushang lesen: Wissen nur, wer tatsaechlich dort war (S24-06).
		if (!Warning.IsNone() && NoticeBoard && FGenesisWorldStateLib::GetObjectValue(Bundle, S.Notice, TEXT("Warning")) == 1
			&& FVector::Dist2D(Npc->GetActorLocation(), NoticeBoard->GetActorLocation()) < S.NoticeReadRangeCm
			&& !FGenesisFlussdorfRules::KnowsWarning(Bundle, Id))
		{
			Causality->RecordEvent(Spec(TEXT("WARNING_RECEIVED"), S.CommunityCoordinator, { Id }, Causes(Warning), TEXT("R01")));
		}

		// Sturmbeginn: wer nicht im Schutz ist, ist dem Wetter ausgesetzt.
		if (bStormStarted)
		{
			const bool bSheltered = Npc->bAtActivitySpot && (Npc->CurrentActivity == Home || Npc->CurrentActivity == Sleep);
			if (!bSheltered)
			{
				Causality->RecordEvent(Spec(TEXT("STORM_EXPOSED"), Weather, { Id }, Causes(FGenesisFlussdorfRules::FindLatestEvent(Bundle, TEXT("STORM"))), NAME_None));
			}
		}

		// N01 sichert die Werkstatt; mit Hilfe vor Ort doppelt so schnell.
		if (Id == S.WorkshopOwner && Npc->CurrentActivity == Secure && Npc->bAtActivitySpot
			&& FGenesisWorldStateLib::GetObjectValue(Bundle, S.Workshop, TEXT("Secured")) == 0)
		{
			const bool bHelped = FGenesisWorldStateLib::GetObjectValue(Bundle, S.Workshop, TEXT("Helped")) == 1
				&& Player && FVector::Dist(Player->GetActorLocation(), Npc->GetActorLocation()) < S.HelpRangeCm;
			SecureCarryMinutes += GameMinutes * (bHelped ? 2.0 : 1.0);
			const int32 Progress = FGenesisWorldStateLib::GetObjectValue(Bundle, S.Workshop, TEXT("SecureProgress")) + int32(SecureCarryMinutes);
			SecureCarryMinutes -= FMath::FloorToDouble(SecureCarryMinutes);
			FGenesisWorldStateLib::SetObjectValue(Bundle, S.Workshop, TEXT("SecureProgress"), Progress, NAME_None);
			if (Progress >= int32(S.SecureMinutes))
			{
				const FName E = Causality->RecordEvent(Spec(TEXT("WORKSHOP_SECURED"), Id, { S.Workshop },
					Causes(FGenesisFlussdorfRules::FindLatestEvent(Bundle, TEXT("WARNING_RECEIVED"))), TEXT("R03")));
				FGenesisWorldStateLib::SetObjectValue(Bundle, S.Workshop, TEXT("Secured"), 1, E);
			}
		}

		// Reaktion auf die Lage statt Tagesplan.
		const FName Scheduled = GetDefault<UGenesisNpcSettings>()->GetActivity(Id, float(Bundle.World.WorldDateTime.GetTimeOfDay().GetTotalHours()));
		FName Reaction = FGenesisFlussdorfRules::ReactionFor(Bundle, Id, Scheduled, Phase);
		if (Id == S.DeliveryDriver && Scheduled == Deliver)
		{
			if (Reaction.IsNone())
			{
				// Kein Teleport: Lieferung nur, wenn es einen begehbaren Weg gibt (Bruecke oder Umweg R05).
				if (RouteCheckTimer <= 0.f)
				{
					RouteCheckTimer = 1.f;
					bLastRouteOk = HasDeliveryRoute(Npc);
				}
				if (!bLastRouteOk)
				{
					Reaction = Home;
				}
				else if (FGenesisFlussdorfRules::IsBridgeBlocked(Bundle) && Bundle.World.EventFlags.FindRef(TEXT("N04.ReroutedDay")) != DayStamp(Bundle.World.WorldDateTime))
				{
					Bundle.World.EventFlags.Add(TEXT("N04.ReroutedDay"), DayStamp(Bundle.World.WorldDateTime));
					Causality->RecordEvent(Spec(TEXT("DELIVERY_REROUTED"), Id, {}, Causes(FGenesisFlussdorfRules::FindLatestEvent(Bundle, TEXT("BRIDGE_CLOSED"))), TEXT("R05")));
				}
			}
			if (Reaction == Home && Bundle.World.EventFlags.FindRef(TEXT("N04.PostponedDay")) != DayStamp(Bundle.World.WorldDateTime))
			{
				Bundle.World.EventFlags.Add(TEXT("N04.PostponedDay"), DayStamp(Bundle.World.WorldDateTime));
				Causality->RecordEvent(Spec(TEXT("DELIVERY_POSTPONED"), Id, {}, {}, TEXT("R08")));
			}
		}
		Npc->ReactionActivity = Reaction;
	}
}

// ---------------------------------------------------------------- Texte (Arbeitstext, kein Kanon-Wortlaut)

void UGenesisFlussdorfSubsystem::AppendTextArgs(const UWorld* World, FFormatNamedArguments& Args)
{
	const UGenesisFlussdorfSubsystem* Self = World ? World->GetSubsystem<UGenesisFlussdorfSubsystem>() : nullptr;
	const FGenesisSaveBundle* Bundle = Self ? Self->GetBundle() : nullptr;
	if (!Self || !Bundle || !Self->IsActive() || !Self->bTimelineBuilt)
	{
		return;
	}
	const UGenesisFlussdorfSettings& S = *GetDefault<UGenesisFlussdorfSettings>();
	const FGenesisWeatherReading R = Self->GetReading();
	const FGenesisSaveBundle& B = *Bundle;
	auto Value = [&B](FName Object, const TCHAR* Key) { return FGenesisWorldStateLib::GetObjectValue(B, Object, Key); };

	FNumberFormattingOptions One;
	One.SetMinimumFractionalDigits(1).SetMaximumFractionalDigits(1);
	FNumberFormattingOptions Zero;
	Zero.SetMaximumFractionalDigits(0);
	FNumberFormattingOptions Signed = One;
	Signed.SetAlwaysSign(true);

	Args.Add(TEXT("Pressure"), FText::AsNumber(R.PressureHPa, &One));
	Args.Add(TEXT("Tendency"), FText::AsNumber(R.PressureTendency3h, &Signed));
	Args.Add(TEXT("Wind"), FText::AsNumber(R.WindMs, &Zero));
	Args.Add(TEXT("Rain"), FText::AsNumber(R.RainMmH, &Zero));
	Args.Add(TEXT("River"), FText::AsNumber(R.RiverM, &Signed));

	const bool bAlert = Value(S.Station, TEXT("Alert")) == 1;
	Args.Add(TEXT("StationStatus"), bAlert
		? LOCTEXT("StationAlert", "ALARM: Druckfall über der Warnschwelle – Unwetter wahrscheinlich.")
		: (R.Phase >= EGenesisWeatherPhase::Over ? LOCTEXT("StationOver", "Kein Alarm mehr. Werte fallen zurück.") : LOCTEXT("StationCalm", "Kein Alarm.")));

	Args.Add(TEXT("NoticeText"), Value(S.Notice, TEXT("Warning")) == 1
		? LOCTEXT("NoticeWarning", "UNWETTERWARNUNG der Gemeinde: Sturm und Hochwasser erwartet. Uferweg und Brücke meiden, Schutz suchen.")
		: LOCTEXT("NoticeNormal", "Aushänge: Markttage, Sprechzeiten der Gemeinde."));

	FText Bridge;
	if (Value(S.Bridge, TEXT("Damage")) >= 2)
	{
		Bridge = LOCTEXT("BridgeDamaged", "Die Brücke hat in der Nacht Schaden genommen und ist nicht passierbar.");
	}
	else if (Value(S.Bridge, TEXT("Flooded")) == 1)
	{
		Bridge = LOCTEXT("BridgeFlooded", "Der Belag der Brücke stand unter Wasser. Sie bleibt zu, bis sie geprüft ist.");
	}
	else if (Value(S.Bridge, TEXT("Closed")) == 1)
	{
		Bridge = LOCTEXT("BridgeClosed", "Die Brücke ist gesperrt, bis eine Fachperson sie prüft.");
	}
	else
	{
		Bridge = LOCTEXT("BridgeOpen", "Die Brücke ist offen.");
	}
	Args.Add(TEXT("BridgeStatus"), Bridge);

	Args.Add(TEXT("TrailStatus"), Value(S.Trail, TEXT("Open")) == 0
		? LOCTEXT("TrailClosed", "Der Uferweg ist nach dem Hochwasser gesperrt.")
		: LOCTEXT("TrailOpen", "Der Uferweg ist begehbar."));

	FText Workshop;
	if (Value(S.Workshop, TEXT("StockDamaged")) == 1)
	{
		Workshop = LOCTEXT("WorkshopDamaged", "Der Sturm hat das Lager erwischt. Ohne Material nehme ich vorerst keine Aufträge an.");
	}
	else if (Value(S.Workshop, TEXT("Secured")) == 1)
	{
		Workshop = LOCTEXT("WorkshopSecured", "Wir hatten rechtzeitig gesichert. Im Lager ist nichts passiert.");
	}
	else
	{
		Workshop = LOCTEXT("WorkshopFine", "In der Werkstatt ist alles in Ordnung.");
	}
	Args.Add(TEXT("WorkshopStatus"), Workshop);

	FText Delivery;
	if (FGenesisFlussdorfRules::IsBridgeBlocked(B))
	{
		Delivery = Value(S.Trail, TEXT("Open")) == 1
			? LOCTEXT("DeliveryDetour", "Über die Brücke geht es nicht. Ich nehme den Umweg über den Uferweg.")
			: LOCTEXT("DeliveryNone", "Über den Fluss komme ich gerade nicht. Die Lieferungen müssen warten.");
	}
	else
	{
		Delivery = LOCTEXT("DeliveryOpen", "Die Strecke ist frei.");
	}
	Args.Add(TEXT("DeliveryStatus"), Delivery);
}

#undef LOCTEXT_NAMESPACE
