#pragma once
#include "CoreMinimal.h"
#include "GenesisWorldTypes.generated.h"

/** One provable state change (data contract of V24 NPC/event simulation, reduced to what G6 uses). */
USTRUCT()
struct GENESIS_API FGenesisWorldEvent
{
    GENERATED_BODY()
    UPROPERTY() FName EventID;            // unique, e.g. EV_000017
    UPROPERTY() FName ActionID;           // what happened, e.g. Contract.Accepted
    UPROPERTY() FName ActorID;            // who did it: Player, N01, N02, N03
    UPROPERTY() FName ObjectID;           // what it affected, e.g. CT_GENERATOR_N02
    UPROPERTY() FString BeforeState;
    UPROPERTY() FString AfterState;
    UPROPERTY() int64 WorldMinute = 0;    // absolute world time in minutes since day 1, 00:00
    UPROPERTY() FName IdempotencyKey;     // same key twice -> applied once
    UPROPERTY() TArray<FName> SourceEventIDs;
};

/** What a NPC knows. Kept apart as in the source: observed, heard, verified. */
USTRUCT()
struct GENESIS_API FGenesisNpcMemory
{
    GENERATED_BODY()
    UPROPERTY() FName NpcID;
    UPROPERTY() TArray<FName> ObservedEventIDs;
    UPROPERTY() TArray<FName> HeardClaims;
    UPROPERTY() TArray<FName> VerifiedReports;
};

/** Everything that persists in a save. Schema version guards against loading unknown layouts. */
USTRUCT()
struct GENESIS_API FGenesisWorldState
{
    GENERATED_BODY()
    static constexpr int32 CurrentSchema = 1;
    UPROPERTY() int32 SchemaVersion = CurrentSchema;
    UPROPERTY() int64 WorldMinute = 0;
    UPROPERTY() int32 PlayerMoneyGE = 0;
    UPROPERTY() TMap<FName, int32> PlayerItems;
    UPROPERTY() TMap<FName, int32> MarketStock;
    UPROPERTY() TMap<FName, FString> ObjectStates;     // ObjectID -> state, e.g. CT_GENERATOR_N02 -> Accepted
    UPROPERTY() TArray<FGenesisNpcMemory> NpcMemories;
    UPROPERTY() TArray<FGenesisWorldEvent> Ledger;
    UPROPERTY() int32 NextEventNumber = 1;
    UPROPERTY() FVector PlayerLocation = FVector::ZeroVector;
    UPROPERTY() FRotator PlayerRotation = FRotator::ZeroRotator;
    UPROPERTY() bool bHasPlayerTransform = false;
};
