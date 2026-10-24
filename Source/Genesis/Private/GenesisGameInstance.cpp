#include "GenesisGameInstance.h"
#include "Save/GenesisSaveStore.h"
#include "UI/GenesisUserSettings.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"

const TCHAR* UGenesisGameInstance::GameplayMap = TEXT("/Game/Genesis/Flussdorf/Maps/L_Flussdorf_G6");
const TCHAR* UGenesisGameInstance::MenuMap = TEXT("/Game/Genesis/UI/Maps/L_MainMenu");

void UGenesisGameInstance::Init()
{
    Super::Init();
    if (UGenesisUserSettings* S = UGenesisUserSettings::Get()) {
        S->ApplyGenesisOptions(this);
    }
}

const TArray<FString>& UGenesisGameInstance::PlayerSlots()
{
    static const TArray<FString> Slots = { TEXT("Slot1"), TEXT("Slot2"), TEXT("Slot3") };
    return Slots;
}

FGenesisSlotInfo UGenesisGameInstance::DescribeSlot(const FString& Slot)
{
    FGenesisSlotInfo Info;
    Info.Slot = Slot;
    const FString Path = FGenesisSaveStore::SlotPath(Slot);
    IFileManager& FM = IFileManager::Get();
    Info.bExists = FM.FileExists(*Path) || FM.FileExists(*(Path + TEXT(".bak")));
    if (!Info.bExists) {
        return Info;
    }
    FGenesisWorldState S;
    Info.bValid = FGenesisSaveStore::Load(Path, S, Info.Error, &Info.bFromBackup);
    if (Info.bValid) {
        const int64 Minute = S.WorldMinute;
        Info.Day = int32(Minute / (24 * 60)) + 1;
        Info.Hour = int32(Minute % (24 * 60)) / 60;
        Info.Minute = int32(Minute % 60);
        Info.MoneyGE = S.PlayerMoneyGE;
        Info.LifeNumber = S.LifeNumber;
        Info.SavedAt = FM.GetTimeStamp(*(Info.bFromBackup ? Path + TEXT(".bak") : Path));
    }
    return Info;
}

FString UGenesisGameInstance::MostRecentSlot()
{
    FString Best;
    FDateTime BestTime = FDateTime::MinValue();
    for (const FString& Slot : PlayerSlots()) {
        const FGenesisSlotInfo Info = DescribeSlot(Slot);
        if (Info.bValid && Info.SavedAt > BestTime) {
            BestTime = Info.SavedAt;
            Best = Slot;
        }
    }
    return Best;
}

void UGenesisGameInstance::StartNewGame(const FString& Slot)
{
    ActiveSlot = Slot;
    bLoadSlotOnStart = false;
    bNewGamePendingSave = true;          // the start save replaces the old slot content right away
    UGameplayStatics::OpenLevel(this, FName(GameplayMap));
}

void UGenesisGameInstance::LoadSlotAndPlay(const FString& Slot)
{
    ActiveSlot = Slot;
    bLoadSlotOnStart = true;
    bNewGamePendingSave = false;
    UGameplayStatics::OpenLevel(this, FName(GameplayMap));
}

void UGenesisGameInstance::ReturnToMainMenu()
{
    bBootSequenceShown = true;           // back from the game: straight to the main menu
    UGameplayStatics::SetGamePaused(this, false);
    UGameplayStatics::OpenLevel(this, FName(MenuMap));
}
