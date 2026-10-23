#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Npc/GenesisNpc.h"
#include "Npc/GenesisNpcController.h"
#include "Npc/GenesisNpcSchedule.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Editor.h"
#include "EngineUtils.h"
#include "Engine/TriggerBox.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"

namespace
{
    const TCHAR* FlussdorfMap = TEXT("/Game/Genesis/Flussdorf/Maps/L_Flussdorf_G6");

    AGenesisNpc* FindNpc(UWorld* W, FName Id)
    {
        for (TActorIterator<AGenesisNpc> It(W); It; ++It) {
            if (It->NpcID == Id) {
                return *It;
            }
        }
        return nullptr;
    }

    bool InRegion(UWorld* W, const FVector& P, FName Region)
    {
        for (TActorIterator<ATriggerBox> It(W); It; ++It) {
            if (It->ActorHasTag(Region)) {
                FVector Origin, Extent;
                It->GetActorBounds(false, Origin, Extent);
                return FBox(Origin - Extent, Origin + Extent).IsInsideOrOn(P);
            }
        }
        return false;
    }

    /** Sets the clock to each checkpoint, waits until everyone has walked there, then checks. */
    class FScheduleWalk : public IAutomationLatentCommand
    {
    public:
        explicit FScheduleWalk(FAutomationTestBase* InTest) : Test(InTest) {}

        virtual bool Update() override
        {
            UWorld* W = GEditor ? GEditor->PlayWorld.Get() : nullptr;
            UGenesisWorldStateSubsystem* WS = W ? W->GetSubsystem<UGenesisWorldStateSubsystem>() : nullptr;
            if (!WS) {
                Test->AddError(TEXT("No PIE world / world state"));
                return true;
            }
            static const int32 Checkpoints[] = { 8 * 60 + 30, 10 * 60, 12 * 60 + 30, 18 * 60 + 30 };
            static const FName Ids[] = { TEXT("N01"), TEXT("N02"), TEXT("N03") };
            const double Now = FPlatformTime::Seconds();
            if (Index >= UE_ARRAY_COUNT(Checkpoints)) {
                return true;
            }
            if (PhaseStart < 0.0) {
                WS->SetClock(1, Checkpoints[Index] / 60, Checkpoints[Index] % 60);
                WS->SetPaused(true);                      // hold the time while they walk there
                PhaseStart = Now;
                return false;
            }
            bool bAllArrived = true;
            for (FName Id : Ids) {
                AGenesisNpc* N = FindNpc(W, Id);
                const AGenesisNpcController* C = N ? Cast<AGenesisNpcController>(N->GetController()) : nullptr;
                const FGenesisScheduleEntry* Due = FGenesisNpcSchedules::Find(Id, Checkpoints[Index]);
                // arrived at THIS checkpoint's anchor, not still flagged from the previous one
                bAllArrived &= C && Due && C->GetCurrentAnchor() == Due->Anchor && C->HasArrived();
            }
            if (!bAllArrived && Now - PhaseStart < 120.0) {
                return false;
            }
            const FString Clock = WS->GetClockText();
            Test->AddInfo(FString::Printf(TEXT("%s: arrived after %.1f s real time"), *Clock, Now - PhaseStart));
            for (FName Id : Ids) {
                AGenesisNpc* N = FindNpc(W, Id);
                const FGenesisScheduleEntry* E = FGenesisNpcSchedules::Find(Id, Checkpoints[Index]);
                if (!Test->TestNotNull(*FString::Printf(TEXT("%s exists"), *Id.ToString()), N) || !E) {
                    continue;
                }
                const FVector P = N->GetActorLocation();
                Test->TestTrue(*FString::Printf(TEXT("%s %s in %s"), *Clock, *Id.ToString(), *E->Region.ToString()), InRegion(W, P, E->Region));
                Test->TestEqual(*FString::Printf(TEXT("%s %s inside private house = %d"), *Clock, *Id.ToString(), E->bIndoorsPrivate),
                    N->IsInsidePrivate(), E->bIndoorsPrivate);
            }
            if (Index == 0) {
                // Perception: an event at the market is known to the people at the market only.
                const FVector Market(2950.f, -350.f, 100.f);
                const FGenesisWorldEvent* Ev = WS->ApplyEvent(TEXT("Test.MarketNoise"), TEXT("Player"), NAME_None, TEXT("x"), NAME_None, {}, &Market);
                const FName EvId = Ev ? Ev->EventID : NAME_None;
                Test->TestTrue(TEXT("N03 at the counter perceives the market event"), WS->NpcKnows(TEXT("N03"), EvId));
                Test->TestTrue(TEXT("N02 at the market perceives it"), WS->NpcKnows(TEXT("N02"), EvId));
                Test->TestFalse(TEXT("N01 at home (inside) does not"), WS->NpcKnows(TEXT("N01"), EvId));
            }
            ++Index;
            PhaseStart = -1.0;
            return Index >= UE_ARRAY_COUNT(Checkpoints);
        }

    private:
        FAutomationTestBase* Test;
        int32 Index = 0;
        double PhaseStart = -1.0;
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisFlussdorfScheduleTest, "Genesis.Flussdorf.DailySchedule",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisFlussdorfScheduleTest::RunTest(const FString&)
{
    AutomationOpenMap(FlussdorfMap);
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(3.f));
    ADD_LATENT_AUTOMATION_COMMAND(FScheduleWalk(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}
#endif
