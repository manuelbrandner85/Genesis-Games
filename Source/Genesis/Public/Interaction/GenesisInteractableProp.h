#pragma once
#include "CoreMinimal.h"
#include "Engine/StaticMeshActor.h"
#include "GenesisInteractableProp.generated.h"

/** A world object the player can use (e.g. the customer's generator). The id is the object id
 *  used by mission logic and the world state ledger. */
UCLASS()
class GENESIS_API AGenesisInteractableProp : public AStaticMeshActor
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "Genesis") FName InteractionId;
    UPROPERTY(EditAnywhere, Category = "Genesis") FText Label;
};
