#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Save/GenesisSaveStore.h"
#include "Time/GenesisTimeTypes.h"
#include "Time/GenesisWorldClockSubsystem.h"

namespace GenesisTimeTests
{
	static const UGenesisTimeSettings& Settings() { return *GetDefault<UGenesisTimeSettings>(); }

	static FGenesisLifeState Unborn(const FDateTime& Conception)
	{
		FGenesisLifeState Life;
		Life.ConceptionDateTime = Conception;
		Life.bBorn = false;
		Life.Stage = EGenesisLifeStage::Conception;
		return Life;
	}

	static FGenesisLifeState BornAt(const FDateTime& Birth)
	{
		FGenesisLifeState Life;
		Life.bBorn = true;
		Life.BirthDateTime = Birth;
		Life.ConceptionDateTime = Birth - FTimespan::FromDays(266.0);
		Life.Stage = EGenesisLifeStage::Infant;
		return Life;
	}

	static FDateTime AfterYears(const FDateTime& Start, double Years)
	{
		return Start + FTimespan::FromDays(Years * FGenesisLifeCycle::DaysPerYear);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisPrenatalStagesTest, "Genesis.Time.LifeStages.Prenatal",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisPrenatalStagesTest::RunTest(const FString&)
{
	using namespace GenesisTimeTests;
	const FDateTime C(2026, 11, 3, 22, 0, 0);
	const FGenesisLifeState Life = Unborn(C);
	auto At = [&](double Days) { return FGenesisLifeCycle::ComputeStage(Life, C + FTimespan::FromDays(Days), Settings()); };

	TestTrue(TEXT("Tag 0: Befruchtung"), At(0.0) == EGenesisLifeStage::Conception);
	TestTrue(TEXT("Tag 13,9: noch Vor-Embryonalzeit"), At(13.9) == EGenesisLifeStage::Conception);
	TestTrue(TEXT("Tag 14: Embryo"), At(14.0) == EGenesisLifeStage::Embryo);
	TestTrue(TEXT("Tag 55,9: Embryo"), At(55.9) == EGenesisLifeStage::Embryo);
	TestTrue(TEXT("Tag 56: Fetus"), At(56.0) == EGenesisLifeStage::Fetus);
	TestTrue(TEXT("Tag 266: Geburtszeitraum"), At(266.0) == EGenesisLifeStage::Birth);
	TestTrue(TEXT("Tag 300: keine automatische Geburt"), At(300.0) == EGenesisLifeStage::Birth);
	TestEqual(TEXT("Alter vor Geburt = 0"), FGenesisLifeCycle::GetAgeYears(Life, C + FTimespan::FromDays(200.0)), 0.0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisPostnatalStagesTest, "Genesis.Time.LifeStages.Postnatal",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisPostnatalStagesTest::RunTest(const FString&)
{
	using namespace GenesisTimeTests;
	const FDateTime B(2027, 7, 29, 5, 40, 0);
	FGenesisLifeState Life = BornAt(B);
	auto At = [&](double Years) { return FGenesisLifeCycle::ComputeStage(Life, AfterYears(B, Years), Settings()); };

	TestTrue(TEXT("0,5 J: Saeugling"), At(0.5) == EGenesisLifeStage::Infant);
	TestTrue(TEXT("1 J: Kind"), At(1.0) == EGenesisLifeStage::Child);
	TestTrue(TEXT("8 J: Kind (C06)"), At(8.0) == EGenesisLifeStage::Child);
	TestTrue(TEXT("12 J: Jugend"), At(12.0) == EGenesisLifeStage::Adolescent);
	TestTrue(TEXT("16 J: Jugend (C08)"), At(16.0) == EGenesisLifeStage::Adolescent);
	TestTrue(TEXT("18 J: Erwachsen"), At(18.0) == EGenesisLifeStage::Adult);
	TestTrue(TEXT("65 J: Alter"), At(65.0) == EGenesisLifeStage::Elder);
	TestTrue(TEXT("Alter nach 30 J"), FMath::IsNearlyEqual(FGenesisLifeCycle::GetAgeYears(Life, AfterYears(B, 30.0)), 30.0, 1e-6));

	Life.Stage = EGenesisLifeStage::Echo;
	TestTrue(TEXT("Echo bleibt Echo"), At(90.0) == EGenesisLifeStage::Echo);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSeasonTest, "Genesis.Time.Seasons",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSeasonTest::RunTest(const FString&)
{
	TestTrue(TEXT("Januar Winter"), FGenesisLifeCycle::GetSeason(FDateTime(2026, 1, 15)) == EGenesisSeason::Winter);
	TestTrue(TEXT("28.02. 23:59 Winter"), FGenesisLifeCycle::GetSeason(FDateTime(2026, 2, 28, 23, 59, 0)) == EGenesisSeason::Winter);
	TestTrue(TEXT("01.03. Fruehling"), FGenesisLifeCycle::GetSeason(FDateTime(2026, 3, 1)) == EGenesisSeason::Spring);
	TestTrue(TEXT("Juni Sommer"), FGenesisLifeCycle::GetSeason(FDateTime(2026, 6, 1)) == EGenesisSeason::Summer);
	TestTrue(TEXT("Oktober Herbst"), FGenesisLifeCycle::GetSeason(FDateTime(2026, 10, 18)) == EGenesisSeason::Autumn);
	TestTrue(TEXT("Dezember Winter"), FGenesisLifeCycle::GetSeason(FDateTime(2026, 12, 1)) == EGenesisSeason::Winter);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisAdvanceDaySeasonTest, "Genesis.Time.Advance.DayAndSeasonEvents",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisAdvanceDaySeasonTest::RunTest(const FString&)
{
	using namespace GenesisTimeTests;
	FGenesisSaveBundle Bundle;
	Bundle.World.WorldDateTime = FDateTime(2026, 2, 28, 23, 0, 0);
	Bundle.Life = BornAt(FDateTime(1996, 3, 1));
	Bundle.Life.Stage = EGenesisLifeStage::Adult;

	FGenesisTimeAdvanceResult R = UGenesisWorldClockSubsystem::AdvanceTime(Bundle, FTimespan::FromMinutes(30.0), Settings());
	TestEqual(TEXT("Kein Tageswechsel nach 30 min"), R.DaysChanged, 0);
	TestFalse(TEXT("Keine neue Jahreszeit"), R.bSeasonChanged);

	R = UGenesisWorldClockSubsystem::AdvanceTime(Bundle, FTimespan::FromHours(1.0), Settings());
	TestEqual(TEXT("Tageswechsel"), R.DaysChanged, 1);
	TestTrue(TEXT("Fruehling beginnt"), R.bSeasonChanged && R.NewSeason == EGenesisSeason::Spring);
	TestEqual(TEXT("Weltzeit exakt"), Bundle.World.WorldDateTime, FDateTime(2026, 3, 1, 0, 30, 0));
	TestEqual(TEXT("Kein neuer Lebensabschnitt"), R.StagesEntered.Num(), 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisTimeSkipTest, "Genesis.Time.Advance.TimeSkipThroughStages",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisTimeSkipTest::RunTest(const FString&)
{
	using namespace GenesisTimeTests;
	FGenesisSaveBundle Bundle;
	const FDateTime Birth(2027, 7, 29, 5, 40, 0);
	Bundle.World.WorldDateTime = Birth + FTimespan::FromDays(30.0);
	Bundle.Life = BornAt(Birth);

	const FGenesisTimeAdvanceResult R = UGenesisWorldClockSubsystem::AdvanceTime(Bundle, FTimespan::FromDays(20.0 * FGenesisLifeCycle::DaysPerYear), Settings());
	TestEqual(TEXT("Drei Abschnitte durchlaufen"), R.StagesEntered.Num(), 3);
	if (R.StagesEntered.Num() == 3)
	{
		TestTrue(TEXT("Kind"), R.StagesEntered[0] == EGenesisLifeStage::Child);
		TestTrue(TEXT("Jugend"), R.StagesEntered[1] == EGenesisLifeStage::Adolescent);
		TestTrue(TEXT("Erwachsen"), R.StagesEntered[2] == EGenesisLifeStage::Adult);
	}
	TestTrue(TEXT("Abschnitt gespeichert"), Bundle.Life.Stage == EGenesisLifeStage::Adult);
	const double Age = FGenesisLifeCycle::GetAgeYears(Bundle.Life, Bundle.World.WorldDateTime);
	AddInfo(FString::Printf(TEXT("Alter nach Zeitraffer: %.4f Jahre"), Age));
	TestTrue(TEXT("Alter ~ 20,08 Jahre"), FMath::IsNearlyEqual(Age, 20.0 + 30.0 / FGenesisLifeCycle::DaysPerYear, 1e-6));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisBiologicalPathTest, "Genesis.Time.Advance.ConceptionToBirth",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisBiologicalPathTest::RunTest(const FString&)
{
	using namespace GenesisTimeTests;
	FGenesisSaveBundle Bundle;
	const FDateTime C(2026, 11, 3, 22, 0, 0);
	Bundle.World.WorldDateTime = C;
	Bundle.Life = Unborn(C);

	const FGenesisTimeAdvanceResult R = UGenesisWorldClockSubsystem::AdvanceTime(Bundle, FTimespan::FromDays(270.0), Settings());
	TestEqual(TEXT("Embryo, Fetus, Geburt"), R.StagesEntered.Num(), 3);
	TestTrue(TEXT("Wartet auf Geburt"), Bundle.Life.Stage == EGenesisLifeStage::Birth);
	TestFalse(TEXT("Noch nicht geboren"), Bundle.Life.bBorn);

	FGenesisLifeCycle::CompleteBirth(Bundle.Life, Bundle.World.WorldDateTime);
	TestTrue(TEXT("Saeugling"), Bundle.Life.Stage == EGenesisLifeStage::Infant);
	TestEqual(TEXT("Geburt = Weltzeit"), Bundle.Life.BirthDateTime, Bundle.World.WorldDateTime);

	const FGenesisTimeAdvanceResult R2 = UGenesisWorldClockSubsystem::AdvanceTime(Bundle, FTimespan::FromDays(366.0), Settings());
	TestTrue(TEXT("Nach einem Jahr Kind"), R2.StagesEntered.Num() == 1 && Bundle.Life.Stage == EGenesisLifeStage::Child);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisMigrationTest, "Genesis.Save.MigrateSchema1ToSchema2",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisMigrationTest::RunTest(const FString&)
{
	// Spielstand im alten Format (Schema 1): Jahr/Tag/Uhrzeit + Alter als Zahl.
	const FString V1Json = TEXT("{\"schemaVersion\":1,\"sequence\":5,\"soul\":{\"soulId\":\"0123456789ABCDEF0123456789ABCDEF\",\"livesLived\":1},")
		TEXT("\"world\":{\"worldYear\":2030,\"dayOfYear\":10,\"timeOfDayHours\":6.5,\"worldSeed\":42},")
		TEXT("\"life\":{\"lifeIndex\":1,\"bodyAssetId\":\"CHR_PLAYER_ADULT\",\"stage\":\"Adult\",\"ageYears\":25,\"moneyCents\":1999}}");
	TArray<uint8> Bytes;
	FGenesisSaveStore::EncodeRaw(1, 5, V1Json, Bytes);

	FGenesisSaveBundle B;
	TestTrue(TEXT("Altes Schema ladbar"), FGenesisSaveStore::Decode(Bytes, B) == EGenesisSaveResult::Ok);
	TestEqual(TEXT("Auf aktuelles Schema gehoben"), B.SchemaVersion, FGenesisSaveBundle::CurrentSchemaVersion);
	TestEqual(TEXT("Weltzeit aus Jahr/Tag/Uhrzeit"), B.World.WorldDateTime, FDateTime(2030, 1, 11, 6, 30, 0));
	TestTrue(TEXT("Als geboren erkannt"), B.Life.bBorn);
	TestTrue(TEXT("Alter 25 Jahre erhalten"), FMath::IsNearlyEqual(FGenesisLifeCycle::GetAgeYears(B.Life, B.World.WorldDateTime), 25.0, 1e-6));
	TestEqual(TEXT("Uebrige Daten erhalten (Geld)"), B.Life.MoneyCents, int64(1999));
	TestEqual(TEXT("Uebrige Daten erhalten (Seed)"), B.World.WorldSeed, int64(42));

	// Wieder speichern ergibt Schema 2.
	TArray<uint8> NewBytes;
	FGenesisSaveStore::Encode(B, NewBytes);
	FGenesisSaveBundle Again;
	TestTrue(TEXT("Neu kodiert ladbar"), FGenesisSaveStore::Decode(NewBytes, Again) == EGenesisSaveResult::Ok);
	TestEqual(TEXT("Weltzeit nach erneutem Speichern"), Again.World.WorldDateTime, B.World.WorldDateTime);
	return true;
}

#endif
