#include "Time/GenesisSkyController.h"

#include "Components/DirectionalLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/StaticMesh.h"
#include "Engine/Texture2D.h"
#include "EngineUtils.h"
#include "Genesis.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/CommandLine.h"
#include "Time/GenesisSolar.h"
#include "Time/GenesisTimeTypes.h"
#include "Time/GenesisWorldClockSubsystem.h"

AGenesisSkyController::AGenesisSkyController()
{
	PrimaryActorTick.bCanEverTick = true;
	// Nach der Weltuhr ticken, damit Licht und Zeit im selben Frame zusammenpassen.
	PrimaryActorTick.TickGroup = TG_PostUpdateWork;

	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));

	// Mond als zweites Atmosphaerenlicht: die Atmosphaere daempft und faerbt es wie die Sonne.
	MoonLight = CreateDefaultSubobject<UDirectionalLightComponent>(TEXT("MoonLight"));
	MoonLight->SetupAttachment(RootComponent);
	MoonLight->SetMobility(EComponentMobility::Movable);
	MoonLight->SetAtmosphereSunLight(true);
	MoonLight->SetAtmosphereSunLightIndex(1);
	MoonLight->LightSourceAngle = 0.5244f; // scheinbarer Monddurchmesser
	MoonLight->bUseTemperature = true;
	MoonLight->Temperature = 4100.f;       // Mondlicht ist reflektiertes, leicht roetlicheres Sonnenlicht
	MoonLight->Intensity = 0.f;

	SkyDome = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SkyDome"));
	SkyDome->SetupAttachment(RootComponent);
	SkyDome->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	SkyDome->CastShadow = false;
	SkyDome->bAffectDistanceFieldLighting = false;
	SkyDome->SetRelativeScale3D(FVector(4000.0));

	SkyMaterial = TSoftObjectPtr<UMaterialInterface>(FSoftObjectPath(TEXT("/Game/Genesis/Sky/M_GenesisSky.M_GenesisSky")));
}

void AGenesisSkyController::BeginPlay()
{
	Super::BeginPlay();
	FindSceneActors();

	UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/EngineSky/SM_SkySphere.SM_SkySphere"));
	UMaterialInterface* Material = SkyMaterial.LoadSynchronous();
	if (Sphere && Material)
	{
		SkyDome->SetStaticMesh(Sphere);
		SkyMID = UMaterialInstanceDynamic::Create(Material, this);
		SkyDome->SetMaterial(0, SkyMID);
	}
	else
	{
		UE_LOG(LogGenesis, Warning, TEXT("SkyController: Himmelskuppel oder Material '%s' fehlt; kein Sternenhimmel."), *SkyMaterial.ToString());
	}
	UpdateSky();
}

void AGenesisSkyController::FindSceneActors()
{
	if (!Sun)
	{
		for (TActorIterator<ADirectionalLight> It(GetWorld()); It; ++It)
		{
			const UDirectionalLightComponent* Light = Cast<UDirectionalLightComponent>(It->GetLightComponent());
			if (Light && Light->IsUsedAsAtmosphereSunLight() && Light->GetAtmosphereSunLightIndex() == 0)
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

	// Licht zeigt von der Quelle weg: Neigung = -Hoehe, Gier = Azimut + 180 (relativ zu Welt-Nord).
	auto LightRotation = [&Settings](double ElevationDeg, double AzimuthDeg)
	{
		return FRotator(-ElevationDeg, AzimuthDeg + 180.0 + Settings.WorldNorthYawDeg, 0.0);
	};

	const FGenesisSunPosition SunPosition = FGenesisSolar::Compute(Utc, Settings.LatitudeDeg, Settings.LongitudeDeg);
	LastElevationDeg = SunPosition.ElevationDeg;
	LastAzimuthDeg = SunPosition.AzimuthDeg;
	if (Sun)
	{
		Sun->GetLightComponent()->SetWorldRotation(LightRotation(SunPosition.ElevationDeg, SunPosition.AzimuthDeg));
	}

	const FGenesisMoonState Moon = FGenesisSolar::ComputeMoon(Utc, Settings.LatitudeDeg, Settings.LongitudeDeg);
	LastMoonElevationDeg = Moon.ElevationDeg;
	LastMoonAzimuthDeg = Moon.AzimuthDeg;
	LastMoonFraction = Moon.IlluminatedFraction;
	LastMoonLux = Moon.IlluminanceLux;
	MoonLight->SetWorldRotation(LightRotation(Moon.ElevationDeg, Moon.AzimuthDeg));
	MoonLight->SetIntensity(float(Moon.IlluminanceLux));

	if (SkyMID)
	{
		// Sternkarte nach Sternzeit drehen; Welt-Nord kann im Level gedreht sein.
		const FGenesisCelestialBasis Basis = FGenesisSolar::GetCelestialBasis(Utc, Settings.LatitudeDeg, Settings.LongitudeDeg);
		const FRotator North(0.f, Settings.WorldNorthYawDeg, 0.f);
		SkyMID->SetVectorParameterValue(TEXT("AxisRA0"), FLinearColor(North.RotateVector(Basis.AxisRA0)));
		SkyMID->SetVectorParameterValue(TEXT("AxisRA18"), FLinearColor(North.RotateVector(Basis.AxisRA18)));
		SkyMID->SetVectorParameterValue(TEXT("AxisPole"), FLinearColor(North.RotateVector(Basis.AxisPole)));
		// -GenesisNoTwilightGlow: nur Unreals Atmosphaere, zum Vermessen der Daemmerung.
		static const bool bNoTwilightGlow = FParse::Param(FCommandLine::Get(), TEXT("GenesisNoTwilightGlow"));
		SkyMID->SetScalarParameterValue(TEXT("TwilightZenithLuminance"), bNoTwilightGlow ? 0.f : float(FGenesisSolar::GetTwilightZenithLuminance(SunPosition.ElevationDeg)));
		const FVector SunHorizontal = North.RotateVector(FRotator(0.0, SunPosition.AzimuthDeg, 0.0).Vector());
		SkyMID->SetVectorParameterValue(TEXT("SunHorizontalDir"), FLinearColor(SunHorizontal));
	}

	LastEV100 = FGenesisSolar::CombineEV100(FGenesisSolar::GetClearSkyEV100(SunPosition.ElevationDeg), FGenesisSolar::GetMoonEV100(Moon)) + ExposureOffsetEV;
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

double UGenesisSkyLibrary::MeasureEquirectMeanLuminance(UTexture2D* Texture)
{
#if WITH_EDITORONLY_DATA
	if (!Texture || Texture->Source.GetFormat() != TSF_RGBA16F)
	{
		UE_LOG(LogGenesis, Error, TEXT("MeasureEquirectMeanLuminance: RGBA16F-Quelldaten erwartet."));
		return -1.0;
	}
	TArray64<uint8> Data;
	Texture->Source.GetMipData(Data, 0);
	const int32 Width = Texture->Source.GetSizeX();
	const int32 Height = Texture->Source.GetSizeY();
	const FFloat16Color* Pixels = reinterpret_cast<const FFloat16Color*>(Data.GetData());

	// Jede Bildzeile ueber cos(Breite) gewichten: Zeilen nahe den Polen decken weniger Raumwinkel ab.
	double WeightedSum = 0.0;
	double WeightSum = 0.0;
	for (int32 Y = 0; Y < Height; ++Y)
	{
		const double Weight = FMath::Cos(((Y + 0.5) / Height - 0.5) * PI);
		double RowSum = 0.0;
		for (int32 X = 0; X < Width; ++X)
		{
			const FFloat16Color& P = Pixels[int64(Y) * Width + X];
			RowSum += 0.2126 * P.R.GetFloat() + 0.7152 * P.G.GetFloat() + 0.0722 * P.B.GetFloat();
		}
		WeightedSum += RowSum * Weight;
		WeightSum += Width * Weight;
	}
	return WeightedSum / WeightSum;
#else
	return -1.0;
#endif
}
