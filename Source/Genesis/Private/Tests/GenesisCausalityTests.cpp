#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Causality/GenesisCausality.h"
#include "Save/GenesisSaveStore.h"

namespace GenesisCausalityTests
{
	static const UGenesisCausalitySettings& Settings() { return *GetDefault<UGenesisCausalitySettings>(); }
	static const FName A = TEXT("NPC_A");
	static const FName B = TEXT("NPC_B");
	static const FName C = TEXT("NPC_C");

	static FGenesisSaveBundle MakeWorld()
	{
		FGenesisSaveBundle Bundle;
		Bundle.World.WorldDateTime = FDateTime(2026, 6, 15, 10, 0, 0);
		Bundle.Life.LifeIndex = 0;
		Bundle.Life.LocationId = TEXT("/Game/Maps/L_GenesisTest");
		return Bundle;
	}

	static FGenesisEventSpec Spec(FName Type, FName Actor, TArray<FName> Targets, TArray<FName> Witnesses = {}, TArray<FName> Causes = {})
	{
		FGenesisEventSpec S;
		S.EventType = Type;
		S.ActorId = Actor;
		S.TargetIds = MoveTemp(Targets);
		S.WitnessIds = MoveTemp(Witnesses);
		S.CauseEventIds = MoveTemp(Causes);
		return S;
	}

	static const FGenesisNpcMemory* MemoryOf(const FGenesisSaveBundle& Bundle, FName Npc, FName EventId)
	{
		const FGenesisNpcState* State = FGenesisCausality::FindNpc(Bundle, Npc);
		return State ? State->Memories.FindByPredicate([EventId](const FGenesisNpcMemory& M) { return M.EventId == EventId; }) : nullptr;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisCausalityConfigTest, "Genesis.Causality.Config.EventTypesLoaded",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisCausalityConfigTest::RunTest(const FString&)
{
	using namespace GenesisCausalityTests;
	TestEqual(TEXT("8 Ereignistypen aus der Konfiguration"), Settings().EventTypes.Num(), 8);
	const FGenesisEventTypeDef* Broken = Settings().FindType(TEXT("PROMISE_BROKEN"));
	TestTrue(TEXT("PROMISE_BROKEN mit Vertrauensverlust"), Broken && Broken->TrustDelta < 0.f && Broken->ConductDeltas.Contains(TEXT("Reliability")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisRecordEventTest, "Genesis.Causality.RecordEventFormsMemoriesAndAttitudes",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisRecordEventTest::RunTest(const FString&)
{
	using namespace GenesisCausalityTests;
	FGenesisSaveBundle W = MakeWorld();
	const FName P0 = FGenesisCausality::PlayerSubjectId(0);

	const FName E = FGenesisCausality::RecordEvent(W, Spec(TEXT("HELPED"), P0, { A }, { B }), Settings());
	TestEqual(TEXT("Erste EventId"), E, FName(TEXT("EV_000001")));
	const FGenesisCausalEvent* Event = FGenesisCausality::FindEvent(W, E);
	TestTrue(TEXT("Zeit, Ort, Leben aus dem Spielstand"), Event && Event->WorldTime == W.World.WorldDateTime && Event->LocationId == W.Life.LocationId && Event->LifeIndex == 0);

	const FGenesisNpcMemory* MemA = MemoryOf(W, A, E);
	const FGenesisNpcMemory* MemB = MemoryOf(W, B, E);
	TestTrue(TEXT("Betroffene erinnert sich voll"), MemA && MemA->Source == EGenesisMemorySource::Experienced && FMath::IsNearlyEqual(MemA->InitialSalience, 0.4f));
	TestTrue(TEXT("Zeuge erinnert sich schwaecher"), MemB && MemB->Source == EGenesisMemorySource::Witnessed && FMath::IsNearlyEqual(MemB->InitialSalience, 0.2f));

	const FGenesisAttitude AttA = FGenesisCausality::GetAttitude(W, A, P0);
	const FGenesisAttitude AttB = FGenesisCausality::GetAttitude(W, B, P0);
	TestTrue(TEXT("Vertrauen der Betroffenen +0,15"), FMath::IsNearlyEqual(AttA.Trust, 0.15f) && FMath::IsNearlyEqual(AttA.Affinity, 0.10f));
	TestTrue(TEXT("Vertrauen des Zeugen +0,075"), FMath::IsNearlyEqual(AttB.Trust, 0.075f));
	TestTrue(TEXT("Verdecktes Profil: Empathie"), FMath::IsNearlyEqual(W.Life.ConductProfile.FindRef(TEXT("Empathy")), 0.05f));
	TestEqual(TEXT("Graph widerspruchsfrei"), FGenesisCausality::ValidateGraph(W).Num(), 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisCauseChainTest, "Genesis.Causality.CauseChainAndRejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisCauseChainTest::RunTest(const FString&)
{
	using namespace GenesisCausalityTests;
	FGenesisSaveBundle W = MakeWorld();
	const FName P0 = FGenesisCausality::PlayerSubjectId(0);

	const FName E1 = FGenesisCausality::RecordEvent(W, Spec(TEXT("PROMISE_BROKEN"), P0, { A }), Settings());
	W.World.WorldDateTime += FTimespan::FromDays(1.0);
	const FName E2 = FGenesisCausality::RecordEvent(W, Spec(TEXT("ARGUMENT"), A, { P0 }, { B }, { E1 }), Settings());
	W.World.WorldDateTime += FTimespan::FromDays(3.0);
	const FName E3 = FGenesisCausality::RecordEvent(W, Spec(TEXT("IGNORED_REQUEST"), A, { P0 }, {}, { E2 }), Settings());

	const TArray<FName> Chain = FGenesisCausality::GetCauseChain(W, E3);
	TestTrue(TEXT("Kette E3 <- E2 <- E1"), Chain.Num() == 2 && Chain[0] == E2 && Chain[1] == E1);
	TestTrue(TEXT("Handelnde Figur erinnert eigene Tat"), MemoryOf(W, A, E2) != nullptr);
	TestNull(TEXT("Spieler hat keinen NPC-Zustand"), FGenesisCausality::FindNpc(W, P0));

	FString Error;
	AddExpectedError(TEXT("Ereignis abgelehnt"), EAutomationExpectedErrorFlags::Contains, 3);
	TestTrue(TEXT("Unbekannte Ursache abgelehnt"), FGenesisCausality::RecordEvent(W, Spec(TEXT("HELPED"), P0, { A }, {}, { TEXT("EV_999999") }), Settings(), &Error).IsNone());
	W.World.WorldDateTime -= FTimespan::FromDays(10.0);
	TestTrue(TEXT("Ursache aus der Zukunft abgelehnt"), FGenesisCausality::RecordEvent(W, Spec(TEXT("HELPED"), P0, { A }, {}, { E3 }), Settings(), &Error).IsNone());
	TestTrue(TEXT("Unbekannter Typ abgelehnt"), FGenesisCausality::RecordEvent(W, Spec(TEXT("FLY_TO_MOON"), P0, { A }), Settings(), &Error).IsNone());
	TestEqual(TEXT("Nur drei Ereignisse"), W.World.CausalEvents.Num(), 3);
	TestEqual(TEXT("Graph widerspruchsfrei"), FGenesisCausality::ValidateGraph(W).Num(), 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisMemoryFadeTest, "Genesis.Causality.MemoryFadesButTruthRemains",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisMemoryFadeTest::RunTest(const FString&)
{
	using namespace GenesisCausalityTests;
	FGenesisSaveBundle W = MakeWorld();
	const FName P0 = FGenesisCausality::PlayerSubjectId(0);
	const FName Gift = FGenesisCausality::RecordEvent(W, Spec(TEXT("GIFT"), P0, { A }), Settings());
	const FName Saved = FGenesisCausality::RecordEvent(W, Spec(TEXT("SAVED_LIFE"), P0, { A }), Settings());

	W.World.WorldDateTime += FTimespan::FromDays(3.0 * 365.0);
	const TArray<FGenesisNpcMemory> Before = FGenesisCausality::GetMemories(W, A, W.World.WorldDateTime, Settings());
	TestTrue(TEXT("Lebensrettung ist nach 3 Jahren die staerkste Erinnerung"), Before.Num() == 2 && Before[0].EventId == Saved);

	const int32 Removed = FGenesisCausality::PruneForgotten(W, W.World.WorldDateTime, Settings());
	TestEqual(TEXT("Geschenk nach 3 Jahren vergessen"), Removed, 1);
	TestNull(TEXT("Geschenk-Erinnerung weg"), MemoryOf(W, A, Gift));
	TestNotNull(TEXT("Lebensrettung bleibt"), MemoryOf(W, A, Saved));
	TestNotNull(TEXT("Ereignis selbst bleibt im Kausalgraphen"), FGenesisCausality::FindEvent(W, Gift));
	TestTrue(TEXT("Vertrauen bleibt trotz Vergessen"), FGenesisCausality::GetAttitude(W, A, P0).Trust > 0.5f);
	TestEqual(TEXT("Graph widerspruchsfrei"), FGenesisCausality::ValidateGraph(W).Num(), 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisRumorTest, "Genesis.Causality.RumorDependsOnTrustInTeller",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisRumorTest::RunTest(const FString&)
{
	using namespace GenesisCausalityTests;
	FGenesisSaveBundle W = MakeWorld();
	const FName P0 = FGenesisCausality::PlayerSubjectId(0);
	const FName E = FGenesisCausality::RecordEvent(W, Spec(TEXT("HARMED"), P0, { A }), Settings());

	// C misstraut A stark (Glaubwuerdigkeit 0,1), B steht A neutral gegenueber (0,5).
	FGenesisNpcState& StateC = W.World.Npcs.AddDefaulted_GetRef();
	StateC.NpcId = C;
	StateC.Attitudes.Add(A, FGenesisAttitude{ -0.8f, 0.f });

	TestTrue(TEXT("A erzaehlt B"), FGenesisCausality::ShareMemory(W, A, B, E, Settings()));
	TestTrue(TEXT("A erzaehlt C"), FGenesisCausality::ShareMemory(W, A, C, E, Settings()));
	TestFalse(TEXT("Zweimal erzaehlen aendert nichts"), FGenesisCausality::ShareMemory(W, A, B, E, Settings()));
	TestFalse(TEXT("Wer nichts weiss, kann nichts erzaehlen"), FGenesisCausality::ShareMemory(W, TEXT("NPC_X"), B, E, Settings()));

	const FGenesisNpcMemory* MemB = MemoryOf(W, B, E);
	TestTrue(TEXT("B hat es gehoert, von A"), MemB && MemB->Source == EGenesisMemorySource::Heard && MemB->HeardFrom == A);
	const float TrustB = FGenesisCausality::GetAttitude(W, B, P0).Trust;
	const float TrustC = FGenesisCausality::GetAttitude(W, C, P0).Trust;
	AddInfo(FString::Printf(TEXT("Vertrauen zum Spieler nach Geruecht: B %.3f, C %.3f, A %.3f"), TrustB, TrustC, FGenesisCausality::GetAttitude(W, A, P0).Trust));
	TestTrue(TEXT("Geruecht wirkt auf B (-0,05)"), FMath::IsNearlyEqual(TrustB, -0.05f, 1e-4f));
	TestTrue(TEXT("Geruecht wirkt auf misstrauische C kaum (-0,01)"), FMath::IsNearlyEqual(TrustC, -0.01f, 1e-4f));
	TestTrue(TEXT("Gehoertes wirkt schwaecher als Erlebtes"), FGenesisCausality::GetAttitude(W, A, P0).Trust < TrustB);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisNewLifeTest, "Genesis.Causality.NewLifeIsAStranger",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisNewLifeTest::RunTest(const FString&)
{
	using namespace GenesisCausalityTests;
	FGenesisSaveBundle W = MakeWorld();
	const FName E = FGenesisCausality::RecordEvent(W, Spec(TEXT("SAVED_LIFE"), FGenesisCausality::PlayerSubjectId(0), { A }), Settings());
	// Eine einzelne Lebensrettung macht herzlich; Naehe ("Close") entsteht erst ueber mehrere Erlebnisse.
	TestTrue(TEXT("Leben 0: herzlich"), FGenesisCausality::ToDisposition(FGenesisCausality::GetAttitude(W, A, FGenesisCausality::PlayerSubjectId(0))) == EGenesisDisposition::Warm);

	W.Life.LifeIndex = 1; // Wiedergeburt: neuer Mensch
	TestTrue(TEXT("Leben 1: Fremder"), FGenesisCausality::ToDisposition(FGenesisCausality::GetAttitude(W, A, FGenesisCausality::PlayerSubjectId(1))) == EGenesisDisposition::Neutral);
	TestNotNull(TEXT("A erinnert sich weiter an den Retter von damals"), MemoryOf(W, A, E));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisValidateGraphTest, "Genesis.Causality.ValidateDetectsContradictions",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisValidateGraphTest::RunTest(const FString&)
{
	using namespace GenesisCausalityTests;
	FGenesisSaveBundle W = MakeWorld();
	FGenesisCausalEvent E1;
	E1.EventId = TEXT("EV_1");
	E1.WorldTime = FDateTime(2026, 1, 1);
	E1.CauseEventIds = { TEXT("EV_2") };
	FGenesisCausalEvent E2 = E1;
	E2.EventId = TEXT("EV_2");
	E2.CauseEventIds = { TEXT("EV_1") };
	FGenesisCausalEvent E3 = E1;
	E3.EventId = TEXT("EV_3");
	E3.CauseEventIds = { TEXT("EV_MISSING") };
	W.World.CausalEvents = { E1, E2, E3 };
	FGenesisNpcState& Npc = W.World.Npcs.AddDefaulted_GetRef();
	Npc.NpcId = A;
	FGenesisNpcMemory Ghost;
	Ghost.EventId = TEXT("EV_GHOST");
	Npc.Memories.Add(Ghost);

	const TArray<FString> Errors = FGenesisCausality::ValidateGraph(W);
	for (const FString& Error : Errors)
	{
		AddInfo(Error);
	}
	TestTrue(TEXT("Zyklus erkannt"), Errors.ContainsByPredicate([](const FString& S) { return S.Contains(TEXT("Zyklus")); }));
	TestTrue(TEXT("Fehlende Ursache erkannt"), Errors.ContainsByPredicate([](const FString& S) { return S.Contains(TEXT("EV_MISSING")); }));
	TestTrue(TEXT("Unbelegte Erinnerung erkannt"), Errors.ContainsByPredicate([](const FString& S) { return S.Contains(TEXT("EV_GHOST")); }));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisCausalitySaveTest, "Genesis.Causality.SaveLoadRoundTrip",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisCausalitySaveTest::RunTest(const FString&)
{
	using namespace GenesisCausalityTests;
	FGenesisSaveBundle W = MakeWorld();
	const FName P0 = FGenesisCausality::PlayerSubjectId(0);
	const FName E1 = FGenesisCausality::RecordEvent(W, Spec(TEXT("PROMISE_BROKEN"), P0, { A }, { B }), Settings());
	W.World.WorldDateTime += FTimespan::FromHours(5.0);
	FGenesisCausality::RecordEvent(W, Spec(TEXT("ARGUMENT"), A, { P0 }, { B }, { E1 }), Settings());
	FGenesisCausality::ShareMemory(W, B, C, E1, Settings());

	TArray<uint8> Bytes;
	FGenesisSaveStore::Encode(W, Bytes);
	FGenesisSaveBundle L;
	TestTrue(TEXT("Laden"), FGenesisSaveStore::Decode(Bytes, L) == EGenesisSaveResult::Ok);
	TestEqual(TEXT("Ereignisse"), L.World.CausalEvents.Num(), 2);
	TestEqual(TEXT("Naechste Seriennummer"), L.World.NextEventSerial, W.World.NextEventSerial);
	TestEqual(TEXT("Figuren"), L.World.Npcs.Num(), W.World.Npcs.Num());
	TestTrue(TEXT("Haltung exakt"), FGenesisCausality::GetAttitude(L, A, P0).Trust == FGenesisCausality::GetAttitude(W, A, P0).Trust);
	const FGenesisNpcMemory* Heard = MemoryOf(L, C, E1);
	TestTrue(TEXT("Geruecht mit Quelle erhalten"), Heard && Heard->Source == EGenesisMemorySource::Heard && Heard->HeardFrom == B);
	TestEqual(TEXT("Ursachen erhalten"), FGenesisCausality::GetCauseChain(L, TEXT("EV_000002")).Num(), 1);
	TestTrue(TEXT("Verdecktes Profil erhalten"), FMath::IsNearlyEqual(L.Life.ConductProfile.FindRef(TEXT("Reliability")), -0.12f));
	TestEqual(TEXT("Geladener Graph widerspruchsfrei"), FGenesisCausality::ValidateGraph(L).Num(), 0);

	// Spielstand aus Schema 2 laedt mit leerem Graphen.
	TArray<uint8> V2;
	FGenesisSaveStore::EncodeRaw(2, 3, TEXT("{\"schemaVersion\":2,\"sequence\":3,\"world\":{\"worldDateTime\":\"2026-06-15T10:00:00.000Z\"}}"), V2);
	FGenesisSaveBundle Old;
	TestTrue(TEXT("Schema 2 ladbar"), FGenesisSaveStore::Decode(V2, Old) == EGenesisSaveResult::Ok);
	TestTrue(TEXT("Schema 2 -> aktuell, leerer Graph"), Old.SchemaVersion == FGenesisSaveBundle::CurrentSchemaVersion && Old.World.CausalEvents.Num() == 0 && Old.World.NextEventSerial == 1);
	return true;
}

#endif
