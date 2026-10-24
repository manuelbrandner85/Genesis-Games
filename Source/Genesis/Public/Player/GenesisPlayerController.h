#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "Mission/GenesisWorkshopContract.h"
#include "GenesisPlayerController.generated.h"

class UGenesisHudWidget;

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
    static const FString SaveSlot;

private:
    void UpdateFocus();
    void RefreshDialog();
    void CloseDialog();
    FText NameOf(FName Who) const;
    FGenesisPresence CurrentPresence() const;
    UPROPERTY() TObjectPtr<UGenesisHudWidget> Hud;
    FName FocusTarget;
    FName DialogTarget;
    TArray<FGenesisChoice> Choices;
    FGenesisReply LastReply;
    int32 Highlight = 0;
};
