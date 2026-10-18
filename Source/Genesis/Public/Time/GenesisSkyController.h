#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "GenesisSkyController.generated.h"

class ADirectionalLight;
class APostProcessVolume;
class UDirectionalLightComponent;
class UMaterialInstanceDynamic;
class UStaticMeshComponent;
class UTexture2D;

/**
 * Koppelt Himmel und Kamerabelichtung an die Weltuhr:
 * Sonne (Stand aus Datum, Uhrzeit, Ort), Mond (Stand, Phase, Beleuchtungsstaerke als zweites Atmosphaerenlicht),
 * Sternenhimmel (NASA-SVS-Sternkarte, nach Sternzeit gedreht) mit Airglow, und Belichtung (EV100) passend zur Lichtsituation.
 * Licht bleibt physikalisch (Lux, cd/m2); die Kamera passt sich an. Wird vom GameMode erzeugt, wenn das Level keinen hat.
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

	/** Himmelsmaterial (Atmosphaere + Sterne + Airglow). */
	UPROPERTY(EditAnywhere, Category = "Genesis|Sky")
	TSoftObjectPtr<UMaterialInterface> SkyMaterial;

	double GetLastElevationDeg() const { return LastElevationDeg; }
	double GetLastAzimuthDeg() const { return LastAzimuthDeg; }
	double GetLastEV100() const { return LastEV100; }
	double GetLastMoonElevationDeg() const { return LastMoonElevationDeg; }
	double GetLastMoonAzimuthDeg() const { return LastMoonAzimuthDeg; }
	double GetLastMoonFraction() const { return LastMoonFraction; }
	double GetLastMoonLux() const { return LastMoonLux; }

private:
	void FindSceneActors();

	UPROPERTY(VisibleAnywhere, Category = "Genesis|Sky")
	TObjectPtr<UDirectionalLightComponent> MoonLight;

	UPROPERTY(VisibleAnywhere, Category = "Genesis|Sky")
	TObjectPtr<UStaticMeshComponent> SkyDome;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> SkyMID;

	double LastElevationDeg = 0.0;
	double LastAzimuthDeg = 0.0;
	double LastEV100 = 0.0;
	double LastMoonElevationDeg = 0.0;
	double LastMoonAzimuthDeg = 0.0;
	double LastMoonFraction = 0.0;
	double LastMoonLux = 0.0;
};

/** Editor-Hilfen fuer den Himmelsaufbau (z. B. Eichung der Sternkarte). */
UCLASS()
class GENESIS_API UGenesisSkyLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Mittlere Luminanz (Rec.709) der Quelldaten einer HDR-Textur, ueber den Raumwinkel gewichtet (Kugelprojektion). Nur im Editor. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Sky")
	static double MeasureEquirectMeanLuminance(UTexture2D* Texture);
};
