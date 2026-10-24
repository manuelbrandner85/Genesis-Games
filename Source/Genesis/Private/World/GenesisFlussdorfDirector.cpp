#include "World/GenesisFlussdorfDirector.h"
#include "Npc/GenesisNpc.h"
#include "Npc/GenesisNpcController.h"
#include "Npc/GenesisNpcSchedule.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Engine/TargetPoint.h"
#include "Engine/TriggerBox.h"
#include "Engine/World.h"
#include "EngineUtils.h"

bool UGenesisFlussdorfDirector::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
    return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

void UGenesisFlussdorfDirector::Tick(float DeltaTime)
{
    SinceRefresh += DeltaTime;
    if (SinceRefresh >= 0.5f) {
        SinceRefresh = 0.f;
        Refresh();
    }
}

FName UGenesisFlussdorfDirector::RegionAt(const FVector& Location) const
{
    for (TActorIterator<ATriggerBox> It(GetWorld()); It; ++It) {
        if (It->Tags.Num() == 0) {
            continue;
        }
        FVector Origin, Extent;
        It->GetActorBounds(false, Origin, Extent);
        if (FBox(Origin - Extent, Origin + Extent).IsInsideOrOn(Location)) {
            return It->Tags[0];
        }
    }
    return NAME_None;
}

AGenesisNpc* UGenesisFlussdorfDirector::FindNpc(FName NpcID) const
{
    for (TActorIterator<AGenesisNpc> It(GetWorld()); It; ++It) {
        if (It->NpcID == NpcID) {
            return *It;
        }
    }
    return nullptr;
}

void UGenesisFlussdorfDirector::Refresh()
{
    UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    if (!WS) {
        return;
    }
    Presence.Reset();
    for (TActorIterator<AGenesisNpc> It(GetWorld()); It; ++It) {
        const AGenesisNpcController* C = Cast<AGenesisNpcController>(It->GetController());
        const bool bStanding = C && C->HasArrived() && !It->IsInsidePrivate();
        Presence.Add(It->NpcID, bStanding ? RegionAt(It->GetActorLocation()) : NAME_None);
    }
    FGenesisWorkshopContract::Update(*WS, Presence);
    for (TActorIterator<AGenesisNpc> It(GetWorld()); It; ++It) {
        if (AGenesisNpcController* C = Cast<AGenesisNpcController>(It->GetController())) {
            const FName Override = FGenesisWorkshopContract::NpcOverrideAnchor(*WS, It->NpcID);
            if (Override != C->GetOverrideAnchor()) {
                C->SetOverrideAnchor(Override);
            }
        }
    }
}

void UGenesisFlussdorfDirector::SnapResidentsToSchedule()
{
    const UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    if (!WS) {
        return;
    }
    for (TActorIterator<AGenesisNpc> It(GetWorld()); It; ++It) {
        FName Anchor = FGenesisWorkshopContract::NpcOverrideAnchor(*WS, It->NpcID);
        bool bInside = false;
        if (Anchor.IsNone()) {
            if (const FGenesisScheduleEntry* E = FGenesisNpcSchedules::Find(It->NpcID, WS->GetMinuteOfDay())) {
                Anchor = E->Anchor;
                bInside = E->bIndoorsPrivate;
            }
        }
        for (TActorIterator<ATargetPoint> T(GetWorld()); T; ++T) {
            if (T->ActorHasTag(Anchor)) {
                It->SetActorLocationAndRotation(T->GetActorLocation(), FRotator(0.f, T->GetActorRotation().Yaw, 0.f), false, nullptr, ETeleportType::ResetPhysics);
                break;
            }
        }
        if (AGenesisNpcController* C = Cast<AGenesisNpcController>(It->GetController())) {
            C->ResetAfterLoad();
        }
        It->SetInsidePrivate(bInside);
    }
    Refresh();
}
