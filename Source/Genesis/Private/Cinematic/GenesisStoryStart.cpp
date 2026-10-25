#include "Cinematic/GenesisStoryStart.h"
#include "Cinematic/GenesisCinematicSubsystem.h"

const FName FGenesisStoryStart::SwimSegment(TEXT("C02B_SWIM"));
const FName FGenesisStoryStart::PreIncarnationLife(TEXT("PRE_INCARNATION"));

namespace
{
    FString NewId() { return FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens); }
}

bool FGenesisStoryStart::Fail(const FString& Why)
{
    LastError = Why;
    UE_LOG(LogTemp, Error, TEXT("Genesis story start: %s"), *Why);
    return false;
}

bool FGenesisStoryStart::Start(UGenesisCinematicSubsystem& Cine)
{
    Reset();
    Life.SoulID = NewId();                // PreIncarnation_SoulSeed: the soul exists from C00 on
    Life.WorldID = NewId();               // one continuous world history, C00 already happens in it
    Life.WorldSeed = int32(FGuid::NewGuid().A & 0x7fffffff) | 1;
    Life.SoulSeedMinute = 0;
    Step = EGenesisStoryStep::C00;
    return BeginScene(Cine, TEXT("C00"));
}

bool FGenesisStoryStart::BeginScene(UGenesisCinematicSubsystem& Cine, FName SceneID)
{
    Scene = FGenesisSceneContract();
    Scene.SceneID = SceneID;
    Scene.VariantID = bTechnicalTest ? TEXT("TECH_CR001") : TEXT("MASTER");
    Scene.bTechnicalTest = bTechnicalTest;
    Scene.SoulID = Life.SoulID;
    Scene.WorldID = Life.WorldID;
    Scene.WorldSeed = Life.WorldSeed;
    Scene.LifeID = Life.LifeID.IsEmpty() ? PreIncarnationLife.ToString() : Life.LifeID;
    Scene.WorldTime = SceneID == TEXT("C00") ? Life.SoulSeedMinute : FMath::Max<int64>(Life.LifeStartMinute, 0);
    Scene.ReturnControlState = TEXT("StoryStart");
    if (SceneID == TEXT("C02")) {
        Scene.GameplaySegmentID = SwimSegment;
    }
    TArray<FString> Errors;
    if (!Cine.Bind(Scene, Errors)) {
        return Fail(FString::Printf(TEXT("%s does not bind: %s"), *SceneID.ToString(), *FString::Join(Errors, TEXT("; "))));
    }
    return Cine.Play(Scene) || Fail(SceneID.ToString() + TEXT(" does not play"));
}

bool FGenesisStoryStart::CloseScene(UGenesisCinematicSubsystem& Cine)
{
    if (!Cine.Commit(Scene, nullptr) || !Cine.HandBack(Scene)) {      // tech tests: in memory, never the ledger
        return Fail(Scene.SceneID.ToString() + TEXT(" commit/hand-back refused"));
    }
    Life.StoryStartCommits.AddUnique(Scene.CommitKey());
    Life.StoryStartStage = Scene.SceneID;
    return true;
}

bool FGenesisStoryStart::FinishFilm(UGenesisCinematicSubsystem& Cine, bool bSkipped)
{
    if (!CanSkip() && bSkipped) {
        return false;
    }
    switch (Step) {
    case EGenesisStoryStep::C00:
    case EGenesisStoryStep::C01: {
        if (!(bSkipped ? Cine.Skip(Scene, true) : Cine.FinishPlayback(Scene)) || !CloseScene(Cine)) {
            return Fail(TEXT("film part could not end"));
        }
        if (Step == EGenesisStoryStep::C00) {
            Step = EGenesisStoryStep::C01;
            return BeginScene(Cine, TEXT("C01"));
        }
        // The new life begins before C02, strictly after the soul seed; same soul, new life.
        Life.LifeID = NewId();
        Life.LifeNumber = 1;
        Life.LifeStartMinute = Life.SoulSeedMinute + 1;
        Step = EGenesisStoryStep::C02Film;
        return BeginScene(Cine, TEXT("C02"));
    }
    case EGenesisStoryStep::C02Film:
        // Ending or skipping C02-A both lead into the swim, never past it.
        if (!(bSkipped ? Cine.Skip(Scene, true) : Cine.BeginSegment(Scene))) {
            return Fail(TEXT("C02 does not enter the swim segment"));
        }
        Step = EGenesisStoryStep::C02Swim;
        return true;
    case EGenesisStoryStep::C02End:
        if (!(bSkipped ? Cine.Skip(Scene, true) : Cine.FinishPlayback(Scene)) || !CloseScene(Cine)) {
            return Fail(TEXT("C02 could not end"));
        }
        Step = EGenesisStoryStep::Title;
        return true;
    default:
        return false;
    }
}

bool FGenesisStoryStart::FinishSwim(UGenesisCinematicSubsystem& Cine, FName ConceptionMode)
{
    if (Step != EGenesisStoryStep::C02Swim || (ConceptionMode != TEXT("Own") && ConceptionMode != TEXT("Other"))) {
        return false;
    }
    if (!Cine.EndSegment(Scene)) {
        return Fail(TEXT("swim segment did not end"));
    }
    Life.ConceptionMode = ConceptionMode;
    Step = EGenesisStoryStep::C02End;
    return true;
}

void FGenesisStoryStart::Complete()
{
    if (Step == EGenesisStoryStep::Title) {
        Life.StoryStartStage = TEXT("Done");
        Step = EGenesisStoryStep::Done;
    }
}
