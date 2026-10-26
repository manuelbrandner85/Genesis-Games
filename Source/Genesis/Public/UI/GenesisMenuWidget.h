#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "UI/GenesisMenuFlow.h"
#include "GenesisMenuWidget.generated.h"

class UBorder;
class UCanvasPanel;
class UScrollBox;
class UTextBlock;
class UVerticalBox;
class UGenesisChoiceButton;

/** Which game the pause menu interrupts: the world, the C02-B route (no slot yet) or the pregnancy. */
UENUM()
enum class EGenesisPauseKind : uint8
{
    Game,
    StoryRoute,
    Pregnancy,
};

UENUM()
enum class EGenesisMenuScreen : uint8
{
    None, Boot, Title, Main, NewGame, NewGameConfirm, Load, Settings, Accessibility, Credits, QuitConfirm,
    Pause, MainMenuConfirm,
    StoryStart,         // CR-001: C00 / C01 light strike / C02 film parts (placeholders until the masters exist)
    ChapterCard,        // "Neues Leben": chapter card, then the game
};

/**
 * Main menu and pause menu (ScriptLock III-D), built in C++ like the HUD. Every screen change goes
 * along an edge of FGenesisMenuFlow (Content/Genesis/Data/menu_flow.json), so no button leads
 * nowhere. Keyboard, mouse and controller: arrows/d-pad move the visible focus, Enter/A selects,
 * Esc/B goes back, left/right changes a setting. Nothing here changes the world state; saving and
 * loading go through the transactional FGenesisSaveStore.
 */
UCLASS()
class GENESIS_API UGenesisMenuWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    /** Main menu map: boot sequence (warnings) -> title card -> main menu; returning from the game skips to the main menu. */
    void StartMainMenu(bool bSkipBoot);
    /** In the game: opens as pause menu (C02-B route: no save/load, "Weg abkürzen" after the first time;
     *  pregnancy: save/load and "Abschnitt abkürzen"). */
    void StartPauseMenu(EGenesisPauseKind Kind = EGenesisPauseKind::Game);
    /** Back from the swim map: C02 continues (C02-C..F), then title card or chapter card. */
    void ResumeStoryStart();

    DECLARE_DELEGATE(FOnResume);
    FOnResume OnResume;

    // --- For automation tests and the controller ---------------------------------------------------
    EGenesisMenuScreen GetScreen() const { return Screen; }
    FName GetFlowNode() const { return Flow.Current; }
    TArray<FString> GetEntryLabels() const;
    bool IsEntryEnabled(int32 Index) const { return Entries.IsValidIndex(Index) && Entries[Index].bEnabled; }
    int32 FindEntry(const FString& Label) const;
    bool ActivateEntry(int32 Index);
    bool AdjustEntry(int32 Index, int32 Direction);
    void Back();
    void AdvanceIntro();
    /** Story start film part: a key press skips (C00 asks for a second press first). */
    void StoryKey();
    bool IsSkipConfirmPending() const { return ConfirmSkipUntil > ScreenTime; }
    /** Current white level of the light-strike overlay (C01), for tests and capture. */
    float GetFlashLevel() const;
    /** Size of the visible light point (share of screen height), 0 when hidden (CR-003 soul point). */
    float GetLightPointShare() const { return LightPointShare; }
    int32 GetFocusedEntry() const;
    const FString& GetInfoText() const { return InfoText; }
    const FString& GetLastFlowError() const { return LastFlowError; }

protected:
    virtual void NativeOnInitialized() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
    virtual FReply NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent) override;
    virtual FReply NativeOnPreviewKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent) override;
    virtual FReply NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;

private:
    struct FEntry
    {
        TFunction<FString()> Label;
        TFunction<void()> Activate;
        TFunction<void(int32)> Adjust;      // settings rows: left/right
        bool bEnabled = true;
    };

    bool ShowScreen(EGenesisMenuScreen NewScreen);
    void Rebuild();
    void BuildEntries();
    void AddButton(const FString& Label, TFunction<void()> Activate, bool bEnabled = true);
    void AddCycle(const FString& Label, TFunction<int32()> Get, TFunction<void(int32)> Set, const TArray<FString>& Names);
    void AddPercent(const FString& Label, float* Value, float Min, float Max, float Step);
    void AddToggle(const FString& Label, bool* Value);
    void SettingsChanged(bool bEngineSettings);
    void FocusEntry(int32 Index);
    void HandleChoice(int32 Index);
    void ChooseNewGameSlot(const FString& SaveSlotName);
    void StoryStartTick();
    void FinishStoryPart(bool bSkipped);
    float StoryPartSeconds() const;
    class UGenesisGameInstance* GetGenesisGI() const;
    void Resume();
    FString SlotLabel(const FString& SaveSlotName, bool bForNewGame) const;
    UTextBlock* MakeText(const FString& Name, int32 Size, const FLinearColor& Color = FLinearColor::White);
    int32 Scaled(int32 Size) const;

    FGenesisMenuFlow Flow;
    EGenesisMenuScreen Screen = EGenesisMenuScreen::None;
    EGenesisMenuScreen ReturnScreen = EGenesisMenuScreen::Main;   // Main or Pause
    bool bInGame = false;
    bool bStoryPause = false;
    EGenesisPauseKind PauseKind = EGenesisPauseKind::Game;
    FName PlayNode() const;
    bool bSwimRequested = false;
    float ConfirmSkipUntil = -1.f;
    float LightPointShare = 0.f;
    FString PendingSlot;
    FString InfoText;
    FString LastFlowError;
    TArray<FEntry> Entries;
    int32 PendingChoice = INDEX_NONE;
    int32 LastFocused = 0;
    int32 BootPage = 0;
    float ScreenTime = 0.f;

    UCanvasPanel* Root = nullptr;
    UBorder* Shade = nullptr;
    UBorder* Panel = nullptr;
    UBorder* Flash = nullptr;          // C01 light strike: full-screen warm white
    UBorder* LightPoint = nullptr;     // C01: the point of light before the strike
    UVerticalBox* Center = nullptr;
    UTextBlock* BigTitle = nullptr;
    UTextBlock* BigSub = nullptr;
    UTextBlock* Press = nullptr;
    UTextBlock* Header = nullptr;
    UTextBlock* Info = nullptr;
    UScrollBox* Scroll = nullptr;
    UVerticalBox* ButtonBox = nullptr;
    UTextBlock* Footer = nullptr;
    UPROPERTY() TArray<TObjectPtr<UGenesisChoiceButton>> Buttons;
    TArray<UTextBlock*> ButtonTexts;
};
