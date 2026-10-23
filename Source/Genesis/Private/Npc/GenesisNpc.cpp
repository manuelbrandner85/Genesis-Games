#include "Npc/GenesisNpc.h"

#include "Causality/GenesisNpcMemoryComponent.h"
#include "Components/StateTreeAIComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Genesis.h"
#include "Npc/GenesisNpcTypes.h"
#include "SmartObjectComponent.h"
#include "StateTree.h"
#include "Time/GenesisSkyController.h"
#include "Time/GenesisWorldClockSubsystem.h"

AGenesisNpcCharacter::AGenesisNpcCharacter()
{
	AIControllerClass = AGenesisNpcAIController::StaticClass();
	AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
	WalkSpeed = 140.f;
	Memory = CreateDefaultSubobject<UGenesisNpcMemoryComponent>(TEXT("Memory"));
}

void AGenesisNpcCharacter::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	Memory->NpcId = CharacterAssetId;
}

void AGenesisNpcCharacter::BeginPlay()
{
	Super::BeginPlay();
	Memory->NpcId = CharacterAssetId;
	GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
}

FName AGenesisNpcCharacter::GetScheduledActivity() const
{
	if (!ReactionActivity.IsNone())
	{
		return ReactionActivity;
	}
	const UGenesisWorldClockSubsystem* Clock = GetWorld() ? GetWorld()->GetSubsystem<UGenesisWorldClockSubsystem>() : nullptr;
	const float Hour = Clock ? Clock->GetTimeOfDayHours() : 12.f;
	return GetDefault<UGenesisNpcSettings>()->GetActivity(CharacterAssetId, Hour);
}

AGenesisNpcAIController::AGenesisNpcAIController()
{
	StateTree = CreateDefaultSubobject<UStateTreeAIComponent>(TEXT("StateTree"));
	StateTree->SetStartLogicAutomatically(false);
}

void AGenesisNpcAIController::OnPossess(APawn* InPawn)
{
	Super::OnPossess(InPawn);
	UStateTree* Tree = GetDefault<UGenesisNpcSettings>()->DailyLifeStateTree.LoadSynchronous();
	if (!Tree)
	{
		UE_LOG(LogGenesis, Error, TEXT("NPC %s: kein Tagesablauf-StateTree in den Projekteinstellungen."), *GetNameSafe(InPawn));
		return;
	}
	StateTree->SetStateTree(Tree);
	StateTree->StartLogic();
}

AGenesisActivitySpot::AGenesisActivitySpot()
{
	// Eigene unskalierte Wurzel: die Moebelgroesse (Visual) darf die Slot-Positionen nicht mitskalieren.
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	Visual = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Visual"));
	Visual->SetupAttachment(RootComponent);
	SmartObject = CreateDefaultSubobject<USmartObjectComponent>(TEXT("SmartObject"));
	SmartObject->SetupAttachment(RootComponent);
}

void AGenesisActivitySpot::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	ApplyDefinition();
}

void AGenesisActivitySpot::ApplyDefinition()
{
	if (Definition && SmartObject->GetDefinition() != Definition)
	{
		SmartObject->SetDefinition(Definition);
	}
}

float FGenesisPerception::GetSightRange(const UWorld* World)
{
	const UGenesisNpcSettings& Settings = *GetDefault<UGenesisNpcSettings>();
	double EV = 15.0;
	for (TActorIterator<AGenesisSkyController> It(const_cast<UWorld*>(World)); It; ++It)
	{
		EV = It->GetLastEV100();
		break;
	}
	const float Alpha = FMath::Clamp(float((EV + 3.0) / 13.0), 0.f, 1.f);
	return FMath::Lerp(Settings.SightRangeNightCm, Settings.SightRangeDayCm, Alpha);
}

TArray<FName> FGenesisPerception::FindWitnesses(const UWorld* World, const FVector& Location, const AActor* IgnoreActor, const TArray<FName>& ExcludeIds)
{
	TArray<FName> Witnesses;
	if (!World)
	{
		return Witnesses;
	}
	const float Range = GetSightRange(World);
	const float CosHalfFov = FMath::Cos(FMath::DegreesToRadians(GetDefault<UGenesisNpcSettings>()->HalfFieldOfViewDeg));
	const FVector Target = Location + FVector(0.f, 0.f, 100.f); // Oberkoerperhoehe des Geschehens

	for (TActorIterator<AGenesisNpcCharacter> It(const_cast<UWorld*>(World)); It; ++It)
	{
		AGenesisNpcCharacter* Npc = *It;
		if (ExcludeIds.Contains(Npc->GetNpcId()) || Npc == IgnoreActor)
		{
			continue;
		}
		const FVector Eye = Npc->GetPawnViewLocation();
		const FVector ToTarget = Target - Eye;
		if (ToTarget.Size() > Range)
		{
			continue;
		}
		if ((Npc->GetActorForwardVector() | ToTarget.GetSafeNormal2D()) < CosHalfFov)
		{
			continue;
		}
		FCollisionQueryParams Params(SCENE_QUERY_STAT(GenesisWitness), false, Npc);
		if (IgnoreActor)
		{
			Params.AddIgnoredActor(IgnoreActor);
		}
		FHitResult Hit;
		if (World->LineTraceSingleByChannel(Hit, Eye, Target, ECC_Visibility, Params))
		{
			continue;
		}
		Witnesses.Add(Npc->GetNpcId());
	}
	return Witnesses;
}
