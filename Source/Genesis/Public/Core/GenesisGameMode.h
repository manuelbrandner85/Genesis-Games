#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "GenesisGameMode.generated.h"

UCLASS()
class GENESIS_API AGenesisPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	AGenesisPlayerController();
};

/**
 * Standard-Spielmodus. Mit -GenesisAutoTest laeuft ein echter Spielstart-Selbsttest:
 * Die Figur geht einige Sekunden vorwaerts, die Strecke wird geloggt, ein Bildschirmfoto
 * wird gespeichert und das Spiel beendet sich.
 */
UCLASS()
class GENESIS_API AGenesisGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AGenesisGameMode();

	virtual void StartPlay() override;
	virtual void Tick(float DeltaSeconds) override;

private:
	bool bAutoTest = false;
	float AutoTestTime = 0.f;
	FVector AutoTestStart = FVector::ZeroVector;
	int32 AutoTestStage = 0;
};
