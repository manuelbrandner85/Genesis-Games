#include "Cinematic/GenesisSceneRunner.h"
#include "Cinematic/GenesisCinematicSubsystem.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "LevelSequence.h"
#include "LevelSequenceActor.h"
#include "LevelSequencePlayer.h"

UGenesisCinematicSubsystem* UGenesisSceneRunner::Cinematics() const
{
    return Controller && Controller->GetGameInstance() ? Controller->GetGameInstance()->GetSubsystem<UGenesisCinematicSubsystem>() : nullptr;
}

bool UGenesisSceneRunner::Start(APlayerController* PC, ULevelSequence* Sequence, const FGenesisSceneContract& InContract, TArray<FString>& OutErrors)
{
    Controller = PC;
    Contract = InContract;
    UGenesisCinematicSubsystem* Cine = Cinematics();
    if (!PC || !Sequence || !Cine) {
        OutErrors.Add(TEXT("player controller, sequence or cinematic subsystem missing"));
        return false;
    }
    if (!Cine->Bind(Contract, OutErrors)) {
        return false;
    }
    FMovieSceneSequencePlaybackSettings Settings;
    Settings.bDisableMovementInput = true;
    Settings.bDisableLookAtInput = true;
    Settings.bHidePlayer = false;
    ALevelSequenceActor* OutActor = nullptr;
    Player = ULevelSequencePlayer::CreateLevelSequencePlayer(PC->GetWorld(), Sequence, Settings, OutActor);
    SequenceActor = OutActor;
    if (!Player) {
        OutErrors.Add(TEXT("sequence player not created"));
        return false;
    }
    Player->OnFinished.AddDynamic(this, &UGenesisSceneRunner::HandleFinished);
    if (APawn* Pawn = PC->GetPawn()) {
        Pawn->DisableInput(PC);
    }
    Cine->Play(Contract);
    Player->Play();
    return true;
}

bool UGenesisSceneRunner::Skip()
{
    UGenesisCinematicSubsystem* Cine = Cinematics();
    const bool bSeenBefore = Cine && Cine->TechTestCommits.Contains(Contract.CommitKey());
    if (!Cine || !Player || !Cine->Skip(Contract, bSeenBefore)) {
        return false;
    }
    bSkipping = true;
    Player->Stop();                      // stop fires OnFinished; the contract is already past Playing
    bSkipping = false;
    if (Contract.CinematicState == EGenesisCinematicState::CommitPending) {
        CommitAndHandBack();
    }
    return true;
}

bool UGenesisSceneRunner::Answer(FName Result)
{
    UGenesisCinematicSubsystem* Cine = Cinematics();
    if (!Cine || !Cine->Answer(Contract, Result)) {
        return false;
    }
    CommitAndHandBack();
    return true;
}

void UGenesisSceneRunner::HandleFinished()
{
    UGenesisCinematicSubsystem* Cine = Cinematics();
    if (bSkipping || !Cine || Contract.CinematicState != EGenesisCinematicState::Playing) {
        return;
    }
    Cine->FinishPlayback(Contract);
    if (Contract.CinematicState == EGenesisCinematicState::CommitPending) {
        CommitAndHandBack();
    }
}

void UGenesisSceneRunner::CommitAndHandBack()
{
    UGenesisCinematicSubsystem* Cine = Cinematics();
    UGenesisWorldStateSubsystem* World = Controller ? Controller->GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>() : nullptr;
    if (!Cine || !Cine->Commit(Contract, World)) {
        return;
    }
    if (SequenceActor) {
        SequenceActor->Destroy();
        SequenceActor = nullptr;
    }
    Player = nullptr;
    if (Controller) {
        if (APawn* Pawn = Controller->GetPawn()) {
            if (!Contract.ReturnLocation.IsZero()) {
                Pawn->SetActorLocation(Contract.ReturnLocation, false, nullptr, ETeleportType::TeleportPhysics);
            }
            Pawn->EnableInput(Controller);
            Controller->SetViewTarget(Pawn);
        }
    }
    Cine->HandBack(Contract);
    OnHandedBack.Broadcast(Contract);
}
