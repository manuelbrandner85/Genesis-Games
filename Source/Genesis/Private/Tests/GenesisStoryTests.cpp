#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Causality/GenesisCausality.h"
#include "Save/GenesisSaveStore.h"
#include "Story/GenesisStory.h"

namespace GenesisStoryTests
{
	static const FName Market = TEXT("NPC_TEST_02");
	static const FName Workshop = TEXT("NPC_TEST_01");

	static UGenesisQuestDefinition* TestQuest()
	{
		return GetDefault<UGenesisStorySettings>()->LoadQuest(TEXT("TEST_Q01"));
	}

	static FGenesisSaveBundle MakeWorld()
	{
		FGenesisSaveBundle Bundle;
		Bundle.World.WorldDateTime = FDateTime(2026, 6, 15, 9, 0, 0);
		return Bundle;
	}

	/** Spielt eine Antwort im aktuellen Questschritt (wie im Spiel, nur ohne Welt). */
	static bool Say(FAutomationTestBase& Test, FGenesisSaveBundle& Bundle, const UGenesisQuestDefinition& Quest, FName ChoiceId)
	{
		const FGenesisQuestStep* Step = FGenesisStory::GetCurrentStep(Bundle, Quest);
		const UGenesisDialogDefinition* Dialog = Step ? Step->Dialog.LoadSynchronous() : nullptr;
		const FGenesisDialogNode* Node = Dialog ? Dialog->FindNode(Dialog->StartNodeId) : nullptr;
		if (!Node)
		{
			Test.AddError(TEXT("Kein Gespraech im aktuellen Schritt"));
			return false;
		}
		for (const FGenesisDialogChoice* Choice : FGenesisStory::GetAvailableChoices(Bundle, *Node, Step->TalkToNpcId))
		{
			if (Choice->ChoiceId == ChoiceId)
			{
				FName Trigger;
				FGenesisStory::ApplyChoice(Bundle, *Choice, Step->TalkToNpcId,
					[&Bundle](const FGenesisEventSpec& Spec) { return FGenesisCausality::RecordEvent(Bundle, Spec, *GetDefault<UGenesisCausalitySettings>()); }, Trigger);
				FGenesisStory::FireTrigger(Bundle, Quest, Trigger);
				return true;
			}
		}
		return false; // Antwort nicht verfuegbar
	}

	static float Trust(const FGenesisSaveBundle& Bundle, FName Npc)
	{
		return FGenesisCausality::GetAttitude(Bundle, Npc, FGenesisCausality::PlayerSubjectId(0)).Trust;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisAllQuestsCleanTest, "Genesis.Story.Validate.AllProjectQuestsClean",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisAllQuestsCleanTest::RunTest(const FString&)
{
	const TArray<TSoftObjectPtr<UGenesisQuestDefinition>>& Quests = GetDefault<UGenesisStorySettings>()->Quests;
	TestTrue(TEXT("Mindestens eine Quest konfiguriert"), Quests.Num() > 0);
	for (const TSoftObjectPtr<UGenesisQuestDefinition>& Ref : Quests)
	{
		const UGenesisQuestDefinition* Quest = Ref.LoadSynchronous();
		if (!TestNotNull(*FString::Printf(TEXT("Quest ladbar: %s"), *Ref.ToString()), Quest))
		{
			continue;
		}
		AddInfo(FString::Printf(TEXT("%s: %d Schritte%s"), *Quest->QuestId.ToString(), Quest->Steps.Num(), Quest->bPlaceholderContent ? TEXT(" (Platzhalter-Inhalt)") : TEXT("")));
		for (const FString& Error : FGenesisStory::ValidateQuest(*Quest))
		{
			AddError(Error);
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisDeadEndTest, "Genesis.Story.Validate.DetectsDeadEnds",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisDeadEndTest::RunTest(const FString&)
{
	// Absichtlich fehlerhaft: jede Fehlerart einmal.
	UGenesisDialogDefinition* Dialog = NewObject<UGenesisDialogDefinition>();
	Dialog->DialogId = TEXT("D_BROKEN");
	Dialog->StartNodeId = TEXT("N1");
	{
		FGenesisDialogNode& N1 = Dialog->Nodes.AddDefaulted_GetRef();
		N1.NodeId = TEXT("N1");
		FGenesisDialogChoice& A = N1.Choices.AddDefaulted_GetRef(); A.ChoiceId = TEXT("C_A"); A.QuestTrigger = TEXT("T_A");
		FGenesisDialogChoice& U = N1.Choices.AddDefaulted_GetRef(); U.ChoiceId = TEXT("C_UNUSED"); U.QuestTrigger = TEXT("T_UNUSED");
		FGenesisDialogChoice& L = N1.Choices.AddDefaulted_GetRef(); L.ChoiceId = TEXT("C_LOOP"); L.NextNodeId = TEXT("N_LOOP1");
		FGenesisDialogChoice& X = N1.Choices.AddDefaulted_GetRef(); X.ChoiceId = TEXT("C_BAD"); X.NextNodeId = TEXT("N_MISSING");
		FGenesisDialogChoice& E = N1.Choices.AddDefaulted_GetRef(); E.ChoiceId = TEXT("C_EVT"); E.Consequences.AddDefaulted_GetRef().EventType = TEXT("FLY_TO_MOON");

		FGenesisDialogNode& L1 = Dialog->Nodes.AddDefaulted_GetRef();
		L1.NodeId = TEXT("N_LOOP1");
		FGenesisDialogChoice& L1C = L1.Choices.AddDefaulted_GetRef(); L1C.ChoiceId = TEXT("C_L1"); L1C.NextNodeId = TEXT("N_LOOP2");
		FGenesisDialogNode& L2 = Dialog->Nodes.AddDefaulted_GetRef();
		L2.NodeId = TEXT("N_LOOP2");
		FGenesisDialogChoice& L2C = L2.Choices.AddDefaulted_GetRef(); L2C.ChoiceId = TEXT("C_L2"); L2C.NextNodeId = TEXT("N_LOOP1");

		FGenesisDialogNode& G = Dialog->Nodes.AddDefaulted_GetRef();
		G.NodeId = TEXT("N_GATED");
		FGenesisDialogChoice& GC = G.Choices.AddDefaulted_GetRef(); GC.ChoiceId = TEXT("C_G"); GC.RequiredTrust = 0.5f;
	}

	UGenesisQuestDefinition* Quest = NewObject<UGenesisQuestDefinition>();
	Quest->QuestId = TEXT("Q_BROKEN");
	Quest->StartStepId = TEXT("S1");
	{
		FGenesisQuestStep& S1 = Quest->Steps.AddDefaulted_GetRef();
		S1.StepId = TEXT("S1"); S1.TalkToNpcId = TEXT("NPC_GHOST"); S1.Dialog = Dialog;
		FGenesisQuestEdge& E1 = S1.Edges.AddDefaulted_GetRef(); E1.Trigger = TEXT("T_A"); E1.NextStepId = TEXT("S2");
		FGenesisQuestEdge& E2 = S1.Edges.AddDefaulted_GetRef(); E2.Trigger = TEXT("T_NEVER"); E2.NextStepId = TEXT("S_MISSING");
		FGenesisQuestStep& S2 = Quest->Steps.AddDefaulted_GetRef();
		S2.StepId = TEXT("S2"); S2.TalkToNpcId = GenesisStoryTests::Market; S2.Dialog = Dialog;
		FGenesisQuestStep& S3 = Quest->Steps.AddDefaulted_GetRef();
		S3.StepId = TEXT("S3"); S3.TalkToNpcId = GenesisStoryTests::Market; S3.Dialog = Dialog;
		FGenesisQuestEdge& E3 = S3.Edges.AddDefaulted_GetRef(); E3.Trigger = TEXT("T_A"); E3.OutcomeId = TEXT("END");
	}

	const TArray<FString> Errors = FGenesisStory::ValidateQuest(*Quest);
	for (const FString& Error : Errors)
	{
		AddInfo(Error);
	}
	auto Has = [&Errors](const TCHAR* Part) { return Errors.ContainsByPredicate([Part](const FString& S) { return S.Contains(Part); }); };
	TestTrue(TEXT("Schritt ohne Ausweg"), Has(TEXT("S2: kein Weg weiter")));
	TestTrue(TEXT("Fehlender Folgeschritt"), Has(TEXT("Folgeschritt S_MISSING fehlt")));
	TestTrue(TEXT("Unerreichbarer Schritt"), Has(TEXT("S3: nie erreichbar")));
	TestTrue(TEXT("Kein Questende von S2"), Has(TEXT("S2: von hier ist kein Questende erreichbar")));
	TestTrue(TEXT("Ausloeser, der nie kommt"), Has(TEXT("Ausloeser T_NEVER wird im Gespraech nie ausgeloest")));
	TestTrue(TEXT("Ausloeser ohne Wirkung"), Has(TEXT("Ausloeser T_UNUSED bleibt ohne Wirkung")));
	TestTrue(TEXT("Unbekannte Figur"), Has(TEXT("NPC_GHOST ist nicht in der Registry")));
	TestTrue(TEXT("Dialog: fehlender Knoten"), Has(TEXT("Folgeknoten N_MISSING fehlt")));
	TestTrue(TEXT("Dialog: Schleife ohne Ausgang"), Has(TEXT("Schleife ohne Ausgang")));
	TestTrue(TEXT("Dialog: nur bedingte Antworten"), Has(TEXT("alle Antworten haben Bedingungen")));
	TestTrue(TEXT("Dialog: unerreichbarer Knoten"), Has(TEXT("N_GATED: nie erreichbar")));
	TestTrue(TEXT("Dialog: unbekannter Ereignistyp"), Has(TEXT("unbekannter Ereignistyp FLY_TO_MOON")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisAllPathsTest, "Genesis.Story.Run.AllPathsReachOutcome",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisAllPathsTest::RunTest(const FString&)
{
	using namespace GenesisStoryTests;
	const UGenesisQuestDefinition* Quest = TestQuest();
	if (!TestNotNull(TEXT("TEST_Q01"), Quest))
	{
		return false;
	}

	// Weg 1: ablehnen.
	{
		FGenesisSaveBundle W = MakeWorld();
		FGenesisStory::StartQuest(W, *Quest);
		TestTrue(TEXT("Ablehnen moeglich"), Say(*this, W, *Quest, TEXT("C_DECLINE")));
		const FGenesisQuestState* S = FGenesisStory::FindQuestState(W, Quest->QuestId);
		TestTrue(TEXT("Ausgang DECLINED"), S && S->bCompleted && S->OutcomeId == FName(TEXT("DECLINED")));
		TestTrue(TEXT("Haendlerin vertraut weniger"), Trust(W, Market) < 0.f);
	}
	// Weg 2: erst zoegern, dann helfen, Waage abgeben.
	{
		FGenesisSaveBundle W = MakeWorld();
		FGenesisStory::StartQuest(W, *Quest);
		Say(*this, W, *Quest, TEXT("C_LATER"));
		TestTrue(TEXT("Zoegern laesst die Quest am Anfang"), FGenesisStory::GetCurrentStep(W, *Quest)->StepId == FName(TEXT("S1")));
		Say(*this, W, *Quest, TEXT("C_ACCEPT"));
		TestFalse(TEXT("Spaeter zahlen ohne Vertrauen nicht waehlbar"), Say(*this, W, *Quest, TEXT("C_PAY_LATER")));
		TestTrue(TEXT("Werkstatt"), Say(*this, W, *Quest, TEXT("C_THANKS")));
		TestEqual(TEXT("Weltzustand: Waage repariert"), W.World.EventFlags.FindRef(TEXT("Q01_SCALE_REPAIRED")), 1);
		TestTrue(TEXT("Abgeben"), Say(*this, W, *Quest, TEXT("C_GIVE")));
		const FGenesisQuestState* S = FGenesisStory::FindQuestState(W, Quest->QuestId);
		TestTrue(TEXT("Ausgang HELPED_MARKET"), S && S->OutcomeId == FName(TEXT("HELPED_MARKET")));
		TestTrue(TEXT("Haendlerin vertraut mehr"), Trust(W, Market) > 0.f);
		AddInfo(FString::Printf(TEXT("Verlauf: %s"), S ? *FString::JoinBy(S->History, TEXT(" > "), [](FName N) { return N.ToString(); }) : TEXT("-")));
	}
	// Weg 3: Waage behalten.
	{
		FGenesisSaveBundle W = MakeWorld();
		FGenesisStory::StartQuest(W, *Quest);
		Say(*this, W, *Quest, TEXT("C_ACCEPT"));
		Say(*this, W, *Quest, TEXT("C_THANKS"));
		Say(*this, W, *Quest, TEXT("C_KEEP"));
		const FGenesisQuestState* S = FGenesisStory::FindQuestState(W, Quest->QuestId);
		TestTrue(TEXT("Ausgang KEPT_SCALE"), S && S->OutcomeId == FName(TEXT("KEPT_SCALE")));
		TestTrue(TEXT("Vertrauen gebrochen"), Trust(W, Market) < -0.2f);
		TestTrue(TEXT("Verdecktes Profil: Zuverlaessigkeit sinkt"), W.Life.ConductProfile.FindRef(TEXT("Reliability")) < 0.f);
	}
	// Weg 4: Vertrauen der Werkstatt schaltet eine Antwort frei.
	{
		FGenesisSaveBundle W = MakeWorld();
		FGenesisEventSpec Earlier;
		Earlier.EventType = TEXT("HELPED");
		Earlier.ActorId = FGenesisCausality::PlayerSubjectId(0);
		Earlier.TargetIds = { Workshop };
		FGenesisCausality::RecordEvent(W, Earlier, *GetDefault<UGenesisCausalitySettings>());
		FGenesisStory::StartQuest(W, *Quest);
		Say(*this, W, *Quest, TEXT("C_ACCEPT"));
		TestTrue(TEXT("Mit Vertrauen: spaeter zahlen waehlbar"), Say(*this, W, *Quest, TEXT("C_PAY_LATER")));
		TestEqual(TEXT("Weltzustand: Schuld bei der Werkstatt"), W.World.EventFlags.FindRef(TEXT("Q01_OWES_WORKSHOP")), 1);
		TestTrue(TEXT("Weiter zu S3"), FGenesisStory::GetCurrentStep(W, *Quest)->StepId == FName(TEXT("S3")));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisQuestSaveTest, "Genesis.Story.SaveLoadMidQuest",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisQuestSaveTest::RunTest(const FString&)
{
	using namespace GenesisStoryTests;
	const UGenesisQuestDefinition* Quest = TestQuest();
	if (!TestNotNull(TEXT("TEST_Q01"), Quest))
	{
		return false;
	}
	FGenesisSaveBundle W = MakeWorld();
	FGenesisStory::StartQuest(W, *Quest);
	Say(*this, W, *Quest, TEXT("C_ACCEPT"));

	TArray<uint8> Bytes;
	FGenesisSaveStore::Encode(W, Bytes);
	FGenesisSaveBundle L;
	TestTrue(TEXT("Laden"), FGenesisSaveStore::Decode(Bytes, L) == EGenesisSaveResult::Ok);
	const FGenesisQuestState* S = FGenesisStory::FindQuestState(L, Quest->QuestId);
	TestTrue(TEXT("Mitten in der Quest geladen: S2"), S && S->CurrentStepId == FName(TEXT("S2")) && !S->bCompleted);
	TestEqual(TEXT("Verlauf erhalten"), S ? S->History.Num() : 0, 3);
	TestFalse(TEXT("Zweiter Start derselben Quest abgelehnt"), FGenesisStory::StartQuest(L, *Quest));

	Say(*this, L, *Quest, TEXT("C_THANKS"));
	Say(*this, L, *Quest, TEXT("C_GIVE"));
	S = FGenesisStory::FindQuestState(L, Quest->QuestId);
	TestTrue(TEXT("Nach dem Laden zu Ende spielbar"), S && S->OutcomeId == FName(TEXT("HELPED_MARKET")));
	return true;
}

#endif
