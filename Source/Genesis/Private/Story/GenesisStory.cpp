#include "Story/GenesisStory.h"

#include "Causality/GenesisCausality.h"
#include "Character/GenesisCharacterRegistry.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Genesis.h"
#include "Save/GenesisSaveSubsystem.h"
#include "World/GenesisFlussdorf.h"
#include "World/GenesisWorld.h"

// ---------------------------------------------------------------- Definitionen

const FGenesisDialogNode* UGenesisDialogDefinition::FindNode(FName NodeId) const
{
	return Nodes.FindByPredicate([NodeId](const FGenesisDialogNode& N) { return N.NodeId == NodeId; });
}

const FGenesisQuestStep* UGenesisQuestDefinition::FindStep(FName StepId) const
{
	return Steps.FindByPredicate([StepId](const FGenesisQuestStep& S) { return S.StepId == StepId; });
}

TArray<FGenesisStepContact> FGenesisQuestStep::GetAllContacts() const
{
	TArray<FGenesisStepContact> Result;
	if (!TalkToNpcId.IsNone())
	{
		FGenesisStepContact& Main = Result.AddDefaulted_GetRef();
		Main.TargetId = TalkToNpcId;
		Main.Dialog = Dialog;
	}
	Result.Append(Contacts);
	return Result;
}

UGenesisQuestDefinition* UGenesisStorySettings::LoadQuest(FName QuestId) const
{
	for (const TSoftObjectPtr<UGenesisQuestDefinition>& Ref : Quests)
	{
		UGenesisQuestDefinition* Quest = Ref.LoadSynchronous();
		if (Quest && Quest->QuestId == QuestId)
		{
			return Quest;
		}
	}
	return nullptr;
}

// ---------------------------------------------------------------- Questgraph

FGenesisQuestState* FGenesisStory::FindQuestState(FGenesisSaveBundle& Bundle, FName QuestId)
{
	return Bundle.Life.Quests.FindByPredicate([QuestId](const FGenesisQuestState& Q) { return Q.QuestId == QuestId; });
}

const FGenesisQuestState* FGenesisStory::FindQuestState(const FGenesisSaveBundle& Bundle, FName QuestId)
{
	return Bundle.Life.Quests.FindByPredicate([QuestId](const FGenesisQuestState& Q) { return Q.QuestId == QuestId; });
}

bool FGenesisStory::StartQuest(FGenesisSaveBundle& Bundle, const UGenesisQuestDefinition& Quest)
{
	if (FindQuestState(Bundle, Quest.QuestId) || !Quest.FindStep(Quest.StartStepId))
	{
		return false;
	}
	FGenesisQuestState& State = Bundle.Life.Quests.AddDefaulted_GetRef();
	State.QuestId = Quest.QuestId;
	State.CurrentStepId = Quest.StartStepId;
	State.History.Add(Quest.StartStepId);
	return true;
}

const FGenesisQuestStep* FGenesisStory::GetCurrentStep(const FGenesisSaveBundle& Bundle, const UGenesisQuestDefinition& Quest)
{
	const FGenesisQuestState* State = FindQuestState(Bundle, Quest.QuestId);
	return State && !State->bCompleted ? Quest.FindStep(State->CurrentStepId) : nullptr;
}

bool FGenesisStory::ConditionsMet(const FGenesisSaveBundle& Bundle, const TArray<FGenesisStateCondition>& Conditions)
{
	for (const FGenesisStateCondition& Condition : Conditions)
	{
		const int32 Value = FGenesisWorldStateLib::GetValue(Bundle, Condition.Key);
		if (Value < Condition.Min || Value > Condition.Max)
		{
			return false;
		}
	}
	return true;
}

bool FGenesisStory::FireTrigger(FGenesisSaveBundle& Bundle, const UGenesisQuestDefinition& Quest, FName Trigger)
{
	FGenesisQuestState* State = FindQuestState(Bundle, Quest.QuestId);
	const FGenesisQuestStep* Step = GetCurrentStep(Bundle, Quest);
	if (!State || !Step || Trigger.IsNone())
	{
		return false;
	}
	for (const FGenesisQuestEdge& Edge : Step->Edges)
	{
		if (Edge.Trigger != Trigger)
		{
			continue;
		}
		if (!Edge.RequiredFlag.IsNone() && Bundle.World.EventFlags.FindRef(Edge.RequiredFlag) != Edge.RequiredFlagValue)
		{
			continue;
		}
		if (!ConditionsMet(Bundle, Edge.Conditions))
		{
			continue;
		}
		State->History.Add(Trigger);
		if (!Edge.NextStepId.IsNone())
		{
			State->CurrentStepId = Edge.NextStepId;
			State->History.Add(Edge.NextStepId);
		}
		else
		{
			State->bCompleted = true;
			State->OutcomeId = Edge.OutcomeId;
			State->History.Add(Edge.OutcomeId);
		}
		return true;
	}
	return false;
}

// ---------------------------------------------------------------- Dialog

TArray<const FGenesisDialogChoice*> FGenesisStory::GetAvailableChoices(const FGenesisSaveBundle& Bundle, const FGenesisDialogNode& Node, FName SpeakerId)
{
	const float Trust = FGenesisCausality::GetAttitude(Bundle, SpeakerId, FGenesisCausality::PlayerSubjectId(Bundle.Life.LifeIndex)).Trust;
	TArray<const FGenesisDialogChoice*> Result;
	for (const FGenesisDialogChoice& Choice : Node.Choices)
	{
		if ((Choice.RequiredTrust < -1.f || Trust >= Choice.RequiredTrust) && ConditionsMet(Bundle, Choice.Conditions))
		{
			Result.Add(&Choice);
		}
	}
	return Result;
}

FName FGenesisStory::ApplyChoice(FGenesisSaveBundle& Bundle, const FGenesisDialogChoice& Choice, FName SpeakerId,
	TFunctionRef<FName(const FGenesisEventSpec&)> RecordEvent, FName& OutQuestTrigger)
{
	for (const FGenesisConsequence& Consequence : Choice.Consequences)
	{
		FName EventId;
		if (!Consequence.EventType.IsNone())
		{
			FGenesisEventSpec Spec;
			Spec.EventType = Consequence.EventType;
			Spec.ActorId = FGenesisCausality::PlayerSubjectId(Bundle.Life.LifeIndex);
			if (Consequence.bTargetSpeaker)
			{
				Spec.TargetIds.Add(SpeakerId);
			}
			Spec.TargetIds.Append(Consequence.ExtraTargets);
			EventId = RecordEvent(Spec);
		}
		if (!Consequence.FlagName.IsNone())
		{
			// Weltobjekte merken sich das verursachende Ereignis (Datenvertrag).
			FGenesisWorldStateLib::SetValue(Bundle, Consequence.FlagName, Consequence.FlagValue, EventId);
		}
	}
	OutQuestTrigger = Choice.QuestTrigger;
	return Choice.NextNodeId;
}

// ---------------------------------------------------------------- Pruefung

TArray<FString> FGenesisStory::ValidateDialog(const UGenesisDialogDefinition& Dialog, TSet<FName>* OutTriggers)
{
	TArray<FString> Errors;
	const FString Name = Dialog.DialogId.ToString();
	const UGenesisCausalitySettings& Causality = *GetDefault<UGenesisCausalitySettings>();

	TSet<FName> NodeIds;
	for (const FGenesisDialogNode& Node : Dialog.Nodes)
	{
		if (NodeIds.Contains(Node.NodeId))
		{
			Errors.Add(FString::Printf(TEXT("%s: Knoten %s doppelt"), *Name, *Node.NodeId.ToString()));
		}
		NodeIds.Add(Node.NodeId);
	}
	if (!Dialog.FindNode(Dialog.StartNodeId))
	{
		Errors.Add(FString::Printf(TEXT("%s: Startknoten %s fehlt"), *Name, *Dialog.StartNodeId.ToString()));
		return Errors;
	}

	for (const FGenesisDialogNode& Node : Dialog.Nodes)
	{
		if (Node.Choices.Num() == 0)
		{
			Errors.Add(FString::Printf(TEXT("%s/%s: keine Antwort - das Gespraech kaeme nicht weiter"), *Name, *Node.NodeId.ToString()));
		}
		if (!Node.Choices.ContainsByPredicate([](const FGenesisDialogChoice& C) { return C.IsUnconditional(); }))
		{
			Errors.Add(FString::Printf(TEXT("%s/%s: alle Antworten haben Bedingungen - Sackgasse moeglich"), *Name, *Node.NodeId.ToString()));
		}
		for (const FGenesisDialogChoice& Choice : Node.Choices)
		{
			if (!Choice.NextNodeId.IsNone() && !NodeIds.Contains(Choice.NextNodeId))
			{
				Errors.Add(FString::Printf(TEXT("%s/%s/%s: Folgeknoten %s fehlt"), *Name, *Node.NodeId.ToString(), *Choice.ChoiceId.ToString(), *Choice.NextNodeId.ToString()));
			}
			for (const FGenesisConsequence& Consequence : Choice.Consequences)
			{
				if (!Consequence.EventType.IsNone() && !Causality.FindType(Consequence.EventType))
				{
					Errors.Add(FString::Printf(TEXT("%s/%s: unbekannter Ereignistyp %s"), *Name, *Choice.ChoiceId.ToString(), *Consequence.EventType.ToString()));
				}
			}
			if (OutTriggers && !Choice.QuestTrigger.IsNone())
			{
				OutTriggers->Add(Choice.QuestTrigger);
			}
		}
	}

	// Erreichbarkeit und Ausgang: jeder Knoten erreichbar, von jedem ein Gespraechsende erreichbar.
	TSet<FName> Reachable;
	TArray<FName> Queue = { Dialog.StartNodeId };
	while (Queue.Num() > 0)
	{
		const FName Id = Queue.Pop();
		if (Reachable.Contains(Id)) { continue; }
		Reachable.Add(Id);
		if (const FGenesisDialogNode* Node = Dialog.FindNode(Id))
		{
			for (const FGenesisDialogChoice& Choice : Node->Choices)
			{
				if (!Choice.NextNodeId.IsNone()) { Queue.Add(Choice.NextNodeId); }
			}
		}
	}
	TSet<FName> CanEnd;
	bool bChanged = true;
	while (bChanged)
	{
		bChanged = false;
		for (const FGenesisDialogNode& Node : Dialog.Nodes)
		{
			if (CanEnd.Contains(Node.NodeId)) { continue; }
			const bool bEnds = Node.Choices.ContainsByPredicate([&CanEnd](const FGenesisDialogChoice& C) { return C.NextNodeId.IsNone() || CanEnd.Contains(C.NextNodeId); });
			if (bEnds) { CanEnd.Add(Node.NodeId); bChanged = true; }
		}
	}
	for (const FGenesisDialogNode& Node : Dialog.Nodes)
	{
		if (!Reachable.Contains(Node.NodeId))
		{
			Errors.Add(FString::Printf(TEXT("%s/%s: nie erreichbar"), *Name, *Node.NodeId.ToString()));
		}
		else if (!CanEnd.Contains(Node.NodeId))
		{
			Errors.Add(FString::Printf(TEXT("%s/%s: Schleife ohne Ausgang"), *Name, *Node.NodeId.ToString()));
		}
	}
	return Errors;
}

TArray<FString> FGenesisStory::ValidateQuest(const UGenesisQuestDefinition& Quest)
{
	TArray<FString> Errors;
	const FString Name = Quest.QuestId.ToString();
	TSet<FName> StepIds;
	for (const FGenesisQuestStep& Step : Quest.Steps)
	{
		if (StepIds.Contains(Step.StepId))
		{
			Errors.Add(FString::Printf(TEXT("%s: Schritt %s doppelt"), *Name, *Step.StepId.ToString()));
		}
		StepIds.Add(Step.StepId);
	}
	if (!Quest.FindStep(Quest.StartStepId))
	{
		Errors.Add(FString::Printf(TEXT("%s: Startschritt %s fehlt"), *Name, *Quest.StartStepId.ToString()));
		return Errors;
	}

	const TArray<FGenesisCharacterRegistryEntry>& Characters = GetDefault<UGenesisCharacterRegistry>()->Entries;
	const TArray<FName>& WorldTriggers = GetDefault<UGenesisWorldSettings>()->WorldTriggers;
	if (!Quest.StartTrigger.IsNone() && !WorldTriggers.Contains(Quest.StartTrigger))
	{
		Errors.Add(FString::Printf(TEXT("%s: Start-Ausloeser %s ist kein bekannter Welt-Ausloeser"), *Name, *Quest.StartTrigger.ToString()));
	}
	for (const FGenesisQuestStep& Step : Quest.Steps)
	{
		const FString StepName = FString::Printf(TEXT("%s/%s"), *Name, *Step.StepId.ToString());
		if (Step.Edges.Num() == 0)
		{
			Errors.Add(StepName + TEXT(": kein Weg weiter - Sackgasse"));
		}
		else if (!Step.Edges.ContainsByPredicate([](const FGenesisQuestEdge& E) { return E.IsUnconditional(); }))
		{
			Errors.Add(StepName + TEXT(": alle Wege weiter haben Bedingungen - Sackgasse moeglich"));
		}

		// Ansprechpartner: Figuren aus der Registry oder Weltobjekte; jedes Gespraech einzeln geprueft.
		TSet<FName> Produced;
		const TArray<FGenesisStepContact> Contacts = Step.GetAllContacts();
		for (const FGenesisStepContact& Contact : Contacts)
		{
			const bool bKnown = FGenesisWorldStateLib::IsWorldObjectId(Contact.TargetId)
				|| Characters.ContainsByPredicate([&Contact](const FGenesisCharacterRegistryEntry& E) { return E.CharacterAssetId == Contact.TargetId; });
			if (!bKnown)
			{
				Errors.Add(FString::Printf(TEXT("%s: Figur %s ist nicht in der Registry"), *StepName, *Contact.TargetId.ToString()));
			}
			if (const UGenesisDialogDefinition* Dialog = Contact.Dialog.LoadSynchronous())
			{
				for (const FString& Error : ValidateDialog(*Dialog, &Produced))
				{
					Errors.Add(StepName + TEXT(": ") + Error);
				}
			}
			else
			{
				Errors.Add(FString::Printf(TEXT("%s: Gespraech fuer %s fehlt"), *StepName, *Contact.TargetId.ToString()));
			}
		}

		TSet<FName> Consumed;
		for (const FGenesisQuestEdge& Edge : Step.Edges)
		{
			Consumed.Add(Edge.Trigger);
			if (Edge.NextStepId.IsNone() && Edge.OutcomeId.IsNone())
			{
				Errors.Add(FString::Printf(TEXT("%s: Kante %s fuehrt nirgendwohin"), *StepName, *Edge.Trigger.ToString()));
			}
			if (!Edge.NextStepId.IsNone() && !StepIds.Contains(Edge.NextStepId))
			{
				Errors.Add(FString::Printf(TEXT("%s: Folgeschritt %s fehlt"), *StepName, *Edge.NextStepId.ToString()));
			}
			if (!Produced.Contains(Edge.Trigger) && !WorldTriggers.Contains(Edge.Trigger))
			{
				Errors.Add(FString::Printf(TEXT("%s: Ausloeser %s wird im Gespraech nie ausgeloest"), *StepName, *Edge.Trigger.ToString()));
			}
		}
		for (const FName Trigger : Produced)
		{
			if (!Consumed.Contains(Trigger))
			{
				Errors.Add(FString::Printf(TEXT("%s: Ausloeser %s bleibt ohne Wirkung"), *StepName, *Trigger.ToString()));
			}
			else if (!Step.Edges.ContainsByPredicate([Trigger](const FGenesisQuestEdge& E) { return E.Trigger == Trigger && E.IsUnconditional(); }))
			{
				Errors.Add(FString::Printf(TEXT("%s: Ausloeser %s wirkt nur unter Bedingung - Sackgasse moeglich"), *StepName, *Trigger.ToString()));
			}
		}
	}

	// Jeder Schritt erreichbar, von jedem Schritt ein Ausgang erreichbar.
	TSet<FName> Reachable;
	TArray<FName> Queue = { Quest.StartStepId };
	while (Queue.Num() > 0)
	{
		const FName Id = Queue.Pop();
		if (Reachable.Contains(Id)) { continue; }
		Reachable.Add(Id);
		if (const FGenesisQuestStep* Step = Quest.FindStep(Id))
		{
			for (const FGenesisQuestEdge& Edge : Step->Edges)
			{
				if (!Edge.NextStepId.IsNone()) { Queue.Add(Edge.NextStepId); }
			}
		}
	}
	TSet<FName> CanFinish;
	bool bChanged = true;
	while (bChanged)
	{
		bChanged = false;
		for (const FGenesisQuestStep& Step : Quest.Steps)
		{
			if (CanFinish.Contains(Step.StepId)) { continue; }
			if (Step.Edges.ContainsByPredicate([&CanFinish](const FGenesisQuestEdge& E) { return (E.NextStepId.IsNone() && !E.OutcomeId.IsNone()) || CanFinish.Contains(E.NextStepId); }))
			{
				CanFinish.Add(Step.StepId);
				bChanged = true;
			}
		}
	}
	for (const FGenesisQuestStep& Step : Quest.Steps)
	{
		if (!Reachable.Contains(Step.StepId))
		{
			Errors.Add(FString::Printf(TEXT("%s/%s: nie erreichbar"), *Name, *Step.StepId.ToString()));
		}
		else if (!CanFinish.Contains(Step.StepId))
		{
			Errors.Add(FString::Printf(TEXT("%s/%s: von hier ist kein Questende erreichbar"), *Name, *Step.StepId.ToString()));
		}
	}
	return Errors;
}

// ---------------------------------------------------------------- Subsystem

FGenesisSaveBundle* UGenesisStorySubsystem::GetBundle() const
{
	UGenesisSaveSubsystem* Save = GetGameInstance()->GetSubsystem<UGenesisSaveSubsystem>();
	return Save ? &Save->GetMutable() : nullptr;
}

bool UGenesisStorySubsystem::StartQuest(FName QuestId)
{
	FGenesisSaveBundle* Bundle = GetBundle();
	const UGenesisQuestDefinition* Quest = GetDefault<UGenesisStorySettings>()->LoadQuest(QuestId);
	return Bundle && Quest && FGenesisStory::StartQuest(*Bundle, *Quest);
}

bool UGenesisStorySubsystem::InteractWith(FName NpcId)
{
	FGenesisSaveBundle* Bundle = GetBundle();
	if (!Bundle || ActiveDialog)
	{
		return false;
	}
	for (const FGenesisQuestState& State : Bundle->Life.Quests)
	{
		if (State.bCompleted)
		{
			continue;
		}
		UGenesisQuestDefinition* Quest = GetDefault<UGenesisStorySettings>()->LoadQuest(State.QuestId);
		const FGenesisQuestStep* Step = Quest ? FGenesisStory::GetCurrentStep(*Bundle, *Quest) : nullptr;
		if (!Step)
		{
			continue;
		}
		for (const FGenesisStepContact& Contact : Step->GetAllContacts())
		{
			UGenesisDialogDefinition* Dialog = Contact.TargetId == NpcId ? Contact.Dialog.LoadSynchronous() : nullptr;
			if (Dialog)
			{
				ActiveDialog = Dialog;
				ActiveDialogQuest = Quest;
				ActiveNodeId = Dialog->StartNodeId;
				ActiveSpeakerId = NpcId;
				return true;
			}
		}
	}
	// Weltobjekte (Aushang, Station, Bruecke) haben ein eigenes Gespraech, auch ohne Quest.
	const FGenesisWorldObjectDef* Object = GetDefault<UGenesisWorldSettings>()->FindObject(NpcId);
	if (UGenesisDialogDefinition* Dialog = Object ? Object->DefaultDialog.LoadSynchronous() : nullptr)
	{
		ActiveDialog = Dialog;
		ActiveDialogQuest = nullptr;
		ActiveNodeId = Dialog->StartNodeId;
		ActiveSpeakerId = NpcId;
		return true;
	}
	return false;
}

void UGenesisStorySubsystem::FireWorldTrigger(FName Trigger)
{
	FGenesisSaveBundle* Bundle = GetBundle();
	if (!Bundle || Trigger.IsNone())
	{
		return;
	}
	for (const TSoftObjectPtr<UGenesisQuestDefinition>& Ref : GetDefault<UGenesisStorySettings>()->Quests)
	{
		const UGenesisQuestDefinition* Quest = Ref.LoadSynchronous();
		if (!Quest)
		{
			continue;
		}
		if (Quest->StartTrigger == Trigger && FGenesisStory::StartQuest(*Bundle, *Quest))
		{
			UE_LOG(LogGenesis, Display, TEXT("Quest %s bietet sich an (%s)."), *Quest->QuestId.ToString(), *Trigger.ToString());
			continue;
		}
		FGenesisStory::FireTrigger(*Bundle, *Quest, Trigger);
	}
}

FName UGenesisStorySubsystem::GetDialogSpeaker() const
{
	const FGenesisDialogNode* Node = ActiveDialog ? ActiveDialog->FindNode(ActiveNodeId) : nullptr;
	return Node && !Node->SpeakerId.IsNone() ? Node->SpeakerId : ActiveSpeakerId;
}

FText UGenesisStorySubsystem::GetDialogSpeakerName() const
{
	const FName Speaker = GetDialogSpeaker();
	if (const FGenesisCharacterRegistryEntry* Entry = UGenesisCharacterRegistry::FindEntry(Speaker))
	{
		if (!Entry->DisplayName.IsEmpty())
		{
			return Entry->DisplayName;
		}
	}
	if (const FGenesisWorldObjectDef* Object = GetDefault<UGenesisWorldSettings>()->FindObject(Speaker))
	{
		if (!Object->DisplayName.IsEmpty())
		{
			return Object->DisplayName;
		}
	}
	return FText::FromName(Speaker);
}

FText UGenesisStorySubsystem::GetDialogText() const
{
	const FGenesisDialogNode* Node = ActiveDialog ? ActiveDialog->FindNode(ActiveNodeId) : nullptr;
	if (!Node)
	{
		return FText::GetEmpty();
	}
	// Platzhalter wie {Wind} oder {BridgeStatus} kommen aus dem aktuellen Weltzustand.
	FFormatNamedArguments Args;
	UGenesisFlussdorfSubsystem::AppendTextArgs(GetGameInstance()->GetWorld(), Args);
	return Args.Num() > 0 ? FText::Format(Node->Text, Args) : Node->Text;
}

TArray<const FGenesisDialogChoice*> UGenesisStorySubsystem::AvailableChoices() const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	const FGenesisDialogNode* Node = ActiveDialog ? ActiveDialog->FindNode(ActiveNodeId) : nullptr;
	return Bundle && Node ? FGenesisStory::GetAvailableChoices(*Bundle, *Node, ActiveSpeakerId) : TArray<const FGenesisDialogChoice*>();
}

TArray<FText> UGenesisStorySubsystem::GetDialogChoiceTexts() const
{
	TArray<FText> Texts;
	for (const FGenesisDialogChoice* Choice : AvailableChoices())
	{
		Texts.Add(Choice->Text);
	}
	return Texts;
}

bool UGenesisStorySubsystem::Choose(int32 Index)
{
	FGenesisSaveBundle* Bundle = GetBundle();
	const TArray<const FGenesisDialogChoice*> Choices = AvailableChoices();
	if (!Bundle || !Choices.IsValidIndex(Index))
	{
		return false;
	}

	UWorld* World = GetGameInstance()->GetWorld();
	APawn* Player = World && World->GetFirstPlayerController() ? World->GetFirstPlayerController()->GetPawn() : nullptr;
	UGenesisCausalitySubsystem* Causality = GetGameInstance()->GetSubsystem<UGenesisCausalitySubsystem>();
	auto Record = [Causality, Player](const FGenesisEventSpec& Spec) -> FName
	{
		// Im Spiel: Zeugen ueber die Wahrnehmung am Ort des Spielers.
		return Player ? Causality->RecordEventAt(Spec, Player->GetActorLocation(), Player) : Causality->RecordEvent(Spec);
	};

	FName Trigger;
	const FName Next = FGenesisStory::ApplyChoice(*Bundle, *Choices[Index], ActiveSpeakerId, Record, Trigger);
	if (!Trigger.IsNone() && ActiveDialogQuest)
	{
		FGenesisStory::FireTrigger(*Bundle, *ActiveDialogQuest, Trigger);
	}
	else if (!Trigger.IsNone())
	{
		// Gespraech ohne Quest (z. B. Messstation): der Ausloeser gilt fuer alle laufenden Quests.
		FireWorldTrigger(Trigger);
	}
	if (Next.IsNone())
	{
		ActiveDialog = nullptr;
		ActiveDialogQuest = nullptr;
		ActiveNodeId = NAME_None;
	}
	else
	{
		ActiveNodeId = Next;
	}
	return true;
}

FText UGenesisStorySubsystem::GetActiveObjective() const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	if (!Bundle)
	{
		return FText::GetEmpty();
	}
	for (const FGenesisQuestState& State : Bundle->Life.Quests)
	{
		const UGenesisQuestDefinition* Quest = State.bCompleted ? nullptr : GetDefault<UGenesisStorySettings>()->LoadQuest(State.QuestId);
		if (const FGenesisQuestStep* Step = Quest ? Quest->FindStep(State.CurrentStepId) : nullptr)
		{
			return Step->Objective;
		}
	}
	return FText::GetEmpty();
}

// ---------------------------------------------------------------- HUD

void AGenesisHUD::DrawHUD()
{
	Super::DrawHUD();
	const UGenesisStorySubsystem* Story = GetGameInstance() ? GetGameInstance()->GetSubsystem<UGenesisStorySubsystem>() : nullptr;
	if (!Story || !Canvas)
	{
		return;
	}
	UFont* Font = GEngine->GetMediumFont();
	const float Scale = Canvas->ClipY / 1080.f * 1.4f;

	if (Story->IsInDialog())
	{
		float Y = Canvas->ClipY * 0.68f;
		const float X = Canvas->ClipX * 0.18f;
		DrawRect(FLinearColor(0.f, 0.f, 0.f, 0.55f), X - 20.f, Y - 15.f, Canvas->ClipX * 0.64f, Canvas->ClipY * 0.28f);
		DrawText(Story->GetDialogSpeakerName().ToString() + TEXT(":"), FLinearColor(0.85f, 0.8f, 0.6f), X, Y, Font, Scale);
		Y += 30.f * Scale;
		// Einfacher Zeilenumbruch nach Woertern (Platzhalter-HUD).
		TArray<FString> Words;
		Story->GetDialogText().ToString().ParseIntoArrayWS(Words);
		FString Line;
		for (int32 i = 0; i < Words.Num(); ++i)
		{
			const FString Candidate = Line.IsEmpty() ? Words[i] : Line + TEXT(" ") + Words[i];
			if (Candidate.Len() > 72 && !Line.IsEmpty())
			{
				DrawText(Line, FLinearColor::White, X, Y, Font, Scale);
				Y += 26.f * Scale;
				Line = Words[i];
			}
			else
			{
				Line = Candidate;
			}
		}
		DrawText(Line, FLinearColor::White, X, Y, Font, Scale);
		Y += 45.f * Scale;
		const TArray<FText> Choices = Story->GetDialogChoiceTexts();
		for (int32 i = 0; i < Choices.Num(); ++i)
		{
			DrawText(FString::Printf(TEXT("%d) %s"), i + 1, *Choices[i].ToString()), FLinearColor(0.8f, 0.9f, 1.f), X + 20.f, Y, Font, Scale);
			Y += 28.f * Scale;
		}
	}
	else
	{
		const FText Objective = Story->GetActiveObjective();
		if (!Objective.IsEmpty())
		{
			DrawText(TEXT("Ziel: ") + Objective.ToString(), FLinearColor(0.95f, 0.95f, 0.9f), 40.f, 40.f, Font, Scale);
		}
	}
}

TArray<FString> UGenesisStoryLibrary::ValidateQuest(UGenesisQuestDefinition* Quest)
{
	return Quest ? FGenesisStory::ValidateQuest(*Quest) : TArray<FString>{ TEXT("Keine Quest") };
}
