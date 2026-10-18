#include "Core/GenesisGameInstance.h"

#include "Genesis.h"
#include "Save/GenesisSaveSubsystem.h"

void UGenesisGameInstance::Init()
{
	Super::Init();
	UE_LOG(LogGenesis, Log, TEXT("GenesisGameInstance initialisiert."));
}

UGenesisSaveSubsystem* UGenesisGameInstance::GetSaveSubsystem() const
{
	return GetSubsystem<UGenesisSaveSubsystem>();
}
