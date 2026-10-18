#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "GenesisGameInstance.generated.h"

class UGenesisSaveSubsystem;

UCLASS()
class GENESIS_API UGenesisGameInstance : public UGameInstance
{
	GENERATED_BODY()

public:
	virtual void Init() override;

	UFUNCTION(BlueprintPure, Category = "Genesis")
	UGenesisSaveSubsystem* GetSaveSubsystem() const;
};
