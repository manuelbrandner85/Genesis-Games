#pragma once
#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "Cinematic/GenesisStoryStart.h"
#include "GenesisGameInstance.generated.h"

/** What the load screen shows about a save slot (read from the verified save file). */
struct GENESIS_API FGenesisSlotInfo
{
    FString Slot;
    bool bExists = false;
    bool bValid = false;
    bool bFromBackup = false;
    FString Error;
    int32 Day = 0;
    int32 Hour = 0;
    int32 Minute = 0;
    int32 MoneyGE = 0;
    int32 LifeNumber = 1;
    FDateTime SavedAt;
};

/**
 * Lives for the whole game session: carries the chosen save slot from the main menu into the game
 * (new game or load) and back. The three player slots are Slot1-Slot3; a game started directly in
 * the editor (PIE, automation) uses the "Dev" slot, so tests never touch a player's save.
 */
UCLASS()
class GENESIS_API UGenesisGameInstance : public UGameInstance
{
    GENERATED_BODY()
public:
    virtual void Init() override;

    static const TArray<FString>& PlayerSlots();
    static FGenesisSlotInfo DescribeSlot(const FString& Slot);
    /** Newest valid player slot, empty if there is none ("Continue" is hidden then). */
    static FString MostRecentSlot();

    static const TCHAR* GameplayMap;
    static const TCHAR* MenuMap;
    static const TCHAR* SwimMap;

    FString ActiveSlot = TEXT("Dev");
    bool bLoadSlotOnStart = false;
    bool bNewGamePendingSave = false;
    bool bBootSequenceShown = false;

    void StartNewGame(const FString& Slot);
    void LoadSlotAndPlay(const FString& Slot);
    void ReturnToMainMenu();

    // --- Story start (CR-001): C00 -> C01 -> C02 with the swim map -> title / chapter card ----------
    FGenesisStoryStart StoryStart;
    /** Started from "Neues Leben" (returning player): ends with the chapter card into the game
     *  instead of the title card; StoryStartSlot is the chosen save slot. */
    bool bStoryStartForNewLife = false;
    FString StoryStartSlot;
    bool BeginStoryStart(bool bForNewLife, const FString& Slot = FString());
    /** C02-B: opens the swim map (the C02 contract is InGameplaySegment now). */
    void EnterSwim();
    /** End of the swim (Own/Other): C02 continues in the menu map, then title or chapter card. */
    bool FinishSwim(FName ConceptionMode);
    /** Leaves the story start from the pause menu: the coming life is dropped, back to the main menu. */
    void AbortStoryStart();
    bool HasCompletedStoryLife() const { return StoryStart.Step == EGenesisStoryStep::Done; }
    /** New game: the life built in the story start becomes the start state (same soul and life
     *  as in C00-C02). Consumed once. Returns false if there is none (e.g. editor start). */
    bool TakeStoryLife(FGenesisWorldState& State);
};
