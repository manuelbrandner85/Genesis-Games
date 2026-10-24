#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Tests/GenesisTestCommon.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Save/GenesisSaveStore.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

namespace
{

    UGenesisWorldStateSubsystem* NewState()
    {
        // Subsystem logic without a world: the object is only used as a state container here.
        return NewObject<UGenesisWorldStateSubsystem>(GetTransientPackage());
    }

    FString TestSavePath(const TCHAR* Name)
    {
        const FString P = FPaths::ProjectSavedDir() / TEXT("Automation/Genesis") / Name;
        IFileManager::Get().Delete(*P);
        IFileManager::Get().Delete(*(P + TEXT(".bak")));
        IFileManager::Get().Delete(*(P + TEXT(".tmp")));
        IFileManager::Get().Delete(*(P + TEXT(".corrupt")));
        return P;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisClockTest, "Genesis.World.Clock", GenesisTestFlags)
bool FGenesisClockTest::RunTest(const FString&)
{
    UGenesisWorldStateSubsystem* S = NewState();
    S->SetClock(1, 8, 30);
    TestEqual(TEXT("Start text"), S->GetClockText(), FString(TEXT("Tag 1, 08:30")));
    S->Tick(60.f);                          // 1 real minute = 10 game minutes
    TestEqual(TEXT("After 60 s"), S->GetClockText(), FString(TEXT("Tag 1, 08:40")));
    for (int32 I = 0; I < 600; ++I) {
        S->Tick(0.1f);                      // 60 s in small steps: no drift from rounding
    }
    TestEqual(TEXT("After 600 x 0.1 s"), S->GetClockText(), FString(TEXT("Tag 1, 08:50")));
    S->SetPaused(true);
    S->Tick(600.f);
    TestEqual(TEXT("Paused"), S->GetClockText(), FString(TEXT("Tag 1, 08:50")));
    S->AdvanceMinutes(16 * 60);
    TestEqual(TEXT("Day rollover"), S->GetClockText(), FString(TEXT("Tag 2, 00:50")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisLedgerTest, "Genesis.World.LedgerIdempotent", GenesisTestFlags)
bool FGenesisLedgerTest::RunTest(const FString&)
{
    UGenesisWorldStateSubsystem* S = NewState();
    S->GetMutableState().PlayerMoneyGE = 40;
    TestTrue(TEXT("Pay 18"), S->TryPay(18, TEXT("Market.Buy"), TEXT("ITEM_SPARK_PLUG"), TEXT("buy_plug_1")));
    TestTrue(TEXT("Same purchase confirmed twice"), S->TryPay(18, TEXT("Market.Buy"), TEXT("ITEM_SPARK_PLUG"), TEXT("buy_plug_1")));
    TestEqual(TEXT("Charged once"), S->GetState().PlayerMoneyGE, 22);
    TestFalse(TEXT("Cannot pay more than owned"), S->TryPay(30, TEXT("Market.Buy"), TEXT("X"), TEXT("buy_x")));
    TestEqual(TEXT("Failed payment changes nothing"), S->GetState().PlayerMoneyGE, 22);
    S->Earn(60, TEXT("Contract.Paid"), TEXT("N02"), TEXT("CT_GENERATOR_N02"), TEXT("pay_ct_generator"));
    S->Earn(60, TEXT("Contract.Paid"), TEXT("N02"), TEXT("CT_GENERATOR_N02"), TEXT("pay_ct_generator"));
    TestEqual(TEXT("Reward exactly once"), S->GetState().PlayerMoneyGE, 82);
    const FGenesisWorldEvent* E = S->ApplyEvent(TEXT("Contract.Accepted"), TEXT("Player"), TEXT("CT_X"), TEXT("Accepted"));
    TestNotNull(TEXT("Event recorded"), E);
    TestEqual(TEXT("Before state recorded"), S->GetState().Ledger.Last().BeforeState, FString());
    S->ApplyEvent(TEXT("Contract.Done"), TEXT("Player"), TEXT("CT_X"), TEXT("Done"));
    TestEqual(TEXT("Before = previous after"), S->GetState().Ledger.Last().BeforeState, FString(TEXT("Accepted")));
    S->NpcObserve(TEXT("N02"), E ? E->EventID : NAME_None);
    TestTrue(TEXT("N02 knows what it observed"), S->NpcKnows(TEXT("N02"), S->GetState().Ledger[S->GetState().Ledger.Num() - 2].EventID));
    TestFalse(TEXT("N03 does not know it"), S->NpcKnows(TEXT("N03"), S->GetState().Ledger[S->GetState().Ledger.Num() - 2].EventID));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSaveRoundtripTest, "Genesis.Save.RoundtripAndRecovery", GenesisTestFlags)
bool FGenesisSaveRoundtripTest::RunTest(const FString&)
{
    UGenesisWorldStateSubsystem* S = NewState();
    S->SetClock(1, 10, 15);
    S->GetMutableState().PlayerMoneyGE = 40;
    S->GetMutableState().MarketStock.Add(TEXT("ITEM_SPARK_PLUG"), 1);
    S->TryPay(18, TEXT("Market.Buy"), TEXT("ITEM_SPARK_PLUG"), TEXT("buy_plug_1"));
    S->NpcHear(TEXT("N01"), TEXT("CLAIM_GENERATOR_BROKEN"));
    S->GetMutableState().PlayerLocation = FVector(123.5, -45.25, 98.0);
    S->GetMutableState().bHasPlayerTransform = true;
    const FString Path = TestSavePath(TEXT("roundtrip.genesis.json"));
    FString Err;
    TestTrue(TEXT("Save"), FGenesisSaveStore::Save(Path, S->GetState(), Err));
    FGenesisWorldState L;
    TestTrue(TEXT("Load ") + Err, FGenesisSaveStore::Load(Path, L, Err));
    TestEqual(TEXT("Clock"), L.WorldMinute, S->GetState().WorldMinute);
    TestEqual(TEXT("Money"), L.PlayerMoneyGE, 22);
    TestEqual(TEXT("Stock"), L.MarketStock.FindRef(TEXT("ITEM_SPARK_PLUG")), 1);
    TestEqual(TEXT("Ledger"), L.Ledger.Num(), 1);
    TestEqual(TEXT("Idempotency key survives"), L.Ledger[0].IdempotencyKey, FName(TEXT("buy_plug_1")));
    TestEqual(TEXT("NPC hearsay kept apart"), L.NpcMemories.Num() > 0 ? L.NpcMemories[0].HeardClaims.Num() : 0, 1);
    TestTrue(TEXT("Player location exact"), L.PlayerLocation.Equals(FVector(123.5, -45.25, 98.0), 0.001));

    // Second save makes the first one the backup; then the main file gets corrupted.
    S->AdvanceMinutes(30);
    TestTrue(TEXT("Second save"), FGenesisSaveStore::Save(Path, S->GetState(), Err));
    FString Text;
    FFileHelper::LoadFileToString(Text, *Path);
    FFileHelper::SaveStringToFile(Text.Left(Text.Len() / 2), *Path);
    bool bBackup = false;
    AddExpectedMessage(TEXT("loaded backup"), EAutomationExpectedErrorFlags::Contains, 1);
    TestTrue(TEXT("Load falls back to backup"), FGenesisSaveStore::Load(Path, L, Err, &bBackup));
    TestTrue(TEXT("Backup used"), bBackup);
    TestEqual(TEXT("Backup holds the previous complete state"), L.WorldMinute, int64(10 * 60 + 15));

    // Saving over a damaged main file keeps the good backup (the damaged file goes to .corrupt).
    TestTrue(TEXT("Third save over damaged main"), FGenesisSaveStore::Save(Path, S->GetState(), Err));
    TestTrue(TEXT("Damaged file kept aside"), IFileManager::Get().FileExists(*(Path + TEXT(".corrupt"))));
    FGenesisWorldState BakState;
    TestTrue(TEXT("Backup still the good first state"), FGenesisSaveStore::Load(Path + TEXT(".bak"), BakState, Err) && BakState.WorldMinute == int64(10 * 60 + 15));

    // A tampered value is caught by the checksum.
    FFileHelper::LoadFileToString(Text, *Path);
    FFileHelper::SaveStringToFile(Text.Replace(TEXT("\"playerMoneyGE\":22"), TEXT("\"playerMoneyGE\":9999")), *Path);
    AddExpectedMessage(TEXT("loaded backup"), EAutomationExpectedErrorFlags::Contains, 1);
    TestTrue(TEXT("Tampered main -> backup"), FGenesisSaveStore::Load(Path, L, Err, &bBackup) && bBackup);
    TestEqual(TEXT("Money not tampered"), L.PlayerMoneyGE, 22);

    // A half-written temp file from a crash does not affect loading.
    FFileHelper::SaveStringToFile(TEXT("{\"schema\":1,\"sha1\":\"x\",\"sta"), *(Path + TEXT(".tmp")));
    TestTrue(TEXT("Stale temp ignored on next save"), FGenesisSaveStore::Save(Path, S->GetState(), Err));
    TestTrue(TEXT("Load after stale temp"), FGenesisSaveStore::Load(Path, L, Err, &bBackup) && !bBackup);

    // A save from a newer build is refused instead of being misread.
    FFileHelper::LoadFileToString(Text, *Path);
    const FString Future = Text.Replace(TEXT("{\"schema\":1,"), TEXT("{\"schema\":99,"));
    const FString FuturePath = TestSavePath(TEXT("future.genesis.json"));
    FFileHelper::SaveStringToFile(Future, *FuturePath);
    TestFalse(TEXT("Future schema refused"), FGenesisSaveStore::Load(FuturePath, L, Err));
    TestTrue(TEXT("Reason names the schema"), Err.Contains(TEXT("schema 99")));
    return true;
}
#endif
