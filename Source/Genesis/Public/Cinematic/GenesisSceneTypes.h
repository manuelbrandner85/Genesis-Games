#pragma once
#include "CoreMinimal.h"
#include "GenesisSceneTypes.generated.h"

/**
 * V4.2 SceneContract data (docs/v4_2: SCENE_MATRIX_C00_C21.json, ScriptLock 1.2 IV.B, CR-001).
 * A cinematic is never "just played": it runs through a contract that names the soul, life and world
 * it belongs to, and it changes the world only through one idempotent commit.
 */
UENUM()
enum class EGenesisCinematicState : uint8
{
    Eligible,
    BindingValidated,
    Ready,
    Playing,
    InGameplaySegment,      // CR-001: playable part inside a scene (C02-B swim): never skippable, pausable
    AwaitingInteraction,    // interactive scenes: the shot ends, the player decides (never auto-decided)
    CommitPending,
    Committed,
    HandedBack,
    Failed,
};

UENUM()
enum class EGenesisSkipPolicy : uint8
{
    Allowed,                // skip jumps Playing -> CommitPending (never past the commit)
    AfterFirstView,         // only once this soul has committed the scene before
    Never,
};

/** Where a replayed scene's picture comes from. C20 must replay the C00 master byte-identical. */
UENUM()
enum class EGenesisReplaySource : uint8
{
    None,
    OriginalRecording,      // the same master file, unchanged
    ArchiveRender,          // state-bound archive replay (C15/C16)
};

/** One row of Content/Genesis/Data/scene_registry.json (written by tools/v4_2/bind_scriptlock.py). */
USTRUCT()
struct GENESIS_API FGenesisSceneRegistryEntry
{
    GENERATED_BODY()
    UPROPERTY() FName SceneID;
    UPROPERTY() FString WorkingTitle;
    UPROPERTY() FString Category;               // A, B, C, D, A/C
    UPROPERTY() bool bInteractive = false;       // ScriptLock I.7: no auto-decision at shot end
    UPROPERTY() FString OpenConflict;            // CON33-01, C17, C21: WAITING_DIRECTOR_DECISION
    UPROPERTY() FString ApprovalStatus;          // DIRECTOR_APPROVED only after "JA zu Vorschlag 11"
    UPROPERTY() FName ReplayOf;

    bool IsDirectorApproved() const { return ApprovalStatus == TEXT("DIRECTOR_APPROVED"); }
};

USTRUCT()
struct GENESIS_API FGenesisReplayRecipe
{
    GENERATED_BODY()
    UPROPERTY() FName RecipeID;
    UPROPERTY() FName SourceSceneID;
    UPROPERTY() EGenesisReplaySource Source = EGenesisReplaySource::None;
    UPROPERTY() FString MasterAssetPath;
    UPROPERTY() FString MasterSha256;
};

USTRUCT()
struct GENESIS_API FGenesisSceneContract
{
    GENERATED_BODY()
    UPROPERTY() FName SceneID;
    UPROPERTY() FString ScriptVersion = TEXT("1.2");
    UPROPERTY() FString SoulID;
    UPROPERTY() FString LifeID;
    UPROPERTY() FString WorldID;
    UPROPERTY() int64 WorldTime = 0;
    UPROPERTY() int32 WorldSeed = 0;
    UPROPERTY() TArray<FName> ParticipantIDs;
    UPROPERTY() TArray<FName> EventEvidenceIDs;   // ledger events that made the scene eligible
    UPROPERTY() FName VariantID;
    UPROPERTY() FString Language = TEXT("de");
    UPROPERTY() EGenesisCinematicState CinematicState = EGenesisCinematicState::Eligible;
    UPROPERTY() EGenesisSkipPolicy SkipPolicy = EGenesisSkipPolicy::Allowed;
    UPROPERTY() FGenesisReplayRecipe ReplayRecipe;
    UPROPERTY() TArray<FName> AudioCueIDs;
    UPROPERTY() TArray<FName> SubtitleCueIDs;
    UPROPERTY() FName ReturnControlState;          // e.g. Gameplay, Menu
    UPROPERTY() FVector ReturnLocation = FVector::ZeroVector;
    UPROPERTY() FName InteractionResult;           // the player's answer for interactive scenes
    /** Technical test (non-canonical stand-in content): runs the full state machine but never
     *  writes the world ledger. Required while the director's script approval is missing. */
    UPROPERTY() bool bTechnicalTest = false;
    /** Playable segment inside the scene (film -> play -> film), e.g. C02B_SWIM. Skipping the film
     *  before it lands in the segment; the segment itself cannot be skipped and must end first. */
    UPROPERTY() FName GameplaySegmentID;
    UPROPERTY() bool bGameplaySegmentDone = false;
    bool HasPendingSegment() const { return !GameplaySegmentID.IsNone() && !bGameplaySegmentDone; }

    /** Ledger key of the commit: once per scene, life and variant. */
    FName CommitKey() const { return FName(*FString::Printf(TEXT("CIN_%s_%s_%s"), *SceneID.ToString(), *LifeID, *VariantID.ToString())); }
};
