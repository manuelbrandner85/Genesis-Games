#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "Cinematic/GenesisSceneTypes.h"
#include "GenesisSceneRunner.generated.h"

class ALevelSequenceActor;
class APlayerController;
class ULevelSequence;
class ULevelSequencePlayer;
class UGenesisCinematicSubsystem;

/**
 * Plays one scene contract in the running game: binds it, plays the level sequence, and on the
 * end (or a skip) goes through CommitPending -> Committed -> HandedBack before the player gets
 * control back at the contract's return location. Player input is blocked while it plays.
 */
UCLASS()
class GENESIS_API UGenesisSceneRunner : public UObject
{
    GENERATED_BODY()
public:
    bool Start(APlayerController* PC, ULevelSequence* Sequence, const FGenesisSceneContract& InContract, TArray<FString>& OutErrors);
    /** Player skip: allowed only while playing (contract skip policy); never past commit or decision. */
    bool Skip();
    bool Answer(FName Result);
    const FGenesisSceneContract& GetContract() const { return Contract; }
    bool IsRunning() const { return Contract.CinematicState != EGenesisCinematicState::HandedBack && Contract.CinematicState != EGenesisCinematicState::Failed && Player != nullptr; }

    DECLARE_MULTICAST_DELEGATE_OneParam(FOnHandedBack, const FGenesisSceneContract&);
    FOnHandedBack OnHandedBack;

private:
    UFUNCTION() void HandleFinished();
    void CommitAndHandBack();
    UGenesisCinematicSubsystem* Cinematics() const;

    FGenesisSceneContract Contract;
    UPROPERTY() TObjectPtr<APlayerController> Controller;
    UPROPERTY() TObjectPtr<ULevelSequencePlayer> Player;
    UPROPERTY() TObjectPtr<ALevelSequenceActor> SequenceActor;
    bool bSkipping = false;
};
