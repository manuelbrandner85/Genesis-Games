#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "Mission/GenesisWorkshopContract.h"
#include "GenesisPlayerController.generated.h"

class UGenesisHudWidget;
class UGenesisMenuWidget;
class UGenesisSceneRunner;

/**
 * Player-side interaction: finds what the player is facing (resident or object within reach),
 * shows the prompt, runs conversations through FGenesisWorkshopContract and saves/loads the game
 * (F5 / F9) through FGenesisSaveStore. While a conversation is open the character does not move.
 */
UCLASS()
class GENESIS_API AGenesisPlayerController : public APlayerController
{
    GENERATED_BODY()
public:
    AGenesisPlayerController();
    virtual void BeginPlay() override;
    virtual void PlayerTick(float DeltaTime) override;
    virtual void SetupInputComponent() override;

    bool IsInDialog() const { return !DialogTarget.IsNone(); }
    void HandleInteract();
    void Choose(int32 Index);
    void MoveHighlight(int32 Delta);
    void ConfirmHighlight() { Choose(Highlight); }
    bool SaveGame(FString* OutError = nullptr);
    bool LoadGame(FString* OutError = nullptr);

    /** For tests: what the player is facing right now (resident id or object id). */
    FName GetFocusTarget() const { return FocusTarget; }
    /** For tests: open the conversation with a target directly. */
    void OpenDialog(FName Target);
    const TArray<FGenesisChoice>& GetCurrentChoices() const { return Choices; }
    const FGenesisReply& GetLastReply() const { return LastReply; }

    static constexpr float ReachCm = 220.f;
    /** Save slot of this session (chosen in the main menu; "Dev" when started directly in the editor). */
    FString GetActiveSlot() const;
    /** Esc / P / gamepad Menu: opens the pause menu (game paused, clock stopped). */
    void TogglePauseMenu();
    bool IsPauseMenuOpen() const { return PauseMenu != nullptr; }
    UGenesisMenuWidget* GetPauseMenu() const { return PauseMenu; }

    /** CM3: non-canonical technical C00 camera test through the scene contract (console: GenesisTechCinematic). */
    UFUNCTION(Exec) void GenesisTechCinematic();
    UGenesisSceneRunner* GetSceneRunner() const { return SceneRunner; }
    static const TCHAR* TechSequencePath;

private:
    void UpdateFocus();
    void RefreshDialog();
    void CloseDialog();
    FText NameOf(FName Who) const;
    FGenesisPresence CurrentPresence() const;
    void ClosePauseMenu();
    void RunStartAction();
    UPROPERTY() TObjectPtr<UGenesisHudWidget> Hud;
    UPROPERTY() TObjectPtr<UGenesisMenuWidget> PauseMenu;
    UPROPERTY() TObjectPtr<UGenesisSceneRunner> SceneRunner;
    void SkipCinematic();
    FName FocusTarget;
    FName DialogTarget;
    TArray<FGenesisChoice> Choices;
    FGenesisReply LastReply;
    int32 Highlight = 0;
};
