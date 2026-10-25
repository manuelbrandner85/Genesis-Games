#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Cinematic/GenesisSceneTypes.h"
#include "GenesisCinematicSubsystem.generated.h"

class UGenesisWorldStateSubsystem;

/**
 * Runs scene contracts through the V4.2 cinematic state machine:
 * Eligible -> BindingValidated -> Ready -> Playing -> (AwaitingInteraction) -> CommitPending -> Committed -> HandedBack.
 * Only the transitions in IsAllowedTransition exist; a skip goes Playing -> CommitPending and can never
 * bypass the commit or an interactive decision. Scenes without the director's approval run only as
 * technical tests (bTechnicalTest), which never touch the world ledger.
 */
UCLASS()
class GENESIS_API UGenesisCinematicSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    static FString DefaultRegistryPath();
    /** ScriptLock version this build implements (CR-001: 1.2). Registry and contracts must match. */
    static const TCHAR* ScriptVersion;
    bool LoadRegistry(const FString& Path, FString& OutError);
    const FGenesisSceneRegistryEntry* FindScene(FName SceneID) const { return Registry.Find(SceneID); }
    int32 NumScenes() const { return Registry.Num(); }

    static bool IsAllowedTransition(EGenesisCinematicState From, EGenesisCinematicState To);

    /** Every problem that keeps the contract from binding (empty = valid). */
    TArray<FString> ValidateContract(const FGenesisSceneContract& Contract) const;

    /** Eligible -> BindingValidated -> Ready, or Failed with the errors. */
    bool Bind(FGenesisSceneContract& Contract, TArray<FString>& OutErrors) const;
    bool Play(FGenesisSceneContract& Contract) const;
    /** End of the playback: interactive scenes wait for the player, others go to CommitPending. */
    bool FinishPlayback(FGenesisSceneContract& Contract) const;
    /** CR-001: Playing -> InGameplaySegment (only with a pending segment) and back after it ended. */
    bool BeginSegment(FGenesisSceneContract& Contract) const;
    bool EndSegment(FGenesisSceneContract& Contract) const;
    /** Skip: never past an open decision and never past the commit. HasSeenBefore: this soul committed it already. */
    bool Skip(FGenesisSceneContract& Contract, bool bHasSeenBefore) const;
    /** The player's decision in an interactive scene. */
    bool Answer(FGenesisSceneContract& Contract, FName Result) const;
    /** Idempotent commit into the world ledger (technical tests: no ledger write). */
    bool Commit(FGenesisSceneContract& Contract, UGenesisWorldStateSubsystem* World);
    bool HandBack(FGenesisSceneContract& Contract) const;

    /** Commits seen by technical tests (in memory only, for QA evidence). */
    TArray<FName> TechTestCommits;

private:
    bool Move(FGenesisSceneContract& Contract, EGenesisCinematicState To) const;
    TMap<FName, FGenesisSceneRegistryEntry> Registry;
};
