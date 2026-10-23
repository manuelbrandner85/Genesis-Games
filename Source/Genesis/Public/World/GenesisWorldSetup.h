#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GenesisWorldSetup.generated.h"

/** Placed once per level: the start state of a new game (overwritten when a save is loaded).
 *  Values for Flussdorf are Startwerte from docs/design/G6_FLUSSDORF_WERKSTATT.md. */
UCLASS()
class GENESIS_API AGenesisWorldSetup : public AActor
{
    GENERATED_BODY()
public:
    AGenesisWorldSetup();
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Genesis|Start") int32 StartDay = 1;
    UPROPERTY(EditAnywhere, Category = "Genesis|Start") int32 StartHour = 8;
    UPROPERTY(EditAnywhere, Category = "Genesis|Start") int32 StartMinute = 30;
    UPROPERTY(EditAnywhere, Category = "Genesis|Start") int32 StartMoneyGE = 40;
    UPROPERTY(EditAnywhere, Category = "Genesis|Start") TMap<FName, int32> MarketStock;
    UPROPERTY(EditAnywhere, Category = "Genesis|Start") TMap<FName, FString> ObjectStates;
};
