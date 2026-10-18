#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GenesisSkyController.generated.h"

class ADirectionalLight;
class APostProcessVolume;

/**
 * Koppelt Sonne und Kamerabelichtung an die Weltuhr: Sonnenstand aus Datum, Uhrzeit und Ort,
 * Belichtung (EV100) passend zur Lichtsituation. Licht bleibt physikalisch (Lux); die Kamera passt sich an.
 * Wird vom GameMode automatisch erzeugt, wenn das Level keinen eigenen hat.
 */
UCLASS()
class GENESIS_API AGenesisSkyController : public AActor
{
	GENERATED_BODY()

public:
	AGenesisSkyController();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	/** Sofort auf den aktuellen Weltzeitpunkt setzen. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Sky")
	void UpdateSky();

	UPROPERTY(EditAnywhere, Category = "Genesis|Sky")
	TObjectPtr<ADirectionalLight> Sun;

	UPROPERTY(EditAnywhere, Category = "Genesis|Sky")
	TObjectPtr<APostProcessVolume> ExposureVolume;

	/** Zusaetzliche Belichtungskorrektur in Blendenstufen (z. B. fuer Wetter, spaeter). */
	UPROPERTY(EditAnywhere, Category = "Genesis|Sky")
	float ExposureOffsetEV = 0.f;

	double GetLastElevationDeg() const { return LastElevationDeg; }
	double GetLastAzimuthDeg() const { return LastAzimuthDeg; }
	double GetLastEV100() const { return LastEV100; }

private:
	void FindSceneActors();

	double LastElevationDeg = 0.0;
	double LastAzimuthDeg = 0.0;
	double LastEV100 = 0.0;
};
