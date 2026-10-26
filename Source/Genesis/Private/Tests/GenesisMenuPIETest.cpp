#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "GenesisGameInstance.h"
#include "Player/GenesisPlayerController.h"
#include "Swim/GenesisSwimGameMode.h"
#include "Pregnancy/GenesisPregnancyGameMode.h"
#include "EngineUtils.h"
#include "Save/GenesisSaveStore.h"
#include "UI/GenesisMenuGameMode.h"
#include "UI/GenesisMenuWidget.h"
#include "UI/GenesisUserSettings.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Editor.h"
#include "Framework/Application/SlateApplication.h"
#include "HAL/FileManager.h"
#include "HighResScreenshot.h"
#include "Kismet/GameplayStatics.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"

namespace
{
    const TCHAR* MenuMapPath = TEXT("/Game/Genesis/UI/Maps/L_MainMenu");

    FString TestSlotDir() { return FPaths::ProjectSavedDir() / TEXT("Automation/Genesis/MenuSlots"); }

    /** Real key press through Slate, the same path keyboard and controller input take. */
    void Press(const FKey& Key)
    {
        FSlateApplication& App = FSlateApplication::Get();
        const FKeyEvent Event(Key, App.GetModifierKeys(), 0, false, 0, 0);
        App.ProcessKeyDownEvent(Event);
        App.ProcessKeyUpEvent(Event);
    }

    /** Walks the whole route in Play-in-Editor: boot -> story start (C00 skip with confirmation, C01,
     *  C02-A) -> swim map -> C02 end -> title -> main menu -> settings -> new game (slot 1) -> chapter
     *  card -> in game with the story's soul and life -> pause/save -> main menu -> continue. */
    class FGenesisMenuDrive : public IAutomationLatentCommand
    {
    public:
        explicit FGenesisMenuDrive(FAutomationTestBase* InTest) : Test(InTest) {}

        virtual bool Update() override
        {
            UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
            if (!World || World->GetTimeSeconds() < Wait) {
                return ++Frames > 6000 ? Fail(TEXT("timeout waiting for the world")) : false;
            }
            UGenesisGameInstance* GI = Cast<UGenesisGameInstance>(World->GetGameInstance());
            APlayerController* PC = World->GetFirstPlayerController();
            AGenesisMenuPlayerController* MenuPC = Cast<AGenesisMenuPlayerController>(PC);
            AGenesisPlayerController* GamePC = Cast<AGenesisPlayerController>(PC);
            UGenesisMenuWidget* M = MenuPC ? MenuPC->GetMenu() : GamePC ? GamePC->GetPauseMenu() : nullptr;
            if (!GI) {
                return Fail(TEXT("game instance is not UGenesisGameInstance"));
            }
            switch (Step) {
            case 0: {
                if (!M) return Fail(TEXT("no main menu widget"));
                Test->TestEqual(TEXT("Starts with the boot sequence"), M->GetFlowNode(), FName("BOOT"));
                for (int32 I = 0; I < 6 && M->GetScreen() == EGenesisMenuScreen::Boot; ++I) M->AdvanceIntro();
                // CR-001: first start (no save) -> story start C00 -> C01 -> C02 with the swim.
                Test->TestEqual(TEXT("No save: story start after the boot pages"), M->GetFlowNode(), FName("STORY_START"));
                Test->TestEqual(TEXT("C00 first"), int32(GI->StoryStart.Step), int32(EGenesisStoryStep::C00));
                SoulID = GI->StoryStart.Life.SoulID;
                Press(EKeys::Gamepad_FaceButton_Bottom);
                Test->TestTrue(TEXT("One press only asks"), M->IsSkipConfirmPending());
                Test->TestEqual(TEXT("Still C00"), int32(GI->StoryStart.Step), int32(EGenesisStoryStep::C00));
                Press(EKeys::Gamepad_FaceButton_Bottom);
                Test->TestEqual(TEXT("Second press skips C00"), int32(GI->StoryStart.Step), int32(EGenesisStoryStep::C01));
                Test->TestEqual(TEXT("Light strike starts dark"), M->GetFlashLevel(), 0.f);
                Press(EKeys::Enter);
                Test->TestEqual(TEXT("C01 skipped: C02 film"), int32(GI->StoryStart.Step), int32(EGenesisStoryStep::C02Film));
                LifeID = GI->StoryStart.Life.LifeID;
                Test->TestFalse(TEXT("Life exists before C02"), LifeID.IsEmpty());
                Press(EKeys::Enter);
                Test->TestEqual(TEXT("Skipping C02-A leads into the swim"), int32(GI->StoryStart.Step), int32(EGenesisStoryStep::C02Swim));
                return NextWorld();
            }
            case 1: {
                AGenesisSwimPlayerController* SwimPC = Cast<AGenesisSwimPlayerController>(PC);
                if (!SwimPC || !SwimPC->GetPawn()) return ++Frames > 6000 ? Fail(TEXT("the swim map did not open")) : false;
                AGenesisSwimDirector* Director = nullptr;
                for (TActorIterator<AGenesisSwimDirector> It(World); It; ++It) Director = *It;
                if (!Director) return Fail(TEXT("no swim director"));
                FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir() / TEXT("CR001/route_swim.png"), false, false);
                Director->ForceFinish(TEXT("Own"));            // the swim itself is covered by Genesis.Swim.*
                return NextWorld();
            }
            case 2: {
                if (!MenuPC || !M) return ++Frames > 6000 ? Fail(TEXT("did not return to the menu map after the swim")) : false;
                Test->TestEqual(TEXT("C02 continues after the swim"), M->GetFlowNode(), FName("STORY_START"));
                Test->TestEqual(TEXT("C02 end part"), int32(GI->StoryStart.Step), int32(EGenesisStoryStep::C02End));
                Press(EKeys::Gamepad_FaceButton_Bottom);
                Test->TestEqual(TEXT("Title after C02 (E1)"), M->GetFlowNode(), FName("TITLE_CARD"));
                Press(EKeys::Gamepad_FaceButton_Bottom);        // "press any button"
                Test->TestEqual(TEXT("Any button opens the main menu"), M->GetScreen(), EGenesisMenuScreen::Main);
                Test->TestTrue(TEXT("Story start complete, life pending"), GI->HasCompletedStoryLife());
                const TArray<FString> Labels = M->GetEntryLabels();
                Test->TestEqual(TEXT("Main menu without save: 6 entries"), Labels.Num(), 6);
                Test->TestEqual(TEXT("No 'Continue' without a save"), M->FindEntry(TEXT("Fortsetzen")), int32(INDEX_NONE));
                return Next(0.3);
            }
            case 3: {
                Test->TestEqual(TEXT("Focus visible on the first entry"), M->GetFocusedEntry(), 0);
                Press(EKeys::Down);
                Press(EKeys::Gamepad_DPad_Down);
                return Next(0.2);
            }
            case 4: {
                Test->TestEqual(TEXT("Keyboard + d-pad move the focus two entries"), M->GetFocusedEntry(), 2);
                Press(EKeys::Enter);                         // focused "Einstellungen"
                return Next(0.2);
            }
            case 5: {
                Test->TestEqual(TEXT("Enter opens the settings"), M->GetScreen(), EGenesisMenuScreen::Settings);
                UGenesisUserSettings* U = UGenesisUserSettings::Get();
                const float Before = U->CameraSensitivity;
                const float VolumeBefore = U->MasterVolume;
                Press(EKeys::Down);
                Press(EKeys::Down);
                Press(EKeys::Down);
                Press(EKeys::Down);                          // focus on "Gesamtlautstaerke"
                Test->TestEqual(TEXT("Focus on master volume"), M->GetFocusedEntry(), M->FindEntry(TEXT("Gesamtlautst")));
                Press(EKeys::Gamepad_DPad_Left);
                Test->TestNearlyEqual(TEXT("D-pad left lowers the volume"), U->MasterVolume, FMath::Max(VolumeBefore - 0.1f, 0.f), 0.001f);
                Press(EKeys::Right);
                Test->TestNearlyEqual(TEXT("Right key restores it"), U->MasterVolume, VolumeBefore, 0.001f);
                const int32 Row = M->FindEntry(TEXT("Kamera-Empfindlichkeit"));
                M->AdjustEntry(Row, 1);
                Test->TestNearlyEqual(TEXT("Right raises camera sensitivity"), U->CameraSensitivity, FMath::Min(Before + 0.1f, 2.f), 0.001f);
                M->AdjustEntry(Row, -1);
                Test->TestNearlyEqual(TEXT("Left restores it"), U->CameraSensitivity, Before, 0.001f);
                Press(EKeys::Gamepad_FaceButton_Right);      // B = back
                Test->TestEqual(TEXT("B returns to the main menu"), M->GetFlowNode(), FName("MAIN_MENU"));
                for (const TCHAR* Screen : { TEXT("Barrierefreiheit"), TEXT("Mitwirkende"), TEXT("Laden") }) {
                    Test->TestTrue(FString(TEXT("Open ")) + Screen, M->ActivateEntry(M->FindEntry(Screen)));
                    if (FCString::Strcmp(Screen, TEXT("Laden")) == 0) {
                        for (int32 I = 0; I < 3; ++I) {
                            Test->TestFalse(TEXT("Empty slot cannot be loaded"), M->IsEntryEnabled(I));
                        }
                    }
                    M->Back();
                    Test->TestEqual(FString(TEXT("Back from ")) + Screen, M->GetFlowNode(), FName("MAIN_MENU"));
                }
                Press(EKeys::BackSpace);                     // Esc would also end PIE in the editor
                Test->TestEqual(TEXT("Back in the main menu asks before quitting"), M->GetScreen(), EGenesisMenuScreen::QuitConfirm);
                Test->TestEqual(TEXT("Quit dialog defaults to 'No'"), M->GetFocusedEntry() == INDEX_NONE ? 1 : M->GetFocusedEntry(), 1);
                M->Back();
                FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir() / TEXT("CM2/menu_main.png"), true, false);
                M->ActivateEntry(M->FindEntry(TEXT("Neues Leben")));
                Test->TestEqual(TEXT("New game screen"), M->GetScreen(), EGenesisMenuScreen::NewGame);
                M->ActivateEntry(0);                          // empty slot 1: chapter card, then the game
                Test->TestEqual(TEXT("Chapter card before the game"), M->GetFlowNode(), FName("CHAPTER_CARD"));
                return Next(0.8);
            }
            case 6: {
                M->AdvanceIntro();
                return NextWorld();
            }
            case 7: {
                // C02-E: the new life continues with the pregnancy (GD-2026-10-26-02/-03).
                AGenesisPregnancyPlayerController* PregPC = Cast<AGenesisPregnancyPlayerController>(PC);
                AGenesisPregnancyDirector* D = PregPC ? PregPC->GetDirector() : nullptr;
                if (!D) return ++Frames > 6000 ? Fail(TEXT("new life did not open the pregnancy")) : false;
                const UGenesisWorldStateSubsystem* PWS = World->GetSubsystem<UGenesisWorldStateSubsystem>();
                Test->TestEqual(TEXT("Pregnancy begins at S1"), D->GetPregnancy().StageId(), FName("S1"));
                Test->TestEqual(TEXT("The pregnancy carries the soul of the story start"), PWS->GetState().SoulID, SoulID);
                Test->TestEqual(TEXT("... and the life that began before C02"), PWS->GetState().LifeID, LifeID);
                Test->TestTrue(TEXT("New life wrote its start save"), IFileManager::Get().FileExists(*FGenesisSaveStore::SlotPath(TEXT("Slot1"))));
                Test->TestTrue(TEXT("Main menu: continue would open the pregnancy"), UGenesisGameInstance::DescribeSlot(TEXT("Slot1")).IsUnborn());
                for (int32 I = 0; I < 8; ++I) D->ShortenStage();         // -> S9: late pregnancy, C03 due
                return Next(8.0);
            }
            case 8: {
                AGenesisPregnancyPlayerController* PregPC = Cast<AGenesisPregnancyPlayerController>(PC);
                AGenesisPregnancyDirector* D = PregPC ? PregPC->GetDirector() : nullptr;
                if (!D) return Fail(TEXT("pregnancy director gone"));
                Test->TestTrue(TEXT("C03 shown in late pregnancy"), D->GetPregnancy().bC03Done);
                D->ShortenStage();                                    // -> S10
                D->ShortenStage();                                    // -> birth, C04, then the world
                return Next(0.5);
            }
            case 9: {
                if (!GamePC) return ++Frames > 6000 ? Fail(TEXT("the birth did not lead into the world")) : false;
                return Next(1.0);                             // the world loads the birth save on its first tick
            }
            case 10: {
                if (!GamePC) return Fail(TEXT("new game did not open the game map"));
                Test->TestEqual(TEXT("Active slot"), GI->ActiveSlot, FString(TEXT("Slot1")));
                Test->TestTrue(TEXT("New game wrote its start save"), IFileManager::Get().FileExists(*FGenesisSaveStore::SlotPath(TEXT("Slot1"))));
                const UGenesisWorldStateSubsystem* WS = World->GetSubsystem<UGenesisWorldStateSubsystem>();
                Test->TestEqual(TEXT("After the birth"), WS->GetState().PregnancyStage, FName("Born"));
                Test->TestFalse(TEXT("New game has a soul identity"), WS->GetState().SoulID.IsEmpty());
                Test->TestEqual(TEXT("The game plays the soul of the story start"), WS->GetState().SoulID, SoulID);
                Test->TestEqual(TEXT("... and the life that began before C02"), WS->GetState().LifeID, LifeID);
                Test->TestEqual(TEXT("Story start passed"), WS->GetState().StoryStartStage, FName("Done"));
                Test->TestEqual(TEXT("Own cell fused"), WS->GetState().ConceptionMode, FName("Own"));
                Test->TestFalse(TEXT("Story life consumed"), GI->HasCompletedStoryLife());
                GamePC->TogglePauseMenu();
                return Next(0.0);
            }
            case 11: {
                if (!M) return Fail(TEXT("pause menu did not open"));
                Test->TestTrue(TEXT("Game paused"), UGameplayStatics::IsGamePaused(World));
                Test->TestEqual(TEXT("Pause node"), M->GetFlowNode(), FName("PAUSE_MENU"));
                Test->TestTrue(TEXT("Save from the pause menu"), M->ActivateEntry(M->FindEntry(TEXT("Speichern"))));
                Test->TestTrue(TEXT("Save confirmed"), M->GetInfoText().StartsWith(TEXT("Gespeichert")));
                M->ActivateEntry(M->FindEntry(TEXT("Einstellungen")));
                M->Back();
                Test->TestEqual(TEXT("Settings from pause return to pause"), M->GetFlowNode(), FName("PAUSE_MENU"));
                FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir() / TEXT("CM2/menu_pause.png"), true, false);
                M->Back();                                    // resume
                Test->TestFalse(TEXT("Resumed"), UGameplayStatics::IsGamePaused(World));
                Test->TestFalse(TEXT("Pause menu closed"), GamePC->IsPauseMenuOpen());
                GamePC->TogglePauseMenu();
                UGenesisMenuWidget* P = GamePC->GetPauseMenu();
                P->ActivateEntry(P->FindEntry(TEXT("Hauptmen")));
                Test->TestEqual(TEXT("Main menu asks first"), P->GetScreen(), EGenesisMenuScreen::MainMenuConfirm);
                P->ActivateEntry(0);
                return Next(3.0);
            }
            case 12: {
                if (!MenuPC || !M) return Fail(TEXT("did not return to the main menu"));
                Test->TestEqual(TEXT("Back from the game: straight to the main menu"), M->GetScreen(), EGenesisMenuScreen::Main);
                Test->TestEqual(TEXT("Continue is offered now"), M->FindEntry(TEXT("Fortsetzen")), 0);
                M->ActivateEntry(0);
                return Next(4.0);
            }
            case 13: {
                if (!GamePC) return Fail(TEXT("continue did not open the game"));
                const UGenesisWorldStateSubsystem* WS = World->GetSubsystem<UGenesisWorldStateSubsystem>();
                Test->TestEqual(TEXT("Continue loaded the saved soul"), WS->GetState().SoulID, SoulID);
                Test->TestFalse(TEXT("Load flag consumed"), GI->bLoadSlotOnStart);
                return true;
            }
            default:
                return true;
            }
        }

    private:
        /** After a map change the new world's clock starts at 0: wait for the new world, not a time. */
        bool NextWorld()
        {
            ++Step;
            Wait = 0.0;
            Frames = 0;
            return false;
        }
        bool Next(double Seconds)
        {
            ++Step;
            Wait = GEditor->PlayWorld->GetTimeSeconds() + Seconds;
            Frames = 0;
            return false;
        }
        bool Fail(const TCHAR* Why)
        {
            Test->AddError(FString::Printf(TEXT("Menu drive step %d: %s"), Step, Why));
            return true;
        }
        FAutomationTestBase* Test;
        int32 Step = 0;
        int32 Frames = 0;
        double Wait = 0.0;
        FString SoulID;
        FString LifeID;
    };

    class FGenesisMenuCleanup : public IAutomationLatentCommand
    {
    public:
        virtual bool Update() override
        {
            FGenesisSaveStore::SlotDirectoryOverride.Reset();
            IFileManager::Get().DeleteDirectory(*TestSlotDir(), false, true);
            return true;
        }
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisMenuPIETest, "Genesis.Menu.PIERoute",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisMenuPIETest::RunTest(const FString&)
{
    IFileManager::Get().DeleteDirectory(*TestSlotDir(), false, true);
    FGenesisSaveStore::SlotDirectoryOverride = TestSlotDir();       // never the player's saves
    AutomationOpenMap(MenuMapPath);
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2.f));
    ADD_LATENT_AUTOMATION_COMMAND(FGenesisMenuDrive(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    ADD_LATENT_AUTOMATION_COMMAND(FGenesisMenuCleanup());
    return true;
}
#endif
