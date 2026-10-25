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
    UPROPERTY() FVector Location = FVector::ZeroVector;   // where it happened (for perception)
    UPROPERTY() bool bHasLocation = false;
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
    static constexpr int32 CurrentSchema = 3;     // 2: soul/life/world identity (V4.2 SceneContracts), 3: story start C00-C02 (CR-001)
    UPROPERTY() int32 SchemaVersion = CurrentSchema;
    UPROPERTY() FString SoulID;                     // stays across rebirths
    UPROPERTY() FString LifeID;                     // new for every life
    UPROPERTY() FString WorldID;                    // one continuous world history
    UPROPERTY() int32 WorldSeed = 0;
    UPROPERTY() int32 LifeNumber = 1;
    // --- Schema 3 (CR-001): story start BOOT -> C00 -> C01 -> C02 (swim) -> title -------------------
    /** Last story-start stage this life passed: None (not begun), C00, C01, C02, Done. */
    UPROPERTY() FName StoryStartStage;
    /** Story time of the PreIncarnation_SoulSeed (C00, also when skipped) and of the conception
     *  (before C02). The life always begins strictly after the soul seed. -1 = not happened. */
    UPROPERTY() int64 SoulSeedMinute = -1;
    UPROPERTY() int64 LifeStartMinute = -1;
    /** C02-B result, never a game over: Own (the player's cell fused) or Other (another cell fused,
     *  seen through the objective camera). The life begins either way. */
    UPROPERTY() FName ConceptionMode;
    UPROPERTY() TArray<FName> StoryStartCommits;
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
