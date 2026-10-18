#include "Core/GenesisGameMode.h"

#include "Camera/PlayerCameraManager.h"
#include "Character/GenesisCharacter.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Genesis.h"
#include "HAL/PlatformMisc.h"
#include "Misc/CommandLine.h"
#include "Misc/Paths.h"
#include "Save/GenesisSaveSubsystem.h"
#include "EngineUtils.h"
#include "Time/GenesisSkyController.h"
#include "Time/GenesisWorldClockSubsystem.h"
#include "Engine/GameInstance.h"
#include "UnrealClient.h"

AGenesisPlayerController::AGenesisPlayerController()
{
	PlayerCameraManagerClass = APlayerCameraManager::StaticClass();
}

AGenesisGameMode::AGenesisGameMode()
{
	DefaultPawnClass = AGenesisCharacter::StaticClass();
	PlayerControllerClass = AGenesisPlayerController::StaticClass();
	PrimaryActorTick.bCanEverTick = true;
}

void AGenesisGameMode::StartPlay()
{
	Super::StartPlay();

	if (UGenesisSaveSubsystem* Save = GetGameInstance() ? GetGameInstance()->GetSubsystem<UGenesisSaveSubsystem>() : nullptr)
	{
		if (!Save->HasActiveSoul())
		{
			// Testprofil fuer das Graubox-Level, kein Kanon: Erwachsener, 30 Jahre, Sommervormittag 2026.
			Save->StartTestLife(TEXT("CHR_PLAYER_ADULT"), FDateTime(2026, 6, 15, 10, 0, 0), 30.f);
		}
	}

	if (APlayerController* PC = GetWorld()->GetFirstPlayerController())
	{
		if (PC->PlayerCameraManager)
		{
			// Natuerlicher Blickbereich: nicht senkrecht nach oben/unten.
			PC->PlayerCameraManager->ViewPitchMin = -70.f;
			PC->PlayerCameraManager->ViewPitchMax = 55.f;
		}
	}

	// Himmel an die Weltuhr koppeln, wenn das Level keinen eigenen Controller hat.
	if (!TActorIterator<AGenesisSkyController>(GetWorld()))
	{
		GetWorld()->SpawnActor<AGenesisSkyController>();
	}

	FString ShotTimes;
	if (FParse::Value(FCommandLine::Get(), TEXT("GenesisSkyShots="), ShotTimes, /*bShouldStopOnSeparator*/ false))
	{
		// Format: -GenesisSkyShots=0700,1320,2100,2330 (Ortszeit am Testdatum)
		ShotTimes.ParseIntoArray(SkyShotTimes, TEXT(","));
		FString DateText;
		SkyShotDate = FDateTime(2026, 6, 15);
		if (FParse::Value(FCommandLine::Get(), TEXT("GenesisSkyDate="), DateText))
		{
			FDateTime::ParseIso8601(*DateText, SkyShotDate);
		}
		if (APlayerController* ShotPC = GetWorld()->GetFirstPlayerController())
		{
			ShotPC->SetIgnoreLookInput(true);
			ShotPC->SetIgnoreMoveInput(true);
		}
		// -GenesisShotWarmup=<s>: Vorlauf vor dem ersten Bild (Shader, Streaming, NPC-Wege).
		FParse::Value(FCommandLine::Get(), TEXT("GenesisShotWarmup="), SkyShotWarmup);
		UE_LOG(LogGenesis, Display, TEXT("GENESIS_SKYSHOTS gestartet: %d Zeitpunkte am %s"), SkyShotTimes.Num(), *SkyShotDate.ToString(TEXT("%Y-%m-%d")));
	}

	bAutoTest = FParse::Param(FCommandLine::Get(), TEXT("GenesisAutoTest"));
	if (bAutoTest)
	{
		UE_LOG(LogGenesis, Display, TEXT("GENESIS_AUTOTEST gestartet"));
		if (APlayerController* AutoPC = GetWorld()->GetFirstPlayerController())
		{
			// Echte Mausbewegungen duerfen den Selbsttest nicht verfaelschen.
			AutoPC->SetIgnoreLookInput(true);
		}
	}
}

void AGenesisGameMode::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (SkyShotTimes.Num() > 0)
	{
		TickSkyShots(DeltaSeconds);
		return;
	}
	if (!bAutoTest)
	{
		return;
	}

	APlayerController* PC = GetWorld()->GetFirstPlayerController();
	AGenesisCharacter* Character = PC ? Cast<AGenesisCharacter>(PC->GetPawn()) : nullptr;
	if (!Character)
	{
		return;
	}

	AutoTestTime += DeltaSeconds;
	switch (AutoTestStage)
	{
	case 0: // Shader/Streaming beruhigen lassen.
		if (AutoTestTime > 4.f)
		{
			AutoTestStart = Character->GetActorLocation();
			AutoTestStage = 1;
			AutoTestTime = 0.f;
		}
		break;
	case 1: // Drei Sekunden vorwaerts gehen, wie mit gedrueckter W-Taste.
		Character->AddMovementInput(Character->GetActorForwardVector(), 1.f);
		if (AutoTestTime > 3.f)
		{
			const FVector End = Character->GetActorLocation();
			UE_LOG(LogGenesis, Display, TEXT("GENESIS_AUTOTEST id=%s mesh=%s distance_cm=%.1f speed_cm_s=%.1f grounded=%d"),
				*Character->CharacterAssetId.ToString(), *GetNameSafe(Character->GetMesh()->GetSkeletalMeshAsset()),
				FVector::Dist2D(AutoTestStart, End), Character->GetVelocity().Size2D(), Character->GetCharacterMovement()->IsMovingOnGround() ? 1 : 0);
			const USkeletalMeshComponent* MeshComp = Character->GetMesh();
			UE_LOG(LogGenesis, Display, TEXT("GENESIS_AUTOTEST mesh_loc=%s bounds=%s visible=%d hidden=%d render=%d materials=%d mat0=%s anim=%s camera=%s"),
				*MeshComp->GetComponentLocation().ToString(), *MeshComp->Bounds.BoxExtent.ToString(),
				MeshComp->IsVisible() ? 1 : 0, MeshComp->bHiddenInGame ? 1 : 0, MeshComp->IsRenderStateCreated() ? 1 : 0,
				MeshComp->GetNumMaterials(), *GetNameSafe(MeshComp->GetMaterial(0)), *GetNameSafe(MeshComp->GetAnimInstance()),
				*PC->PlayerCameraManager->GetCameraLocation().ToString());
			const FString Shot = FPaths::ProjectSavedDir() / TEXT("Automation/WK-M02-002/autotest_shot.png");
			FScreenshotRequest::RequestScreenshot(Shot, false, false);
			AutoTestStage = 2;
			AutoTestTime = 0.f;
		}
		break;
	case 2:
		if (AutoTestTime > 1.5f)
		{
			UE_LOG(LogGenesis, Display, TEXT("GENESIS_AUTOTEST beendet"));
			FPlatformMisc::RequestExit(false, TEXT("GenesisAutoTest"));
			AutoTestStage = 3;
		}
		break;
	default:
		break;
	}
}

void AGenesisGameMode::TickSkyShots(float DeltaSeconds)
{
	UWorld* World = GetWorld();
	APlayerController* PC = World->GetFirstPlayerController();
	UGenesisSaveSubsystem* Save = GetGameInstance()->GetSubsystem<UGenesisSaveSubsystem>();
	UGenesisWorldClockSubsystem* Clock = World->GetSubsystem<UGenesisWorldClockSubsystem>();
	AGenesisSkyController* Sky = nullptr;
	for (TActorIterator<AGenesisSkyController> It(World); It; ++It)
	{
		Sky = *It;
	}
	if (!PC || !PC->GetPawn() || !Save || !Clock || !Sky)
	{
		return;
	}

	SkyShotTimer += DeltaSeconds;
	const bool bFirst = SkyShotIndex == 0 && SkyShotStage == 0;
	switch (SkyShotStage)
	{
	case 0: // Zeitpunkt einstellen. Erster Zeitpunkt wartet laenger (Shader, Streaming).
		if (SkyShotTimer < (bFirst ? SkyShotWarmup : 0.f))
		{
			return;
		}
		{
			// Eintrag: [JJJJMMTT-]HHMM[@Gier[/Neigung]], Gier "moon" = Richtung des Mondes.
			FString TimePart, ViewPart;
			if (!SkyShotTimes[SkyShotIndex].Split(TEXT("@"), &TimePart, &ViewPart))
			{
				TimePart = SkyShotTimes[SkyShotIndex];
			}
			FDateTime Date = SkyShotDate;
			FString Hhmm = TimePart;
			FString Ymd;
			if (TimePart.Split(TEXT("-"), &Ymd, &Hhmm))
			{
				Date = FDateTime(FCString::Atoi(*Ymd.Left(4)), FCString::Atoi(*Ymd.Mid(4, 2)), FCString::Atoi(*Ymd.Mid(6, 2)));
			}
			Save->GetMutable().World.WorldDateTime = Date + FTimespan(FCString::Atoi(*Hhmm.Left(2)), FCString::Atoi(*Hhmm.Mid(2, 2)), 0);
			Clock->SetClockRunning(false);
			Sky->UpdateSky();

			// Standard: West-Suedwest, leicht nach unten (Figur, Treppe, Horizont im Bild).
			FString YawText = TEXT("250"), PitchText = TEXT("-6");
			if (!ViewPart.IsEmpty() && !ViewPart.Split(TEXT("/"), &YawText, &PitchText))
			{
				YawText = ViewPart;
			}
			const float Yaw = YawText == TEXT("moon") ? float(Sky->GetLastMoonAzimuthDeg()) : FCString::Atof(*YawText);
			PC->SetControlRotation(FRotator(FCString::Atof(*PitchText), Yaw, 0.f));
			SkyShotName = ViewPart.IsEmpty() ? TimePart : TimePart + TEXT("_") + ViewPart.Replace(TEXT("/"), TEXT("_"));
			SkyShotStage = 1;
			SkyShotTimer = 0.f;
		}
		return;
	case 1: // Lumen, Himmelslicht-Erfassung und Schatten einschwingen lassen.
		if (SkyShotTimer > 4.f)
		{
			UE_LOG(LogGenesis, Display, TEXT("GENESIS_SKYSHOT shot=%s local=%s sun_el=%.2f sun_az=%.2f moon_el=%.2f moon_az=%.2f moon_frac=%.3f moon_lux=%.4f ev100=%.2f"),
				*SkyShotName, *Clock->GetWorldDateTime().ToString(), Sky->GetLastElevationDeg(), Sky->GetLastAzimuthDeg(),
				Sky->GetLastMoonElevationDeg(), Sky->GetLastMoonAzimuthDeg(), Sky->GetLastMoonFraction(), Sky->GetLastMoonLux(), Sky->GetLastEV100());
			FString ShotDir = TEXT("WK-M02-006");
			FParse::Value(FCommandLine::Get(), TEXT("GenesisShotDir="), ShotDir);
			FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir() / TEXT("Automation") / ShotDir / FString::Printf(TEXT("sky_%s.png"), *SkyShotName), false, false);
			SkyShotStage = 2;
			SkyShotTimer = 0.f;
		}
		return;
	case 2: // Bildschirmfoto abwarten, naechster Zeitpunkt.
		if (SkyShotTimer > 1.f)
		{
			++SkyShotIndex;
			SkyShotStage = 0;
			SkyShotTimer = 0.f;
			if (SkyShotIndex >= SkyShotTimes.Num())
			{
				UE_LOG(LogGenesis, Display, TEXT("GENESIS_SKYSHOTS beendet"));
				SkyShotTimes.Reset();
				FPlatformMisc::RequestExit(false, TEXT("GenesisSkyShots"));
			}
		}
		return;
	default:
		return;
	}
}
