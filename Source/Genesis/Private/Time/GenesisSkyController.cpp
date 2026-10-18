#include "Time/GenesisSkyController.h"

#include "Components/DirectionalLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/PostProcessVolume.h"
#include "EngineUtils.h"
#include "Genesis.h"
#include "Time/GenesisSolar.h"
#include "Time/GenesisTimeTypes.h"
#include "Time/GenesisWorldClockSubsystem.h"

AGenesisSkyController::AGenesisSkyController()
{
	PrimaryActorTick.bCanEverTick = true;
	// Nach der Weltuhr ticken, damit Licht und Zeit im selben Frame zusammenpassen.
	PrimaryActorTick.TickGroup = TG_PostUpdateWork;
}

void AGenesisSkyController::BeginPlay()
{
	Super::BeginPlay();
	FindSceneActors();
	UpdateSky();
}

void AGenesisSkyController::FindSceneActors()
{
	if (!Sun)
	{
		for (TActorIterator<ADirectionalLight> It(GetWorld()); It; ++It)
		{
			const UDirectionalLightComponent* Light = Cast<UDirectionalLightComponent>(It->GetLightComponent());
			if (Light && Light->IsUsedAsAtmosphereSunLight())
			{
				Sun = *It;
				break;
			}
		}
	}
	if (!ExposureVolume)
	{
		for (TActorIterator<APostProcessVolume> It(GetWorld()); It; ++It)
		{
			if (It->bUnbound)
			{
				ExposureVolume = *It;
				break;
			}
		}
	}
	UE_CLOG(!Sun, LogGenesis, Warning, TEXT("SkyController: keine Sonne (DirectionalLight mit Atmosphere Sun Light) gefunden."));
	UE_CLOG(!ExposureVolume, LogGenesis, Warning, TEXT("SkyController: kein unbegrenztes PostProcessVolume fuer die Belichtung gefunden."));
}

void AGenesisSkyController::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	UpdateSky();
}

void AGenesisSkyController::UpdateSky()
{
	const UGenesisWorldClockSubsystem* Clock = GetWorld() ? GetWorld()->GetSubsystem<UGenesisWorldClockSubsystem>() : nullptr;
	if (!Clock)
	{
		return;
	}
	const UGenesisTimeSettings& Settings = *GetDefault<UGenesisTimeSettings>();

	const FDateTime Utc = FGenesisSolar::LocalToUtc(Clock->GetWorldDateTime(), Settings.StandardUtcOffsetHours, Settings.bEuSummerTime);
	const FGenesisSunPosition SunPosition = FGenesisSolar::Compute(Utc, Settings.LatitudeDeg, Settings.LongitudeDeg);
	LastElevationDeg = SunPosition.ElevationDeg;
	LastAzimuthDeg = SunPosition.AzimuthDeg;

	if (Sun)
	{
		// Das Licht zeigt von der Sonne weg: Neigung = -Hoehe, Gier = Azimut + 180 (relativ zu Welt-Nord).
		const FRotator LightRotation(-SunPosition.ElevationDeg, SunPosition.AzimuthDeg + 180.0 + Settings.WorldNorthYawDeg, 0.0);
		Sun->GetLightComponent()->SetWorldRotation(LightRotation);
	}

	LastEV100 = FGenesisSolar::GetClearSkyEV100(SunPosition.ElevationDeg) + ExposureOffsetEV;
	if (ExposureVolume)
	{
		// Manuelle Belichtung ohne physikalische Kamera: Basis ist EV100 = 0, die Korrektur wirkt als 2^Bias.
		// Damit gilt Bias = -EV100 (Engine: CalculateManualAutoExposure).
		FPostProcessSettings& PP = ExposureVolume->Settings;
		PP.bOverride_AutoExposureMethod = true;
		PP.AutoExposureMethod = AEM_Manual;
		PP.bOverride_AutoExposureApplyPhysicalCameraExposure = true;
		PP.AutoExposureApplyPhysicalCameraExposure = false;
		PP.bOverride_AutoExposureBias = true;
		PP.AutoExposureBias = float(-LastEV100);
	}
}
