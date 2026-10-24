#pragma once
#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
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

    FString ActiveSlot = TEXT("Dev");
    bool bLoadSlotOnStart = false;
    bool bNewGamePendingSave = false;
    bool bBootSequenceShown = false;

    void StartNewGame(const FString& Slot);
    void LoadSlotAndPlay(const FString& Slot);
    void ReturnToMainMenu();
};
