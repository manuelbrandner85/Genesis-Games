#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Mission/GenesisWorkshopContract.h"
#include "Npc/GenesisNpcSchedule.h"
#include "Save/GenesisSaveStore.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "HAL/FileManager.h"
#include "Misc/Paths.h"

namespace
{
    constexpr EAutomationTestFlags GenesisTestFlags = EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::ProductFilter;
    using CT = FGenesisWorkshopContract;

    UGenesisWorldStateSubsystem* NewWorld()
    {
        UGenesisWorldStateSubsystem* WS = NewObject<UGenesisWorldStateSubsystem>(GetTransientPackage());
        FGenesisWorldState S;                       // Flussdorf start values (WorldSetup in the level)
        S.PlayerMoneyGE = 40;
        S.MarketStock.Add(CT::Part, 1);
        S.ObjectStates.Add(CT::Generator, TEXT("Defect"));
        WS->ResetState(S);
        WS->SetClock(1, 8, 30);
        return WS;
    }

    /** Where everyone stands per the daily schedule / appointments, assuming they have arrived. */
    FGenesisPresence Presence(const UGenesisWorldStateSubsystem& WS)
    {
        FGenesisPresence P;
        for (const TCHAR* Id : { TEXT("N01"), TEXT("N02"), TEXT("N03") }) {
            const FName Override = CT::NpcOverrideAnchor(WS, Id);
            if (!Override.IsNone()) {
                P.Add(Id, TEXT("R03"));
                continue;
            }
            const FGenesisScheduleEntry* E = FGenesisNpcSchedules::Find(Id, WS.GetMinuteOfDay());
            P.Add(Id, E && !E->bIndoorsPrivate ? E->Region : NAME_None);
        }
        return P;
    }

    FString Do(UGenesisWorldStateSubsystem* WS, FName Target, const TCHAR* Action)
    {
        const FGenesisReply R = CT::Execute(*WS, Target, Action, Presence(*WS));
        CT::Update(*WS, Presence(*WS));
        return R.Line.ToString();
    }

    void Wait(UGenesisWorldStateSubsystem* WS, int32 Minutes)
    {
        for (int32 M = 0; M < Minutes; M += 10) {   // NPCs react while time passes
            WS->AdvanceMinutes(10);
            CT::Update(*WS, Presence(*WS));
        }
    }

    int32 PaidCount(const UGenesisWorldStateSubsystem& WS)
    {
        return WS.GetState().Ledger.FilterByPredicate([](const FGenesisWorldEvent& E) { return E.ActionID == TEXT("Contract.Paid"); }).Num();
    }

    bool Offered(const UGenesisWorldStateSubsystem& WS, FName Target, const TCHAR* Action, bool* bEnabled = nullptr)
    {
        for (const FGenesisChoice& C : CT::Choices(WS, Target, Presence(WS))) {
            if (C.Action == Action) {
                if (bEnabled) *bEnabled = C.bEnabled;
                return true;
            }
        }
        return false;
    }

    // Happy path as action list: (target, action, minutes to wait afterwards)
    struct FStep { const TCHAR* Target; const TCHAR* Action; int32 WaitAfter; };
    const FStep HappyPath[] = {
        { TEXT("N02"), TEXT("N02.Ask"), 0 }, { TEXT("N02"), TEXT("N02.Accept60"), 40 },        // -> 09:10, N01 at work
        { TEXT("N01"), TEXT("N01.BorrowTool"), 0 },
        { TEXT("OBJ_GENERATOR_N02"), TEXT("Gen.InspectFilter"), 0 }, { TEXT("OBJ_GENERATOR_N02"), TEXT("Gen.InspectPlug"), 0 },
        { TEXT("N03"), TEXT("N03.BuyPlug"), 0 },
        { TEXT("OBJ_GENERATOR_N02"), TEXT("Gen.Repair"), 0 }, { TEXT("N01"), TEXT("N01.ReturnTool"), 0 },
        { TEXT("N02"), TEXT("N02.ReportDone"), 10 },
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisContractHappyPath, "Genesis.Flussdorf.Contract.RepairAndPayOnce", GenesisTestFlags)
bool FGenesisContractHappyPath::RunTest(const FString&)
{
    UGenesisWorldStateSubsystem* WS = NewWorld();
    bool bRepairEnabled = true;
    Offered(*WS, CT::Generator, TEXT("Gen.Repair"), &bRepairEnabled);
    TestFalse(TEXT("Cannot repair before an agreement"), bRepairEnabled);
    for (const FStep& S : HappyPath) {
        const FString Line = Do(WS, S.Target, S.Action);
        AddInfo(FString::Printf(TEXT("%s %s -> %s | %s"), *WS->GetClockText(), S.Action, *CT::State(*WS), *Line));
        Wait(WS, S.WaitAfter);
    }
    TestEqual(TEXT("Completed"), CT::State(*WS), FString(TEXT("Completed")));
    TestEqual(TEXT("Money: 40 - 18 + 60"), WS->GetState().PlayerMoneyGE, 82);
    TestEqual(TEXT("Paid exactly once"), PaidCount(*WS), 1);
    TestEqual(TEXT("Generator repaired"), WS->GetObjectState(CT::Generator), FString(TEXT("Repaired")));
    TestEqual(TEXT("Tool back with N01"), WS->GetObjectState(CT::Tool), FString(TEXT("N01")));
    TestEqual(TEXT("Market stock used"), WS->GetState().MarketStock.FindRef(CT::Part), 0);
    TestTrue(TEXT("Customer knows the repair from her own inspection"), WS->NpcKnows(TEXT("N02"), WS->FindLastEvent(TEXT("Repair.Done"))->EventID));
    // Repeating the final steps changes nothing.
    Do(WS, TEXT("N02"), TEXT("N02.ReportDone"));
    CT::Update(*WS, Presence(*WS));
    TestEqual(TEXT("Still paid once"), PaidCount(*WS), 1);
    TestEqual(TEXT("Money unchanged"), WS->GetState().PlayerMoneyGE, 82);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisContractSaveEveryStep, "Genesis.Flussdorf.Contract.SaveLoadEveryStep", GenesisTestFlags)
bool FGenesisContractSaveEveryStep::RunTest(const FString&)
{
    const FString Path = FPaths::ProjectSavedDir() / TEXT("Automation/Genesis/contract_steps.genesis.json");
    for (const TCHAR* Ext : { TEXT(""), TEXT(".bak"), TEXT(".tmp"), TEXT(".corrupt") }) {
        IFileManager::Get().Delete(*(Path + Ext));
    }
    UGenesisWorldStateSubsystem* WS = NewWorld();
    int32 Step = 0;
    for (const FStep& S : HappyPath) {
        Do(WS, S.Target, S.Action);
        Wait(WS, S.WaitAfter);
        // Save, throw the running world away, load into a fresh one and continue from there.
        FString Err;
        TestTrue(FString::Printf(TEXT("Save after %s"), S.Action), FGenesisSaveStore::Save(Path, WS->GetState(), Err));
        FGenesisWorldState Loaded;
        TestTrue(FString::Printf(TEXT("Load after %s"), S.Action), FGenesisSaveStore::Load(Path, Loaded, Err));
        WS = NewObject<UGenesisWorldStateSubsystem>(GetTransientPackage());
        WS->ResetState(Loaded);
        // Re-running the same step after loading (player presses again) must not duplicate it.
        CT::Execute(*WS, S.Target, S.Action, Presence(*WS));
        CT::Update(*WS, Presence(*WS));
        ++Step;
    }
    TestEqual(TEXT("Completed after reload at every step"), CT::State(*WS), FString(TEXT("Completed")));
    TestEqual(TEXT("Paid once"), PaidCount(*WS), 1);
    TestEqual(TEXT("Money 82"), WS->GetState().PlayerMoneyGE, 82);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisContractOtherWays, "Genesis.Flussdorf.Contract.ReferDeclineWithdraw", GenesisTestFlags)
bool FGenesisContractOtherWays::RunTest(const FString&)
{
    {   // Refer to the workshop: N02 goes there when it opens, N01 takes the order and repairs it.
        UGenesisWorldStateSubsystem* WS = NewWorld();
        Do(WS, TEXT("N02"), TEXT("N02.Ask"));
        Do(WS, TEXT("N02"), TEXT("N02.Refer"));
        TestEqual(TEXT("N02 heads to the workshop only once it opens"), CT::NpcOverrideAnchor(*WS, TEXT("N02")), FName());
        Wait(WS, 40);                                              // 09:10: N01 at work, N02 goes there
        TestEqual(TEXT("N01 took the order"), CT::State(*WS), FString(TEXT("WithN01")));
        Wait(WS, 70);
        TestEqual(TEXT("N01 repaired it"), CT::State(*WS), FString(TEXT("CompletedByN01")));
        TestEqual(TEXT("Generator repaired by N01"), WS->GetObjectState(CT::Generator), FString(TEXT("Repaired")));
        TestEqual(TEXT("Player money untouched"), WS->GetState().PlayerMoneyGE, 40);
        TestEqual(TEXT("N01 bought the market's part"), WS->GetState().MarketStock.FindRef(CT::Part), 0);
    }
    {   // Price too high: N02 refuses 90 GE, the talk goes on; then the player declines.
        UGenesisWorldStateSubsystem* WS = NewWorld();
        Do(WS, TEXT("N02"), TEXT("N02.Ask"));
        const FString Line = Do(WS, TEXT("N02"), TEXT("N02.Quote90"));
        TestEqual(TEXT("Price rejected"), CT::State(*WS), FString(TEXT("PriceRejected")));
        TestTrue(TEXT("She says why"), Line.Contains(TEXT("zu teuer")));
        TestTrue(TEXT("60 GE still possible"), Offered(*WS, TEXT("N02"), TEXT("N02.Accept60")));
        TestFalse(TEXT("90 GE not offered twice"), Offered(*WS, TEXT("N02"), TEXT("N02.Quote90")));
        Do(WS, TEXT("N02"), TEXT("N02.Decline"));
        TestTrue(TEXT("Declined is an end"), CT::IsTerminal(CT::State(*WS)));
    }
    {   // Accepted but left undone: withdrawn at the end of day 2, reservation released.
        UGenesisWorldStateSubsystem* WS = NewWorld();
        Do(WS, TEXT("N02"), TEXT("N02.Ask"));
        Do(WS, TEXT("N02"), TEXT("N02.Accept60"));
        TestEqual(TEXT("Part reserved for the player"), WS->GetObjectState(CT::Reservation), FString(TEXT("Player")));
        Wait(WS, 2 * 24 * 60);
        TestEqual(TEXT("Withdrawn"), CT::State(*WS), FString(TEXT("Withdrawn")));
        TestEqual(TEXT("Reservation released"), WS->GetObjectState(CT::Reservation), FString(TEXT("None")));
        TestEqual(TEXT("No payment"), PaidCount(*WS), 0);
    }
    {   // Limits from the source: no sale without money, closed shop, absent people.
        UGenesisWorldStateSubsystem* WS = NewWorld();
        WS->GetMutableState().PlayerMoneyGE = 10;
        bool bEnabled = true;
        TestTrue(TEXT("Buy shown"), Offered(*WS, TEXT("N03"), TEXT("N03.BuyPlug"), &bEnabled));
        TestFalse(TEXT("but not possible with 10 GE"), bEnabled);
        CT::Execute(*WS, TEXT("N03"), TEXT("N03.BuyPlug"), Presence(*WS));
        TestEqual(TEXT("Nothing bought"), WS->GetItemCount(CT::Part), 0);
        TestEqual(TEXT("Nothing paid"), WS->GetState().PlayerMoneyGE, 10);
        WS->SetClock(1, 19, 0);
        TestEqual(TEXT("Shop closed at 19:00: no choices at N03"), CT::Choices(*WS, TEXT("N03"), Presence(*WS)).Num(), 0);
        TestEqual(TEXT("N02 at home: not reachable"), CT::Choices(*WS, TEXT("N02"), Presence(*WS)).Num(), 0);
        TestEqual(TEXT("N01 off work: no tool"), CT::Choices(*WS, TEXT("N01"), Presence(*WS)).Num(), 0);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisContractNoSoftlock, "Genesis.Flussdorf.Contract.NoSoftlockExhaustive", GenesisTestFlags)
bool FGenesisContractNoSoftlock::RunTest(const FString&)
{
    // Explore every combination of choices (all targets) and waiting (+1 h) for three days.
    struct FNode { FGenesisWorldState State; TArray<int32> Next; bool bExpanded = false; };
    TArray<FNode> Nodes;
    TMap<FString, int32> Index;
    const FName Targets[] = { TEXT("N01"), TEXT("N02"), TEXT("N03"), CT::Generator };
    auto Signature = [](const UGenesisWorldStateSubsystem& WS) {
        const FGenesisWorldState& S = WS.GetState();
        TArray<FString> Parts;
        for (const TPair<FName, FString>& KV : S.ObjectStates) Parts.Add(KV.Key.ToString() + TEXT("=") + KV.Value);
        Parts.Sort();
        return FString::Printf(TEXT("%lld|%d|%d|%d|%d|%d|%s"), S.WorldMinute / 60, S.PlayerMoneyGE, WS.GetItemCount(CT::Part),
            S.MarketStock.FindRef(CT::Part), WS.WasApplied(TEXT("fact:plug_worn")), WS.WasApplied(TEXT("fact:filter_ok")), *FString::Join(Parts, TEXT(";")));
    };
    auto AddNode = [&](UGenesisWorldStateSubsystem* WS) {
        const FString Sig = Signature(*WS);
        if (const int32* Existing = Index.Find(Sig)) return *Existing;
        const int32 I = Nodes.Add(FNode{ WS->GetState(), {}, false });
        Index.Add(Sig, I);
        return I;
    };
    UGenesisWorldStateSubsystem* Start = NewWorld();
    AddNode(Start);
    int32 MaxPaid = 0, MaxMoney = 0;
    for (int32 I = 0; I < Nodes.Num() && I < 60000; ++I) {
        UGenesisWorldStateSubsystem* Base = NewObject<UGenesisWorldStateSubsystem>(GetTransientPackage());
        Base->ResetState(Nodes[I].State);
        MaxPaid = FMath::Max(MaxPaid, PaidCount(*Base));
        MaxMoney = FMath::Max(MaxMoney, Base->GetState().PlayerMoneyGE);
        Nodes[I].bExpanded = true;
        if (CT::IsTerminal(CT::State(*Base)) || Base->GetDay() > 3) {
            continue;
        }
        TArray<TPair<FName, FName>> Moves;
        for (FName T : Targets) {
            for (const FGenesisChoice& C : CT::Choices(*Base, T, Presence(*Base))) {
                if (C.bEnabled) Moves.Add({ T, C.Action });
            }
        }
        Moves.Add({ NAME_None, TEXT("Wait1h") });
        for (const TPair<FName, FName>& M : Moves) {
            UGenesisWorldStateSubsystem* W = NewObject<UGenesisWorldStateSubsystem>(GetTransientPackage());
            W->ResetState(Nodes[I].State);
            if (M.Key.IsNone()) {
                Wait(W, 60);
            } else {
                CT::Execute(*W, M.Key, M.Value, Presence(*W));
                CT::Update(*W, Presence(*W));
            }
            const int32 J = AddNode(W);
            if (J != I) Nodes[I].Next.AddUnique(J);
        }
    }
    // Backwards: which nodes can still reach an end?
    TArray<bool> CanEnd;
    CanEnd.Init(false, Nodes.Num());
    for (int32 I = 0; I < Nodes.Num(); ++I) {
        UGenesisWorldStateSubsystem* W = NewObject<UGenesisWorldStateSubsystem>(GetTransientPackage());
        W->ResetState(Nodes[I].State);
        CanEnd[I] = CT::IsTerminal(CT::State(*W)) || CT::State(*W) == TEXT("None");   // never asked = no obligation
    }
    for (bool bChanged = true; bChanged;) {
        bChanged = false;
        for (int32 I = 0; I < Nodes.Num(); ++I) {
            if (!CanEnd[I] && Nodes[I].Next.ContainsByPredicate([&](int32 J) { return CanEnd[J]; })) {
                CanEnd[I] = bChanged = true;
            }
        }
    }
    int32 Stuck = 0, Expanded = 0;
    for (int32 I = 0; I < Nodes.Num(); ++I) {
        if (Nodes[I].bExpanded) {
            ++Expanded;
            if (!CanEnd[I]) {
                ++Stuck;
                if (Stuck <= 5) {
                    UGenesisWorldStateSubsystem* W = NewObject<UGenesisWorldStateSubsystem>(GetTransientPackage());
                    W->ResetState(Nodes[I].State);
                    AddError(FString::Printf(TEXT("Stuck: %s %s"), *W->GetClockText(), *CT::State(*W)));
                }
            }
        }
    }
    AddInfo(FString::Printf(TEXT("Explored %d states (%d expanded), max paid %d, max money %d GE"), Nodes.Num(), Expanded, MaxPaid, MaxMoney));
    TestEqual(TEXT("No state without a way to an end"), Stuck, 0);
    TestTrue(TEXT("Never paid twice"), MaxPaid <= 1);
    TestTrue(TEXT("Money never above 40 + 60"), MaxMoney <= 100);
    TestTrue(TEXT("Search was not cut off"), Nodes.Num() < 60000);
    return true;
}
#endif
