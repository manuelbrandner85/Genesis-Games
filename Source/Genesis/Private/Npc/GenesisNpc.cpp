#include "Npc/GenesisNpc.h"
#include "Npc/GenesisNpcController.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"

AGenesisNpc::AGenesisNpc()
{
    GetCapsuleComponent()->InitCapsuleSize(42.f, 96.f);
    GetMesh()->SetRelativeLocationAndRotation(FVector(0.f, 0.f, -96.f), FRotator(0.f, -90.f, 0.f));
    AIControllerClass = AGenesisNpcController::StaticClass();
    AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
    bUseControllerRotationYaw = false;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0.f, 360.f, 0.f);
    GetCharacterMovement()->bUseRVOAvoidance = true;
}

void AGenesisNpc::BeginPlay()
{
    Super::BeginPlay();
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
    if (UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>()) {
        EventHandle = WS->OnWorldEvent.AddUObject(this, &AGenesisNpc::HandleWorldEvent);
    }
}

void AGenesisNpc::EndPlay(const EEndPlayReason::Type Reason)
{
    if (UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>()) {
        WS->OnWorldEvent.Remove(EventHandle);
    }
    Super::EndPlay(Reason);
}

void AGenesisNpc::SetInsidePrivate(bool bInside)
{
    if (bInsidePrivate == bInside) {
        return;
    }
    bInsidePrivate = bInside;
    SetActorHiddenInGame(bInside);
    SetActorEnableCollision(!bInside);
}

bool AGenesisNpc::CanPerceive(const FVector& Location, const AActor* Subject) const
{
    if (bInsidePrivate || FVector::Dist(GetActorLocation(), Location) > PerceptionRadius) {
        return false;
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(GenesisNpcSight), false, this);
    if (Subject) {
        Params.AddIgnoredActor(Subject);
    }
    const FVector Eye = GetActorLocation() + FVector(0.f, 0.f, 70.f);   // eye height ~1.66 m
    FHitResult Hit;
    return !GetWorld()->LineTraceSingleByChannel(Hit, Eye, Location + FVector(0.f, 0.f, 50.f), ECC_Visibility, Params);
}

void AGenesisNpc::HandleWorldEvent(const FGenesisWorldEvent& Event)
{
    // The NPC that acts knows its own action; others only if they could see/hear it.
    UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    if (!WS) {
        return;
    }
    if (Event.ActorID == NpcID || (Event.bHasLocation && CanPerceive(Event.Location, nullptr))) {
        WS->NpcObserve(NpcID, Event.EventID);
    }
}
