#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "GenesisMenuGameMode.generated.h"

class ACameraActor;
class UGenesisMenuWidget;

/** Main menu map: no player figure, no world simulation, no save writes - only the menu over a
 *  slowly drifting camera shot of the workshop (non-persistent background, MENU_FLOW constraint). */
UCLASS()
class GENESIS_API AGenesisMenuGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AGenesisMenuGameMode();
};

UCLASS()
class GENESIS_API AGenesisMenuPlayerController : public APlayerController
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void PlayerTick(float DeltaTime) override;
    UGenesisMenuWidget* GetMenu() const { return Menu; }

private:
    UPROPERTY() TObjectPtr<UGenesisMenuWidget> Menu;
    UPROPERTY() TObjectPtr<ACameraActor> MenuCamera;
    FTransform CameraStart;
    float Time = 0.f;
};
