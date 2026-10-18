#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Save/GenesisSaveStore.h"

namespace GenesisSaveTests
{
	static const FString Slot = TEXT("TestSlot");

	static FString MakeTempDir()
	{
		return FPaths::ProjectIntermediateDir() / TEXT("GenesisSaveTests") / FGuid::NewGuid().ToString();
	}

	static FGenesisSaveBundle MakeBundle(int32 Marker)
	{
		FGenesisSaveBundle B;
		B.Soul.SoulId = FGuid::NewGuid();
		B.Soul.LivesLived = Marker;
		B.Soul.UnlockedRevealGuards.Add(TEXT("TEST_GUARD"));
		B.World.WorldYear = 2026 + Marker;
		B.World.EventFlags.Add(TEXT("EV_TEST"), Marker);
		B.Life.LifeIndex = Marker;
		B.Life.BodyAssetId = TEXT("CHR_TEST_BODY");
		B.Life.Stage = EGenesisLifeStage::Adult;
		B.Life.AgeYears = 30.5f;
		B.Life.Inventory.Add(TEXT("ITEM_TEST"), 3);
		B.Life.MoneyCents = 123456789012LL;
		FGenesisMemoryRecord M;
		M.MemoryId = FName(TEXT("MEM_UMLAUT_ÄÖÜß"));
		M.WorldYear = 2030;
		B.Life.Memories.Add(M);
		return B;
	}

	static void Cleanup(const FString& Dir)
	{
		IFileManager::Get().DeleteDirectory(*Dir, false, true);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSaveRoundTripTest, "Genesis.Save.RoundTrip",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSaveRoundTripTest::RunTest(const FString&)
{
	using namespace GenesisSaveTests;
	const FString Dir = MakeTempDir();
	FGenesisSaveStore Store(Dir);

	FGenesisSaveBundle B = MakeBundle(7);
	TestEqual(TEXT("Erstes Speichern"), Store.Save(Slot, B), EGenesisSaveResult::Ok);
	TestEqual(TEXT("Sequenz 1"), B.Sequence, int64(1));
	TestEqual(TEXT("Zweites Speichern"), Store.Save(Slot, B), EGenesisSaveResult::Ok);
	TestEqual(TEXT("Sequenz 2"), B.Sequence, int64(2));

	FGenesisSaveBundle L;
	bool bBackup = true;
	TestEqual(TEXT("Laden"), Store.Load(Slot, L, &bBackup), EGenesisSaveResult::Ok);
	TestFalse(TEXT("Hauptdatei benutzt"), bBackup);
	TestEqual(TEXT("Sequenz"), L.Sequence, int64(2));
	TestEqual(TEXT("SoulId"), L.Soul.SoulId, B.Soul.SoulId);
	TestEqual(TEXT("WorldYear"), L.World.WorldYear, 2033);
	TestEqual(TEXT("EventFlag"), L.World.EventFlags.FindRef(TEXT("EV_TEST")), 7);
	TestTrue(TEXT("Stage"), L.Life.Stage == EGenesisLifeStage::Adult);
	TestEqual(TEXT("Inventar"), L.Life.Inventory.FindRef(TEXT("ITEM_TEST")), 3);
	TestEqual(TEXT("Geld int64"), L.Life.MoneyCents, int64(123456789012LL));
	TestTrue(TEXT("Erinnerung mit Umlaut"), L.Life.Memories.Num() == 1 && L.Life.Memories[0].MemoryId == B.Life.Memories[0].MemoryId);
	TestTrue(TEXT("Guard"), L.Soul.UnlockedRevealGuards.Contains(TEXT("TEST_GUARD")));
	TestTrue(TEXT("Sicherung angelegt"), IFileManager::Get().FileExists(*Store.GetBackupPath(Slot)));

	Cleanup(Dir);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSaveAbortAfterTempTest, "Genesis.Save.AbortAfterTempWriteKeepsOldState",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSaveAbortAfterTempTest::RunTest(const FString&)
{
	using namespace GenesisSaveTests;
	const FString Dir = MakeTempDir();
	FGenesisSaveStore Store(Dir);

	FGenesisSaveBundle B = MakeBundle(1);
	TestTrue(TEXT("Grundstand"), Store.Save(Slot, B) == EGenesisSaveResult::Ok);

	FGenesisSaveBundle Newer = B;
	Newer.Life.LifeIndex = 99;
	Store.SetFaultForTesting(EGenesisSaveFault::AbortAfterTempWrite);
	TestTrue(TEXT("Abbruch meldet Fehler"), Store.Save(Slot, Newer) != EGenesisSaveResult::Ok);
	TestTrue(TEXT("Temp-Datei liegt herum"), IFileManager::Get().FileExists(*Store.GetTempFilePath(Slot)));

	FGenesisSaveBundle L;
	TestTrue(TEXT("Laden"), Store.Load(Slot, L) == EGenesisSaveResult::Ok);
	TestEqual(TEXT("Alter Stand"), L.Sequence, int64(1));
	TestEqual(TEXT("Altes Leben"), L.Life.LifeIndex, 1);

	// Naechstes normales Speichern ueberschreibt die liegengebliebene Temp-Datei.
	Store.SetFaultForTesting(EGenesisSaveFault::None);
	TestTrue(TEXT("Erholung"), Store.Save(Slot, Newer) == EGenesisSaveResult::Ok);
	TestTrue(TEXT("Laden nach Erholung"), Store.Load(Slot, L) == EGenesisSaveResult::Ok);
	TestEqual(TEXT("Neuer Stand"), L.Life.LifeIndex, 99);

	Cleanup(Dir);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSaveTruncatedTempTest, "Genesis.Save.TruncatedTempWriteKeepsOldState",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSaveTruncatedTempTest::RunTest(const FString&)
{
	using namespace GenesisSaveTests;
	const FString Dir = MakeTempDir();
	FGenesisSaveStore Store(Dir);

	FGenesisSaveBundle B = MakeBundle(2);
	TestTrue(TEXT("Grundstand"), Store.Save(Slot, B) == EGenesisSaveResult::Ok);

	Store.SetFaultForTesting(EGenesisSaveFault::TruncatedTempWrite);
	FGenesisSaveBundle Newer = B;
	TestTrue(TEXT("Abbruch meldet Fehler"), Store.Save(Slot, Newer) != EGenesisSaveResult::Ok);

	FGenesisSaveBundle Garbage;
	TestTrue(TEXT("Halbe Temp-Datei ist als defekt erkannt"), FGenesisSaveStore::ReadFile(Store.GetTempFilePath(Slot), Garbage) == EGenesisSaveResult::Corrupt);

	FGenesisSaveBundle L;
	TestTrue(TEXT("Laden"), Store.Load(Slot, L) == EGenesisSaveResult::Ok);
	TestEqual(TEXT("Alter Stand"), L.Sequence, int64(1));

	Cleanup(Dir);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSaveCorruptMainTest, "Genesis.Save.CorruptMainFallsBackToBackup",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSaveCorruptMainTest::RunTest(const FString&)
{
	using namespace GenesisSaveTests;
	const FString Dir = MakeTempDir();
	FGenesisSaveStore Store(Dir);

	FGenesisSaveBundle B = MakeBundle(3);
	Store.Save(Slot, B);
	Store.Save(Slot, B);

	// Ein Byte in den Nutzdaten der Hauptdatei kippen.
	TArray<uint8> Bytes;
	FFileHelper::LoadFileToArray(Bytes, *Store.GetMainPath(Slot));
	Bytes.Last(10) ^= 0x20;
	FFileHelper::SaveArrayToFile(Bytes, *Store.GetMainPath(Slot));

	FGenesisSaveBundle L;
	bool bBackup = false;
	TestTrue(TEXT("Laden"), Store.Load(Slot, L, &bBackup) == EGenesisSaveResult::Ok);
	TestTrue(TEXT("Sicherung benutzt"), bBackup);
	TestEqual(TEXT("Vorheriger Stand"), L.Sequence, int64(1));

	// Ohne Sicherung muss der Defekt gemeldet werden, nicht stillschweigend geladen.
	IFileManager::Get().Delete(*Store.GetBackupPath(Slot));
	TestTrue(TEXT("Defekt erkannt"), Store.Load(Slot, L) == EGenesisSaveResult::Corrupt);

	Cleanup(Dir);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSaveFirstAbortTest, "Genesis.Save.AbortOnFirstSaveLeavesNoSave",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSaveFirstAbortTest::RunTest(const FString&)
{
	using namespace GenesisSaveTests;
	const FString Dir = MakeTempDir();
	FGenesisSaveStore Store(Dir);
	Store.SetFaultForTesting(EGenesisSaveFault::AbortAfterTempWrite);

	FGenesisSaveBundle B = MakeBundle(4);
	Store.Save(Slot, B);

	FGenesisSaveBundle L;
	TestTrue(TEXT("Kein Spielstand"), Store.Load(Slot, L) == EGenesisSaveResult::NotFound);

	Cleanup(Dir);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSaveSchemaTest, "Genesis.Save.FutureSchemaRejected",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSaveSchemaTest::RunTest(const FString&)
{
	using namespace GenesisSaveTests;
	FGenesisSaveBundle B = MakeBundle(5);
	B.SchemaVersion = FGenesisSaveBundle::CurrentSchemaVersion + 1;
	TArray<uint8> Bytes;
	FGenesisSaveStore::Encode(B, Bytes);

	FGenesisSaveBundle L;
	TestTrue(TEXT("Zukuenftiges Schema"), FGenesisSaveStore::Decode(Bytes, L) == EGenesisSaveResult::SchemaUnsupported);
	return true;
}

#endif
