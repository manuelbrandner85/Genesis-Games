#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "World/GenesisWorldTypes.h"
#include "GenesisWorldStateSubsystem.generated.h"

/**
 * Authoritative world state of the running game: world clock, money, items, object states,
 * NPC knowledge and the event ledger. Every gameplay change goes through ApplyEvent, so it is
 * recorded, idempotent and saved/loaded as one unit.
 */
UCLASS()
class GENESIS_API UGenesisWorldStateSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()
public:
    /** Game minutes per real second while running (1 real minute = 10 game minutes). Startwert. */
    static constexpr double DefaultGameMinutesPerSecond = 10.0 / 60.0;

    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(UGenesisWorldStateSubsystem, STATGROUP_Tickables); }
    virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;

    // --- Clock ---------------------------------------------------------------------------------
    int64 GetWorldMinute() const { return State.WorldMinute; }
    int32 GetDay() const { return int32(State.WorldMinute / (24 * 60)) + 1; }
    int32 GetMinuteOfDay() const { return int32(State.WorldMinute % (24 * 60)); }
    FString GetClockText() const;
    void SetClock(int32 Day, int32 Hour, int32 Minute);
    void AdvanceMinutes(double Minutes);
    void SetPaused(bool bInPaused) { bPaused = bInPaused; }
    bool IsPaused() const { return bPaused; }
    double GameMinutesPerSecond = DefaultGameMinutesPerSecond;

    // --- State and ledger ------------------------------------------------------------------------
    const FGenesisWorldState& GetState() const { return State; }
    FGenesisWorldState& GetMutableState() { return State; }
    void ResetState(const FGenesisWorldState& NewState);
    /** New game: gives the state a fresh soul, life and world identity (keeps existing ones). */
    void EnsureIdentity();
    FString GetObjectState(FName ObjectID) const;

    /** Records a change of ObjectID to AfterState. Returns the event, or nullptr if the
     *  IdempotencyKey was applied before (nothing changes then). */
    const FGenesisWorldEvent* ApplyEvent(FName ActionID, FName ActorID, FName ObjectID, const FString& AfterState,
                                         FName IdempotencyKey = NAME_None, const TArray<FName>& Sources = {},
                                         const FVector* Location = nullptr);
    bool WasApplied(FName IdempotencyKey) const;
    const FGenesisWorldEvent* FindLastEvent(FName ActionID) const;

    /** NPC learns about an event only by perceiving it (or being told: Heard). */
    void NpcObserve(FName NpcID, FName EventID);
    void NpcHear(FName NpcID, FName ClaimID);
    bool NpcKnows(FName NpcID, FName EventID) const;

    // --- Money / items (atomic: either all of it happens or nothing) ------------------------------
    bool TryPay(int32 AmountGE, FName ActionID, FName ObjectID, FName IdempotencyKey);
    void Earn(int32 AmountGE, FName ActionID, FName ActorID, FName ObjectID, FName IdempotencyKey);
    int32 GetItemCount(FName ItemID) const;

    /** Called for every applied event (UI, NPC reactions). */
    DECLARE_MULTICAST_DELEGATE_OneParam(FOnWorldEvent, const FGenesisWorldEvent&);
    FOnWorldEvent OnWorldEvent;

private:
    FGenesisNpcMemory& MemoryFor(FName NpcID);
    FGenesisWorldState State;
    double MinuteAccumulator = 0.0;
    bool bPaused = false;
};
