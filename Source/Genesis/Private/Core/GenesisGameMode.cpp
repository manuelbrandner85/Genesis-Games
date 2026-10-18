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
