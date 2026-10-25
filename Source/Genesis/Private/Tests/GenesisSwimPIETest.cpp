#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "GenesisGameInstance.h"
#include "Swim/GenesisOviduct.h"
#include "Swim/GenesisSpermPawn.h"
#include "Swim/GenesisSwimGameMode.h"
#include "UI/GenesisMenuWidget.h"
#include "UI/GenesisUserSettings.h"
#include "Editor.h"
#include "EngineUtils.h"
#include "GameFramework/WorldSettings.h"
#include "HAL/FileManager.h"
#include "HighResScreenshot.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"

namespace
{
    FString EvidenceDir() { return FPaths::ProjectSavedDir() / TEXT("CR001"); }

    /** Real key through the player's input pipeline (the path keyboard and gamepad take). */
    void Key(APlayerController* PC, const FKey& K, EInputEvent Event)
    {
        PC->InputKey(FInputKeyEventArgs(nullptr, FInputDeviceId::CreateFromInternalId(0), K, Event, FPlatformTime::Cycles64()));
    }

    void Axis(APlayerController* PC, const FKey& K, float Value)
    {
        PC->InputKey(FInputKeyEventArgs(nullptr, FInputDeviceId::CreateFromInternalId(0), K, Value, 1.f / 60.f, 1, FPlatformTime::Cycles64()));
    }

    struct FSwimWorld
    {
        UWorld* World = nullptr;
        AGenesisSwimPlayerController* PC = nullptr;
        AGenesisSpermPawn* Sperm = nullptr;
        AGenesisSwimDirector* Director = nullptr;

        bool Find()
        {
            World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
            PC = World ? Cast<AGenesisSwimPlayerController>(World->GetFirstPlayerController()) : nullptr;
            Sperm = PC ? Cast<AGenesisSpermPawn>(PC->GetPawn()) : nullptr;
            Director = nullptr;
            if (World) {
                for (TActorIterator<AGenesisSwimDirector> It(World); It; ++It) {
                    Director = *It;
                }
            }
            return Sperm && Director;
        }
    };

    /** 120 s (and more) without any input: the scene goes on, guidance begins at 120 s and the swim
     *  ends with a result - never a game over. Runs at 6x game speed; also measures the frame rate. */
    class FGenesisSwimNoInputDrive : public IAutomationLatentCommand
    {
    public:
        explicit FGenesisSwimNoInputDrive(FAutomationTestBase* InTest) : Test(InTest) {}

        virtual bool Update() override
        {
            FSwimWorld W;
            if (!W.Find()) {
                return ++Frames > 600 ? Fail(TEXT("no swim world (map/game mode)")) : false;
            }
            const double Now = FPlatformTime::Seconds();
            switch (Step) {
            case 0:
                Start = Now;
                FrameCount = 0;
                Step = 1;
                return false;
            case 1:
                // Frame rate at normal speed in PIE (editor viewport, not a packaged build).
                ++FrameCount;
                if (Now - Start < 6.0) {
                    return false;
                }
                Fps = FrameCount / (Now - Start);
                IFileManager::Get().MakeDirectory(*EvidenceDir(), true);
                FScreenshotRequest::RequestScreenshot(EvidenceDir() / TEXT("swim_start.png"), false, false);
                StartS = W.Sperm->GetCourseS();
                W.World->GetWorldSettings()->SetTimeDilation(6.f);
                Step = 2;
                return false;
            case 2: {
                if (W.Director->GetPhase() == EGenesisSwimPhase::Guided && !bSawGuided) {
                    bSawGuided = true;
                    GuidedAt = W.Director->GetElapsed();
                }
                if (W.Director->GetPhase() == EGenesisSwimPhase::Fusion && !bShot) {
                    bShot = true;
                    FScreenshotRequest::RequestScreenshot(EvidenceDir() / TEXT("swim_fusion.png"), false, false);
                }
                if (!W.Director->IsFinished()) {
                    return W.Director->GetElapsed() > 200.f ? Fail(TEXT("swim did not end by 200 s")) : false;
                }
                const float Arrival = W.Director->GetArrivalSeconds();
                Test->TestTrue(TEXT("The cell moved up the oviduct without input (rheotaxis)"), W.Sperm->GetCourseS() > StartS + 1000.f || W.Director->GetResult() == FName("Other"));
                Test->TestFalse(TEXT("Swim ended with a result (no game over)"), W.Director->GetResult().IsNone());
                Test->TestTrue(TEXT("Result is Own or Other"), W.Director->GetResult() == FName("Own") || W.Director->GetResult() == FName("Other"));
                if (W.Director->GetResult() == FName("Own")) {
                    Test->TestTrue(*FString::Printf(TEXT("Arrival %.1f s is not before 60 s (E4)"), Arrival), Arrival >= 55.f);
                }
                Test->TestTrue(TEXT("Scene went on past 120 s or arrived inside the window"), bSawGuided || (Arrival > 0.f && Arrival <= 120.f));
                if (bSawGuided) {
                    Test->TestTrue(TEXT("Guidance began at 120 s"), GuidedAt >= 119.f && GuidedAt <= 122.f);
                }
                const FString Report = FString::Printf(
                    TEXT("{\n  \"test\": \"Genesis.Swim.NoInputPIE\",\n  \"input\": \"none\",\n  \"result\": \"%s\",\n  \"arrival_s\": %.1f,\n  \"guided_from_s\": %.1f,\n  \"ended_after_s\": %.1f,\n  \"wall_contacts\": %d,\n  \"pie_fps_avg\": %.1f,\n  \"note\": \"PIE in the editor viewport, game speed 6x after the fps window; not a packaged build\"\n}\n"),
                    *W.Director->GetResult().ToString(), Arrival, bSawGuided ? GuidedAt : -1.f, W.Director->GetElapsed(), W.Sperm->GetWallContacts(), Fps);
                FFileHelper::SaveStringToFile(Report, *(EvidenceDir() / TEXT("swim_no_input.json")));
                Test->AddInfo(Report);
                W.World->GetWorldSettings()->SetTimeDilation(1.f);
                return true;
            }
            default:
                return true;
            }
        }

    private:
        bool Fail(const TCHAR* Why)
        {
            Test->AddError(FString::Printf(TEXT("Swim no-input step %d: %s"), Step, Why));
            return true;
        }
        FAutomationTestBase* Test;
        int32 Step = 0;
        int32 Frames = 0;
        int32 FrameCount = 0;
        double Start = 0.0;
        double Fps = 0.0;
        float StartS = 0.f;
        float GuidedAt = -1.f;
        bool bSawGuided = false;
        bool bShot = false;
    };

    /** Keyboard and gamepad through the input pipeline, stick dead zone, harder beat, pause menu. */
    class FGenesisSwimControlsDrive : public IAutomationLatentCommand
    {
    public:
        explicit FGenesisSwimControlsDrive(FAutomationTestBase* InTest) : Test(InTest) {}

        virtual bool Update() override
        {
            FSwimWorld W;
            if (!W.Find()) {
                return ++Frames > 600 ? Fail(TEXT("no swim world")) : false;
            }
            const double T = W.World->GetRealTimeSeconds();
            if (T < Wait) {
                if (Step == 3) Axis(W.PC, EKeys::Gamepad_LeftX, 1.f);          // stick held: sent every frame
                if (Step == 4) Axis(W.PC, EKeys::Gamepad_LeftX, 0.15f);        // drift-sized deflection
                return false;
            }
            switch (Step) {
            case 0:
                Heading = W.Sperm->GetHeading();
                Key(W.PC, EKeys::W, IE_Pressed);
                return Next(T, 1.0);
            case 1:
                Test->TestEqual(TEXT("W steers up"), W.PC->GetLastSteer().Y, 1.0);
                Test->TestTrue(TEXT("Heading pitched up"), W.Sperm->GetHeading().Z > Heading.Z + 0.2f);
                Key(W.PC, EKeys::W, IE_Released);
                Key(W.PC, EKeys::SpaceBar, IE_Pressed);
                SpeedBefore = W.Sperm->GetSwimVelocity().Size();
                return Next(T, 0.6);
            case 2:
                Test->TestTrue(TEXT("Space beats harder"), W.PC->GetLastBurst());
                Test->TestTrue(TEXT("Faster with the harder beat"), W.Sperm->GetSwimVelocity().Size() > SpeedBefore + 5.f);
                Key(W.PC, EKeys::SpaceBar, IE_Released);
                Heading = W.Sperm->GetHeading();
                return Next(T, 1.0);
            case 3:
                Test->TestTrue(TEXT("Gamepad stick steers"), W.PC->GetLastSteer().X > 0.9f);
                Test->TestTrue(TEXT("Heading turned"), FVector::DotProduct(W.Sperm->GetHeading(), Heading) < 0.98f);
                return Next(T, 0.5);
            case 4:
                Test->TestEqual(TEXT("Small stick drift is ignored (dead zone)"), W.PC->GetLastSteer().X, 0.0);
                Key(W.PC, EKeys::Gamepad_Special_Right, IE_Pressed);
                Key(W.PC, EKeys::Gamepad_Special_Right, IE_Released);
                return Next(T, 0.3);
            case 5: {
                UGenesisMenuWidget* M = W.PC->GetPauseMenu();
                if (!M) return Fail(TEXT("Menu button did not open the pause menu"));
                Test->TestTrue(TEXT("Swim paused"), UGameplayStatics::IsGamePaused(W.World));
                Test->TestEqual(TEXT("Pause node from the swim"), M->GetFlowNode(), FName("PAUSE_MENU"));
                Test->TestEqual(TEXT("No saving in the story start"), M->FindEntry(TEXT("Speichern")), int32(INDEX_NONE));
                Elapsed = W.Director->GetElapsed();
                Test->TestTrue(TEXT("Accessibility reachable from the swim pause"), M->ActivateEntry(M->FindEntry(TEXT("Barrierefreiheit"))));
                const int32 Auto = M->FindEntry(TEXT("Automatisch schwimmen"));
                Test->TestTrue(TEXT("Auto swim option present"), Auto != INDEX_NONE);
                M->ActivateEntry(Auto);
                Test->TestTrue(TEXT("Auto swim on"), UGenesisUserSettings::Get()->bAutoSwim);
                return Next(T, 1.0);                           // stay paused for a second
            }
            case 6: {
                Test->TestTrue(TEXT("Swim time stands still while paused"), FMath::IsNearlyEqual(W.Director->GetElapsed(), Elapsed, 0.05f));
                UGenesisMenuWidget* M = W.PC->GetPauseMenu();
                if (!M) return Fail(TEXT("pause menu vanished"));
                M->Back();
                M->Back();                                     // resume
                Test->TestFalse(TEXT("Resumed"), UGameplayStatics::IsGamePaused(W.World));
                Test->TestFalse(TEXT("Pause menu closed"), W.PC->IsPauseMenuOpen());
                return Next(T, 1.0);
            }
            case 7:
                Test->TestTrue(TEXT("Auto swim guides"), W.Sperm->GetGuidance() > 0.5f);
                UGenesisUserSettings::Get()->bAutoSwim = false;
                FScreenshotRequest::RequestScreenshot(EvidenceDir() / TEXT("swim_controls.png"), false, false);
                return true;
            default:
                return true;
            }
        }

    private:
        bool Next(double Now, double Seconds)
        {
            ++Step;
            Wait = Now + Seconds;
            return false;
        }
        bool Fail(const TCHAR* Why)
        {
            Test->AddError(FString::Printf(TEXT("Swim controls step %d: %s"), Step, Why));
            UGenesisUserSettings::Get()->bAutoSwim = false;
            return true;
        }
        FAutomationTestBase* Test;
        int32 Step = 0;
        int32 Frames = 0;
        double Wait = 0.0;
        float SpeedBefore = 0.f;
        float Elapsed = 0.f;
        FVector Heading = FVector::ZeroVector;
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSwimNoInputPIETest, "Genesis.Swim.NoInputPIE",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisSwimNoInputPIETest::RunTest(const FString&)
{
    UGenesisUserSettings::Get()->bAutoSwim = false;
    AutomationOpenMap(UGenesisGameInstance::SwimMap);
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2.f));
    ADD_LATENT_AUTOMATION_COMMAND(FGenesisSwimNoInputDrive(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSwimControlsPIETest, "Genesis.Swim.ControlsPIE",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisSwimControlsPIETest::RunTest(const FString&)
{
    UGenesisUserSettings::Get()->bAutoSwim = false;
    AutomationOpenMap(UGenesisGameInstance::SwimMap);
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2.f));
    ADD_LATENT_AUTOMATION_COMMAND(FGenesisSwimControlsDrive(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}
#endif
