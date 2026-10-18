#include "Save/GenesisSaveSubsystem.h"

#include "Genesis.h"
#include "Save/GenesisSaveStore.h"

void UGenesisSaveSubsystem::StartNewSoul(FName BodyAssetId)
{
	Current = FGenesisSaveBundle();
	Current.Soul.SoulId = FGuid::NewGuid();
	Current.World.WorldSeed = FMath::Rand();
	Current.Life.LifeIndex = 0;
	Current.Life.BodyAssetId = BodyAssetId;
	Current.Life.Stage = EGenesisLifeStage::Conception;
}

EGenesisSaveResult UGenesisSaveSubsystem::SaveToSlot(const FString& Slot)
{
	const EGenesisSaveResult Result = FGenesisSaveStore(FGenesisSaveStore::DefaultDirectory()).Save(Slot, Current);
	UE_LOG(LogGenesis, Log, TEXT("Speichern '%s' -> %s (Sequenz %lld)"),
		*Slot, *UEnum::GetValueAsString(Result), Current.Sequence);
	return Result;
}

EGenesisSaveResult UGenesisSaveSubsystem::LoadFromSlot(const FString& Slot)
{
	FGenesisSaveBundle Loaded;
	const EGenesisSaveResult Result = FGenesisSaveStore(FGenesisSaveStore::DefaultDirectory()).Load(Slot, Loaded);
	if (Result == EGenesisSaveResult::Ok)
	{
		Current = MoveTemp(Loaded);
	}
	UE_LOG(LogGenesis, Log, TEXT("Laden '%s' -> %s (Sequenz %lld)"),
		*Slot, *UEnum::GetValueAsString(Result), Current.Sequence);
	return Result;
}
