#include "World/GenesisWorldStateSubsystem.h"

bool UGenesisWorldStateSubsystem::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
    return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

void UGenesisWorldStateSubsystem::Tick(float DeltaTime)
{
    if (!bPaused) {
        AdvanceMinutes(DeltaTime * GameMinutesPerSecond);
    }
}

FString UGenesisWorldStateSubsystem::GetClockText() const
{
    const int32 M = GetMinuteOfDay();
    return FString::Printf(TEXT("Tag %d, %02d:%02d"), GetDay(), M / 60, M % 60);
}

void UGenesisWorldStateSubsystem::SetClock(int32 Day, int32 Hour, int32 Minute)
{
    State.WorldMinute = int64(FMath::Max(Day, 1) - 1) * 24 * 60 + Hour * 60 + Minute;
    MinuteAccumulator = 0.0;
}

void UGenesisWorldStateSubsystem::AdvanceMinutes(double Minutes)
{
    MinuteAccumulator += Minutes;
    const int64 Whole = int64(FMath::FloorToDouble(MinuteAccumulator));
    if (Whole > 0) {
        State.WorldMinute += Whole;
        MinuteAccumulator -= double(Whole);
    }
}

void UGenesisWorldStateSubsystem::ResetState(const FGenesisWorldState& NewState)
{
    State = NewState;
    MinuteAccumulator = 0.0;
}

void UGenesisWorldStateSubsystem::EnsureIdentity()
{
    auto Fill = [](FString& Id) {
        if (Id.IsEmpty()) {
            Id = FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens);
        }
    };
    Fill(State.SoulID);
    Fill(State.LifeID);
    Fill(State.WorldID);
    if (State.WorldSeed == 0) {
        State.WorldSeed = int32(FGuid::NewGuid().A & 0x7fffffff) | 1;
    }
}

FString UGenesisWorldStateSubsystem::GetObjectState(FName ObjectID) const
{
    const FString* S = State.ObjectStates.Find(ObjectID);
    return S ? *S : FString();
}

bool UGenesisWorldStateSubsystem::WasApplied(FName IdempotencyKey) const
{
    return !IdempotencyKey.IsNone() && State.Ledger.ContainsByPredicate([&](const FGenesisWorldEvent& E) { return E.IdempotencyKey == IdempotencyKey; });
}

const FGenesisWorldEvent* UGenesisWorldStateSubsystem::FindLastEvent(FName ActionID) const
{
    for (int32 I = State.Ledger.Num() - 1; I >= 0; --I) {
        if (State.Ledger[I].ActionID == ActionID) {
            return &State.Ledger[I];
        }
    }
    return nullptr;
}

const FGenesisWorldEvent* UGenesisWorldStateSubsystem::ApplyEvent(FName ActionID, FName ActorID, FName ObjectID, const FString& AfterState,
                                                                  FName IdempotencyKey, const TArray<FName>& Sources,
                                                                  const FVector* Location)
{
    if (WasApplied(IdempotencyKey)) {
        return nullptr;
    }
    FGenesisWorldEvent& E = State.Ledger.AddDefaulted_GetRef();
    E.EventID = FName(*FString::Printf(TEXT("EV_%06d"), State.NextEventNumber++));
    E.ActionID = ActionID;
    E.ActorID = ActorID;
    E.ObjectID = ObjectID;
    E.BeforeState = GetObjectState(ObjectID);
    E.AfterState = AfterState;
    E.WorldMinute = State.WorldMinute;
    E.IdempotencyKey = IdempotencyKey;
    E.SourceEventIDs = Sources;
    if (Location) {
        E.Location = *Location;
        E.bHasLocation = true;
    }
    if (!ObjectID.IsNone()) {
        State.ObjectStates.Add(ObjectID, AfterState);
    }
    OnWorldEvent.Broadcast(E);
    return &State.Ledger.Last();
}

FGenesisNpcMemory& UGenesisWorldStateSubsystem::MemoryFor(FName NpcID)
{
    if (FGenesisNpcMemory* M = State.NpcMemories.FindByPredicate([&](const FGenesisNpcMemory& X) { return X.NpcID == NpcID; })) {
        return *M;
    }
    FGenesisNpcMemory& M = State.NpcMemories.AddDefaulted_GetRef();
    M.NpcID = NpcID;
    return M;
}

void UGenesisWorldStateSubsystem::NpcObserve(FName NpcID, FName EventID)
{
    MemoryFor(NpcID).ObservedEventIDs.AddUnique(EventID);
}

void UGenesisWorldStateSubsystem::NpcHear(FName NpcID, FName ClaimID)
{
    MemoryFor(NpcID).HeardClaims.AddUnique(ClaimID);
}

bool UGenesisWorldStateSubsystem::NpcKnows(FName NpcID, FName EventID) const
{
    const FGenesisNpcMemory* M = State.NpcMemories.FindByPredicate([&](const FGenesisNpcMemory& X) { return X.NpcID == NpcID; });
    return M && M->ObservedEventIDs.Contains(EventID);
}

bool UGenesisWorldStateSubsystem::TryPay(int32 AmountGE, FName ActionID, FName ObjectID, FName IdempotencyKey)
{
    if (WasApplied(IdempotencyKey)) {
        return true;                     // already paid for exactly this, no second charge
    }
    if (AmountGE < 0 || State.PlayerMoneyGE < AmountGE) {
        return false;
    }
    State.PlayerMoneyGE -= AmountGE;
    ApplyEvent(ActionID, TEXT("Player"), ObjectID, FString::Printf(TEXT("paid %d GE"), AmountGE), IdempotencyKey);
    return true;
}

void UGenesisWorldStateSubsystem::Earn(int32 AmountGE, FName ActionID, FName ActorID, FName ObjectID, FName IdempotencyKey)
{
    if (WasApplied(IdempotencyKey)) {
        return;
    }
    State.PlayerMoneyGE += AmountGE;
    ApplyEvent(ActionID, ActorID, ObjectID, FString::Printf(TEXT("earned %d GE"), AmountGE), IdempotencyKey);
}

int32 UGenesisWorldStateSubsystem::GetItemCount(FName ItemID) const
{
    const int32* N = State.PlayerItems.Find(ItemID);
    return N ? *N : 0;
}
