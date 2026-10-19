#include "Character/GenesisCharacter.h"

#include "Camera/CameraComponent.h"
#include "Character/GenesisCharacterAppearance.h"
#include "Character/GenesisCharacterRegistry.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "Engine/SkeletalMesh.h"
#include "Genesis.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "Input/GenesisInputSet.h"
#include "EngineUtils.h"
#include "Engine/GameInstance.h"
#include "Npc/GenesisNpc.h"
#include "Story/GenesisStory.h"
#include "InputActionValue.h"
#include "Materials/MaterialInterface.h"
#include "PhysicsEngine/PhysicsAsset.h"

AGenesisCharacter::AGenesisCharacter()
{
	GetCapsuleComponent()->InitCapsuleSize(34.f, 90.f);

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->bOrientRotationToMovement = true;
	Movement->RotationRate = FRotator(0.f, 420.f, 0.f);
	Movement->MaxWalkSpeed = WalkSpeed;
	Movement->MinAnalogWalkSpeed = 20.f;
	Movement->BrakingDecelerationWalking = 1400.f;
	Movement->GroundFriction = 8.f;
	// Realistischer Standsprung, ca. 45 cm Steighoehe.
	Movement->JumpZVelocity = 300.f;
	Movement->AirControl = 0.2f;
	Movement->BrakingDecelerationFalling = 1500.f;
	Movement->MaxStepHeight = 40.f;
	Movement->SetWalkableFloorAngle(44.f);
	// Alle Figuren (auch die Spielfigur) weichen einander aus.
	Movement->bUseRVOAvoidance = true;
	Movement->AvoidanceConsiderationRadius = 200.f;

	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 280.f;
	CameraBoom->SocketOffset = FVector(0.f, 45.f, 0.f);
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->bDoCollisionTest = true;
	CameraBoom->ProbeSize = 14.f;
	CameraBoom->bEnableCameraLag = true;
	CameraBoom->CameraLagSpeed = 14.f;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;
	FollowCamera->SetFieldOfView(70.f);
}

void AGenesisCharacter::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	if (!CharacterAssetId.IsNone())
	{
		ApplyAppearance(CharacterAssetId);
	}
}

void AGenesisCharacter::BeginPlay()
{
	Super::BeginPlay();
	if (!ActiveAppearance && !CharacterAssetId.IsNone())
	{
		ApplyAppearance(CharacterAssetId);
	}
	GetCharacterMovement()->MaxWalkSpeed = bRunning ? RunSpeed : WalkSpeed;
}

bool AGenesisCharacter::ApplyAppearance(FName InCharacterAssetId)
{
	const FGenesisCharacterRegistryEntry* Entry = UGenesisCharacterRegistry::FindEntry(InCharacterAssetId);
	if (!Entry)
	{
		return false;
	}
	TArray<FString> Errors;
	if (!TryApplyAppearanceAsset(Entry->Appearance.LoadSynchronous(), Entry->Contract, Errors))
	{
		return false;
	}
	CharacterAssetId = InCharacterAssetId;
	return true;
}

bool AGenesisCharacter::TryApplyAppearanceAsset(UGenesisCharacterAppearance* Appearance, const FGenesisProportionContract& Contract, TArray<FString>& OutErrors)
{
	if (!UGenesisCharacterRegistry::ValidateAppearance(Appearance, Contract, OutErrors))
	{
		for (const FString& Error : OutErrors)
		{
			UE_LOG(LogGenesis, Error, TEXT("Figur '%s': Austausch abgelehnt: %s"), *CharacterAssetId.ToString(), *Error);
		}
		return false;
	}
	USkeletalMesh* SkeletalMesh = Appearance->Mesh.LoadSynchronous();

	USkeletalMeshComponent* MeshComponent = GetMesh();
	MeshComponent->SetSkeletalMeshAsset(SkeletalMesh);
	MeshComponent->EmptyOverrideMaterials();
	for (int32 Slot = 0; Slot < Appearance->MaterialOverrides.Num(); ++Slot)
	{
		if (UMaterialInterface* Material = Appearance->MaterialOverrides[Slot].LoadSynchronous())
		{
			MeshComponent->SetMaterial(Slot, Material);
		}
	}
	if (UPhysicsAsset* Physics = Appearance->PhysicsAssetOverride.LoadSynchronous())
	{
		MeshComponent->SetPhysicsAsset(Physics);
	}
	MeshComponent->SetAnimationMode(EAnimationMode::AnimationBlueprint);
	MeshComponent->SetAnimInstanceClass(Appearance->AnimClass.LoadSynchronous());

	GetCapsuleComponent()->SetCapsuleSize(Appearance->CapsuleRadius, Appearance->CapsuleHalfHeight);
	MeshComponent->SetRelativeTransform(Appearance->MeshRelativeTransform);

	// Die Kamera haengt am Vertragswert, nicht am Mesh: ein neues Modell veraendert die Kameraposition nicht.
	CameraBoom->SetRelativeLocation(FVector(0.f, 0.f, Contract.AnchorHeightCm - Appearance->CapsuleHalfHeight));

	ActiveAppearance = Appearance;
	return true;
}

void AGenesisCharacter::SetRunning(bool bInRunning)
{
	bRunning = bInRunning;
	GetCharacterMovement()->MaxWalkSpeed = bRunning ? RunSpeed : WalkSpeed;
}

void AGenesisCharacter::EnsureInputSet()
{
	if (!InputSet)
	{
		InputSet = UGenesisInputSet::CreateDefault(this);
	}
}

void AGenesisCharacter::AddMappingContext()
{
	const APlayerController* PC = Cast<APlayerController>(Controller);
	const ULocalPlayer* LocalPlayer = PC ? PC->GetLocalPlayer() : nullptr;
	if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(LocalPlayer))
	{
		EnsureInputSet();
		if (!Subsystem->HasMappingContext(InputSet->Context))
		{
			Subsystem->AddMappingContext(InputSet->Context, 0);
		}
	}
}

void AGenesisCharacter::NotifyControllerChanged()
{
	Super::NotifyControllerChanged();
	AddMappingContext();
}

void AGenesisCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	EnsureInputSet();

	UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!Input)
	{
		UE_LOG(LogGenesis, Error, TEXT("EnhancedInputComponent fehlt; Steuerung nicht gebunden."));
		return;
	}

	Input->BindAction(InputSet->Move, ETriggerEvent::Triggered, this, &AGenesisCharacter::HandleMove);
	Input->BindAction(InputSet->Look, ETriggerEvent::Triggered, this, &AGenesisCharacter::HandleLook);
	Input->BindAction(InputSet->Jump, ETriggerEvent::Started, this, &ACharacter::Jump);
	Input->BindAction(InputSet->Jump, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
	Input->BindActionValueLambda(InputSet->RunHold, ETriggerEvent::Started, [this](const FInputActionValue&) { SetRunning(true); });
	Input->BindActionValueLambda(InputSet->RunHold, ETriggerEvent::Completed, [this](const FInputActionValue&) { SetRunning(false); });
	Input->BindAction(InputSet->RunToggle, ETriggerEvent::Started, this, &AGenesisCharacter::HandleRunToggle);
	Input->BindActionValueLambda(InputSet->Interact, ETriggerEvent::Started, [this](const FInputActionValue&) { TryInteract(); });
	for (int32 i = 0; i < InputSet->Choices.Num(); ++i)
	{
		Input->BindActionValueLambda(InputSet->Choices[i], ETriggerEvent::Started, [this, i](const FInputActionValue&)
		{
			if (UGenesisStorySubsystem* Story = GetGameInstance() ? GetGameInstance()->GetSubsystem<UGenesisStorySubsystem>() : nullptr)
			{
				Story->Choose(i);
			}
		});
	}
}

void AGenesisCharacter::HandleMove(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	if (!Controller)
	{
		return;
	}
	const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
	const FRotationMatrix YawMatrix(Yaw);
	AddMovementInput(YawMatrix.GetUnitAxis(EAxis::X), Axis.Y);
	AddMovementInput(YawMatrix.GetUnitAxis(EAxis::Y), Axis.X);
}

void AGenesisCharacter::HandleLook(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	AddControllerYawInput(Axis.X);
	AddControllerPitchInput(Axis.Y);
}

void AGenesisCharacter::HandleRunToggle(const FInputActionValue&)
{
	SetRunning(!bRunning);
}

bool AGenesisCharacter::TryInteract()
{
	UGenesisStorySubsystem* Story = GetGameInstance() ? GetGameInstance()->GetSubsystem<UGenesisStorySubsystem>() : nullptr;
	if (!Story || Story->IsInDialog())
	{
		return false;
	}
	// Naechste Figur vor dem Spieler innerhalb der Reichweite.
	const float Range = GetDefault<UGenesisStorySettings>()->InteractRangeCm;
	AGenesisNpcCharacter* Best = nullptr;
	float BestDistance = Range;
	for (TActorIterator<AGenesisNpcCharacter> It(GetWorld()); It; ++It)
	{
		const FVector ToNpc = It->GetActorLocation() - GetActorLocation();
		const float Distance = ToNpc.Size2D();
		if (Distance <= BestDistance && (GetActorForwardVector() | ToNpc.GetSafeNormal2D()) > 0.3f)
		{
			Best = *It;
			BestDistance = Distance;
		}
	}
	return Best && Story->InteractWith(Best->GetNpcId());
}
