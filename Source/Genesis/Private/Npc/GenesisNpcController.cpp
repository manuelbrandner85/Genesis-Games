#include "Npc/GenesisNpcController.h"
#include "Npc/GenesisNpc.h"
#include "Npc/GenesisNpcSchedule.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Engine/TargetPoint.h"
#include "EngineUtils.h"
#include "Navigation/PathFollowingComponent.h"

AGenesisNpcController::AGenesisNpcController()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AGenesisNpcController::OnPossess(APawn* InPawn)
{
    Super::OnPossess(InPawn);
    Npc = Cast<AGenesisNpc>(InPawn);
    SinceUpdate = 1.f;
}

AActor* AGenesisNpcController::FindAnchor(FName Anchor) const
{
    for (TActorIterator<ATargetPoint> It(GetWorld()); It; ++It) {
        if (It->ActorHasTag(Anchor)) {
            return *It;
        }
    }
    return nullptr;
}

void AGenesisNpcController::SetOverrideAnchor(FName Anchor, bool bIndoors)
{
    OverrideAnchor = Anchor;
    bOverrideIndoors = bIndoors;
    SinceUpdate = 1.f;
}

void AGenesisNpcController::ResetAfterLoad()
{
    StopMovement();
    CurrentAnchor = NAME_None;
    bArrived = false;
    SinceUpdate = 1.f;
    UpdateSchedule();
}

void AGenesisNpcController::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    SinceUpdate += DeltaSeconds;
    if (SinceUpdate >= 1.f) {
        SinceUpdate = 0.f;
        UpdateSchedule();
    }
}

void AGenesisNpcController::UpdateSchedule()
{
    AGenesisNpc* P = Npc.Get();
    const UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    if (!P || !WS) {
        return;
    }
    FName Target = OverrideAnchor;
    bool bIndoors = bOverrideIndoors;
    if (Target.IsNone()) {
        const FGenesisScheduleEntry* E = FGenesisNpcSchedules::Find(P->NpcID, WS->GetMinuteOfDay());
        if (!E) {
            return;
        }
        Target = E->Anchor;
        bIndoors = E->bIndoorsPrivate;
    }
    AActor* Anchor = FindAnchor(Target);
    if (!Anchor) {
        return;
    }
    if (Target != CurrentAnchor) {
        CurrentAnchor = Target;
        bTargetIndoors = bIndoors;
        bArrived = false;
        P->SetInsidePrivate(false);              // step out of the house before walking anywhere
    }
    const float Dist = FVector::Dist2D(P->GetActorLocation(), Anchor->GetActorLocation());
    if (Dist <= AcceptRadius + 30.f) {
        if (!bArrived) {
            bArrived = true;
            StopMovement();
            P->SetActorRotation(FRotator(0.f, Anchor->GetActorRotation().Yaw, 0.f));
            P->SetInsidePrivate(bTargetIndoors);
        }
        return;
    }
    bArrived = false;
    if (GetMoveStatus() != EPathFollowingStatus::Moving) {
        // bStopOnOverlap = false: measure the acceptance radius from the capsule centre, otherwise the
        // person stops ~1 m short (radius + capsule) and never counts as arrived.
        MoveToActor(Anchor, AcceptRadius, false, true, false);
    }
}
