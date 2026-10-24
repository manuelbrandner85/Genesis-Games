#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Cinematic/GenesisCinematicSubsystem.h"
#include "Cinematic/GenesisSceneRunner.h"
#include "Player/GenesisPlayerController.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Editor.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"

namespace
{
    /** CM3: plays the non-canonical C00 camera test in the real game map twice - once skipped,
     *  once to the end - and checks contract states, commit, hand-back and that the ledger stays clean. */
    class FGenesisTechCinematicDrive : public IAutomationLatentCommand
    {
    public:
        explicit FGenesisTechCinematicDrive(FAutomationTestBase* InTest) : Test(InTest) {}

        virtual bool Update() override
        {
            UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
            AGenesisPlayerController* PC = World ? Cast<AGenesisPlayerController>(World->GetFirstPlayerController()) : nullptr;
            if (!PC || !PC->GetPawn()) {
                Test->AddError(TEXT("No PIE world / Genesis player"));
                return true;
            }
            if (World->GetTimeSeconds() < Wait) {
                return false;
            }
            const UGenesisWorldStateSubsystem* WS = World->GetSubsystem<UGenesisWorldStateSubsystem>();
            UGenesisCinematicSubsystem* Cine = World->GetGameInstance()->GetSubsystem<UGenesisCinematicSubsystem>();
            switch (Step) {
            case 0:
                LedgerBefore = WS->GetState().Ledger.Num();
                PC->GenesisTechCinematic();
                if (!PC->GetSceneRunner() || !PC->GetSceneRunner()->IsRunning()) {
                    Test->AddError(TEXT("Tech cinematic did not start"));
                    return true;
                }
                Test->TestEqual(TEXT("Contract is Playing"), PC->GetSceneRunner()->GetContract().CinematicState, EGenesisCinematicState::Playing);
                Test->TestTrue(TEXT("Marked as technical test"), PC->GetSceneRunner()->GetContract().bTechnicalTest);
                Test->TestFalse(TEXT("Player input blocked"), PC->GetPawn()->InputEnabled());
                PC->TogglePauseMenu();
                Test->TestFalse(TEXT("No pause menu over a running cinematic"), PC->IsPauseMenuOpen());
                return Next(1.5);
            case 1: {
                Test->TestTrue(TEXT("Sequence camera has the view"), PC->GetViewTarget() != PC->GetPawn());
                UGenesisSceneRunner* R = PC->GetSceneRunner();
                Test->TestTrue(TEXT("Skip accepted"), R->Skip());
                Test->TestEqual(TEXT("Skip still commits and hands back"), R->GetContract().CinematicState, EGenesisCinematicState::HandedBack);
                Test->TestTrue(TEXT("Commit recorded (technical, in memory)"), Cine->TechTestCommits.Contains(R->GetContract().CommitKey()));
                Test->TestEqual(TEXT("World ledger untouched by the technical test"), WS->GetState().Ledger.Num(), LedgerBefore);
                Test->TestTrue(TEXT("Player input back"), PC->GetPawn()->InputEnabled());
                Test->TestTrue(TEXT("View back on the player"), PC->GetViewTarget() == PC->GetPawn());
                PC->GenesisTechCinematic();                // second run: watch to the end
                return Next(9.0);
            }
            case 2: {
                UGenesisSceneRunner* R = PC->GetSceneRunner();
                Test->TestEqual(TEXT("Played to the end and handed back"), R->GetContract().CinematicState, EGenesisCinematicState::HandedBack);
                Test->TestFalse(TEXT("Runner finished"), R->IsRunning());
                Test->TestTrue(TEXT("View back on the player after the end"), PC->GetViewTarget() == PC->GetPawn());
                Test->TestEqual(TEXT("Ledger still untouched"), WS->GetState().Ledger.Num(), LedgerBefore);
                return true;
            }
            default:
                return true;
            }
        }

    private:
        bool Next(double Seconds)
        {
            ++Step;
            Wait = GEditor->PlayWorld->GetTimeSeconds() + Seconds;
            return false;
        }
        FAutomationTestBase* Test;
        int32 Step = 0;
        int32 LedgerBefore = 0;
        double Wait = 0.0;
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisTechCinematicPIETest, "Genesis.Cinematic.TechC00PIE",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisTechCinematicPIETest::RunTest(const FString&)
{
    AutomationOpenMap(TEXT("/Game/Genesis/Flussdorf/Maps/L_Flussdorf_G6"));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(3.f));
    ADD_LATENT_AUTOMATION_COMMAND(FGenesisTechCinematicDrive(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}
#endif
