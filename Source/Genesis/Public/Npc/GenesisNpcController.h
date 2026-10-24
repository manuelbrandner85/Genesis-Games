#pragma once
#include "CoreMinimal.h"
#include "AIController.h"
#include "GenesisNpcController.generated.h"

class AGenesisNpc;

/**
 * Drives a AGenesisNpc through its day: once per second it looks up the active schedule entry
 * for the current world time and walks to that anchor (TargetPoint with the anchor tag). Arriving
 * at a private home anchor puts the person inside the house; leaving brings them out again.
 * No teleporting: if the clock jumps, the person still has to walk.
 */
UCLASS()
class GENESIS_API AGenesisNpcController : public AAIController
{
    GENERATED_BODY()
public:
    AGenesisNpcController();
    virtual void OnPossess(APawn* InPawn) override;
    virtual void Tick(float DeltaSeconds) override;

    FName GetCurrentAnchor() const { return CurrentAnchor; }
    bool HasArrived() const { return bArrived; }
    /** Overrides the schedule (e.g. an agreed appointment). None = back to the schedule. */
    void SetOverrideAnchor(FName Anchor, bool bIndoors = false);
    FName GetOverrideAnchor() const { return OverrideAnchor; }
    /** After a load moved the pawn: forget the old target and re-evaluate at once. */
    void ResetAfterLoad();

private:
    void UpdateSchedule();
    AActor* FindAnchor(FName Anchor) const;
    TWeakObjectPtr<AGenesisNpc> Npc;
    FName CurrentAnchor;
    FName OverrideAnchor;
    bool bOverrideIndoors = false;
    bool bTargetIndoors = false;
    bool bArrived = false;
    float SinceUpdate = 1.f;
    static constexpr float AcceptRadius = 60.f;
};
