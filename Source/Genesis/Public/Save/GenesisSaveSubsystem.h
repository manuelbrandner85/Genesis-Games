#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Save/GenesisSaveTypes.h"
#include "GenesisSaveSubsystem.generated.h"

/** Haelt den laufenden Soul/World/Life-Stand und speichert ihn transaktional. */
UCLASS()
class GENESIS_API UGenesisSaveSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	/** Beginnt eine neue Seele: neues SoulId, Welt 2026, erstes Leben ab der Befruchtung. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Save")
	void StartNewSoul(FName BodyAssetId);

	UFUNCTION(BlueprintCallable, Category = "Genesis|Save")
	EGenesisSaveResult SaveToSlot(const FString& Slot);

	UFUNCTION(BlueprintCallable, Category = "Genesis|Save")
	EGenesisSaveResult LoadFromSlot(const FString& Slot);

	UFUNCTION(BlueprintPure, Category = "Genesis|Save")
	const FGenesisSaveBundle& GetCurrent() const { return Current; }

	FGenesisSaveBundle& GetMutable() { return Current; }

private:
	UPROPERTY()
	FGenesisSaveBundle Current;
};
