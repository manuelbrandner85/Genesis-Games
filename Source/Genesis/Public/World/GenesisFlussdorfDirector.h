#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Mission/GenesisWorkshopContract.h"
#include "GenesisFlussdorfDirector.generated.h"

class AGenesisNpc;

/**
 * Runs the village while the game is running (with or without the player watching):
 * twice per second it records where each resident really stands (region volume, arrived, not
 * inside), advances the workshop chain (inspection, N01 taking over, withdrawal) and hands
 * appointments to the NPC controllers. After loading a save it puts every resident where the
 * loaded time says they are (a load restores the world, it is not travel).
 */
UCLASS()
class GENESIS_API UGenesisFlussdorfDirector : public UTickableWorldSubsystem
{
    GENERATED_BODY()
public:
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(UGenesisFlussdorfDirector, STATGROUP_Tickables); }
    virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;

    const FGenesisPresence& GetPresence() const { return Presence; }
    /** Region tag (R01..R08) whose volume contains the location, None if outside all. */
    FName RegionAt(const FVector& Location) const;
    AGenesisNpc* FindNpc(FName NpcID) const;
    /** Rebuild presence and run the chain now (after a dialog choice). */
    void Refresh();
    /** After loading: place residents at the anchors their (loaded) schedule asks for. */
    void SnapResidentsToSchedule();

private:
    FGenesisPresence Presence;
    float SinceRefresh = 0.f;
};
