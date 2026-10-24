#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Interaction/GenesisInteractableProp.h"
#include "Mission/GenesisWorkshopContract.h"
#include "Npc/GenesisNpc.h"
#include "Player/GenesisPlayerController.h"
#include "World/GenesisFlussdorfDirector.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Editor.h"
#include "EngineUtils.h"
#include "HighResScreenshot.h"
#include "Kismet/GameplayStatics.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"

namespace GenesisMissionPIE
{
    /**
     * Plays the workshop chain in the real level with the real player controller, conversations,
     * residents walking on the nav mesh and the village director. The test only moves the player
     * next to whoever it talks to (instead of steering the walk) and sets the clock at 09:05 so the
     * workshop is open; saving and loading happens in the middle.
     */
    class FPlay : public IAutomationLatentCommand
    {
    public:
        explicit FPlay(FAutomationTestBase* InTest) : Test(InTest) {}

        virtual bool Update() override
        {
            World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
            PC = World ? Cast<AGenesisPlayerController>(UGameplayStatics::GetPlayerController(World, 0)) : nullptr;
            WS = World ? World->GetSubsystem<UGenesisWorldStateSubsystem>() : nullptr;
            Dir = World ? World->GetSubsystem<UGenesisFlussdorfDirector>() : nullptr;
            if (!PC || !WS || !Dir || !PC->GetPawn()) {
                Test->AddError(TEXT("PIE world, player controller or subsystems missing"));
                return true;
            }
            const double Now = FPlatformTime::Seconds();
            if (StepStart < 0.0) StepStart = Now;
            const double Waited = Now - StepStart;
            bool bNext = false;
            switch (Step) {
            case 0: bNext = Present(TEXT("N02"), TEXT("R02")); break;
            case 1:
                bNext = Talk(TEXT("N02"), { TEXT("N02.Ask"), TEXT("N02.Accept60") });
                WS->SetClock(1, 9, 5);                                    // workshop opens
                break;
            case 2: bNext = Present(TEXT("N01"), TEXT("R03")); break;
            case 3: bNext = Talk(TEXT("N01"), { TEXT("N01.BorrowTool") }); break;
            case 4: bNext = Talk(FGenesisWorkshopContract::Generator, { TEXT("Gen.TryStart"), TEXT("Gen.InspectFilter"), TEXT("Gen.InspectPlug") }); break;
            case 5: bNext = Talk(TEXT("N03"), { TEXT("N03.BuyPlug") }); break;
            case 6: {
                const FGenesisWorldState Before = WS->GetState();
                FString Err;
                Test->TestTrue(TEXT("Save in PIE ") + Err, PC->SaveGame(&Err));
                WS->GetMutableState().PlayerMoneyGE = 999;                // change something, the load must undo it
                Test->TestTrue(TEXT("Load in PIE ") + Err, PC->LoadGame(&Err));
                Test->TestEqual(TEXT("Money restored by load"), WS->GetState().PlayerMoneyGE, Before.PlayerMoneyGE);
                Test->TestEqual(TEXT("Ledger restored by load"), WS->GetState().Ledger.Num(), Before.Ledger.Num());
                Test->TestEqual(TEXT("Contract state restored"), FGenesisWorkshopContract::State(*WS), FString(TEXT("Accepted")));
                bNext = true;
                break;
            }
            case 7: bNext = Present(TEXT("N01"), TEXT("R03")); break;    // after the load the residents stand again
            case 8: bNext = Talk(FGenesisWorkshopContract::Generator, { TEXT("Gen.Repair") }) && Talk(TEXT("N01"), { TEXT("N01.ReturnTool") }); break;
            case 9: bNext = Present(TEXT("N02"), TEXT("R02")); break;
            case 10: bNext = Talk(TEXT("N02"), { TEXT("N02.ReportDone") }); break;
            case 11:                                                          // she walks to the workshop and checks it herself
                bNext = FGenesisWorkshopContract::State(*WS) == TEXT("Completed");
                if (!bShot && Waited > 6.0) {
                    FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir() / TEXT("G6/pie_customer_walks.png"), false, false);
                    bShot = true;
                }
                break;
            default: {
                const int32 Paid = WS->GetState().Ledger.FilterByPredicate([](const FGenesisWorldEvent& E) { return E.ActionID == TEXT("Contract.Paid"); }).Num();
                Test->AddInfo(FString::Printf(TEXT("PIE mission done at %s: %d GE, paid %d time(s), %d ledger events"),
                    *WS->GetClockText(), WS->GetState().PlayerMoneyGE, Paid, WS->GetState().Ledger.Num()));
                Test->TestEqual(TEXT("Money 40 - 18 + 60"), WS->GetState().PlayerMoneyGE, 82);
                Test->TestEqual(TEXT("Paid once"), Paid, 1);
                Test->TestEqual(TEXT("Generator repaired"), WS->GetObjectState(FGenesisWorkshopContract::Generator), FString(TEXT("Repaired")));
                return true;
            }
            }
            if (bNext) {
                Test->AddInfo(FString::Printf(TEXT("step %d done at %s after %.1f s"), Step, *WS->GetClockText(), Waited));
                ++Step;
                StepStart = -1.0;
            } else if (Waited > 150.0) {
                Test->AddError(FString::Printf(TEXT("step %d timed out (contract %s)"), Step, *FGenesisWorkshopContract::State(*WS)));
                return true;
            }
            return false;
        }

    private:
        bool Present(FName Npc, FName Region) const
        {
            const FName* R = Dir->GetPresence().Find(Npc);
            return R && *R == Region;
        }

        AActor* TargetActor(FName Target) const
        {
            if (AGenesisNpc* N = Dir->FindNpc(Target)) return N;
            for (TActorIterator<AGenesisInteractableProp> It(World); It; ++It) {
                if (It->InteractionId == Target) return *It;
            }
            return nullptr;
        }

        /** Stand 1.2 m in front of the target, face it, check the prompt focus, then pick the
         *  given choices in the conversation by their action ids. */
        /** Side to stand on (customer side of the counter, open floor in the workshop) and distance. */
        static void StandFor(FName Target, FVector& Dir, float& Dist)
        {
            Dir = Target == FGenesisWorkshopContract::Generator ? FVector(-1, 0, 0) : FVector(0, -1, 0);
            Dist = Target == TEXT("N03") ? 200.f : 120.f;                 // N03 stands behind the counter
        }

        bool Talk(FName Target, std::initializer_list<const TCHAR*> Actions)
        {
            AActor* T = TargetActor(Target);
            if (!Test->TestNotNull(*FString::Printf(TEXT("Target %s"), *Target.ToString()), T)) return true;
            const FVector To = T->GetActorLocation();
            FVector Dir2D;
            float Dist;
            StandFor(Target, Dir2D, Dist);
            const FVector Stand = FVector(To.X, To.Y, 0.f) + Dir2D * Dist + FVector(0, 0, 100.f);
            const FRotator Face = (To - Stand).GetSafeNormal2D().Rotation();
            PC->GetPawn()->SetActorLocationAndRotation(Stand, Face, false, nullptr, ETeleportType::ResetPhysics);
            PC->SetControlRotation(Face);
            PC->PlayerTick(0.f);                                         // update focus/prompt now
            if (!Test->TestEqual(*FString::Printf(TEXT("Prompt focuses %s"), *Target.ToString()), PC->GetFocusTarget(), Target)) {
                // where everybody stands, so a wrong focus can be diagnosed from the log alone
                Test->AddInfo(FString::Printf(TEXT("  player at %s, target %s at %s"), *Stand.ToCompactString(), *Target.ToString(), *To.ToCompactString()));
                for (TActorIterator<AGenesisNpc> It(World); It; ++It) {
                    Test->AddInfo(FString::Printf(TEXT("  %s at %s"), *It->NpcID.ToString(), *It->GetActorLocation().ToCompactString()));
                }
            }
            PC->HandleInteract();
            if (!Test->TestTrue(*FString::Printf(TEXT("Conversation with %s open"), *Target.ToString()), PC->IsInDialog())) return true;
            for (const TCHAR* A : Actions) {
                const int32 I = PC->GetCurrentChoices().IndexOfByPredicate([&](const FGenesisChoice& C) { return C.Action == A; });
                if (!Test->TestTrue(FString::Printf(TEXT("Choice %s offered and enabled"), A), I != INDEX_NONE && PC->GetCurrentChoices()[I].bEnabled)) break;
                PC->Choose(I);
                Test->AddInfo(FString::Printf(TEXT("  %s -> \"%s\""), A, *PC->GetLastReply().Line.ToString()));
            }
            PC->Choose(PC->GetCurrentChoices().Num());                   // "Gespräch beenden"
            return true;
        }

        FAutomationTestBase* Test;
        UWorld* World = nullptr;
        AGenesisPlayerController* PC = nullptr;
        UGenesisWorldStateSubsystem* WS = nullptr;
        UGenesisFlussdorfDirector* Dir = nullptr;
        int32 Step = 0;
        double StepStart = -1.0;
        bool bShot = false;
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisFlussdorfMissionTest, "Genesis.Flussdorf.MissionPlaythrough",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisFlussdorfMissionTest::RunTest(const FString&)
{
    AutomationOpenMap(TEXT("/Game/Genesis/Flussdorf/Maps/L_Flussdorf_G6"));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(3.f));
    ADD_LATENT_AUTOMATION_COMMAND(GenesisMissionPIE::FPlay(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}
#endif
