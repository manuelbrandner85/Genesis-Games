#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "GenesisGameInstance.h"
#include "Player/GenesisPlayerController.h"
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

    /** Walks the whole menu route in Play-in-Editor: boot -> title -> main menu -> settings ->
     *  new game (slot 1) -> in game -> pause/save -> main menu -> continue -> in game with the save. */
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
                Test->TestEqual(TEXT("C00/C01 not approved: no prologue, title card next"), M->GetFlowNode(), FName("TITLE_CARD"));
                Press(EKeys::Gamepad_FaceButton_Bottom);        // "press any button"
                Test->TestEqual(TEXT("Any button opens the main menu"), M->GetScreen(), EGenesisMenuScreen::Main);
                const TArray<FString> Labels = M->GetEntryLabels();
                Test->TestEqual(TEXT("Main menu without save: 6 entries"), Labels.Num(), 6);
                Test->TestEqual(TEXT("No 'Continue' without a save"), M->FindEntry(TEXT("Fortsetzen")), int32(INDEX_NONE));
                return Next(0.3);
            }
            case 1: {
                Test->TestEqual(TEXT("Focus visible on the first entry"), M->GetFocusedEntry(), 0);
                Press(EKeys::Down);
                Press(EKeys::Gamepad_DPad_Down);
                return Next(0.2);
            }
            case 2: {
                Test->TestEqual(TEXT("Keyboard + d-pad move the focus two entries"), M->GetFocusedEntry(), 2);
                Press(EKeys::Enter);                         // focused "Einstellungen"
                return Next(0.2);
            }
            case 3: {
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
                M->ActivateEntry(0);                          // empty slot 1: starts at once
                return Next(4.0);
            }
            case 4: {
                if (!GamePC) return Fail(TEXT("new game did not open the game map"));
                Test->TestEqual(TEXT("Active slot"), GI->ActiveSlot, FString(TEXT("Slot1")));
                Test->TestTrue(TEXT("New game wrote its start save"), IFileManager::Get().FileExists(*FGenesisSaveStore::SlotPath(TEXT("Slot1"))));
                const UGenesisWorldStateSubsystem* WS = World->GetSubsystem<UGenesisWorldStateSubsystem>();
                Test->TestFalse(TEXT("New game has a soul identity"), WS->GetState().SoulID.IsEmpty());
                SoulID = WS->GetState().SoulID;
                GamePC->TogglePauseMenu();
                return Next(0.0);
            }
            case 5: {
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
            case 6: {
                if (!MenuPC || !M) return Fail(TEXT("did not return to the main menu"));
                Test->TestEqual(TEXT("Back from the game: straight to the main menu"), M->GetScreen(), EGenesisMenuScreen::Main);
                Test->TestEqual(TEXT("Continue is offered now"), M->FindEntry(TEXT("Fortsetzen")), 0);
                M->ActivateEntry(0);
                return Next(4.0);
            }
            case 7: {
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
