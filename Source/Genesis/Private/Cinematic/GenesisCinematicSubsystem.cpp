#include "Cinematic/GenesisCinematicSubsystem.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

using ECineState = EGenesisCinematicState;

void UGenesisCinematicSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    FString Error;
    if (!LoadRegistry(DefaultRegistryPath(), Error)) {
        UE_LOG(LogTemp, Error, TEXT("Genesis cinematics: scene registry not loaded: %s"), *Error);
    }
}

FString UGenesisCinematicSubsystem::DefaultRegistryPath()
{
    return FPaths::ProjectContentDir() / TEXT("Genesis/Data/scene_registry.json");
}

const TCHAR* UGenesisCinematicSubsystem::ScriptVersion = TEXT("1.3");

bool UGenesisCinematicSubsystem::LoadRegistry(const FString& Path, FString& OutError)
{
    Registry.Reset();
    FString Text;
    TSharedPtr<FJsonObject> Root;
    if (!FFileHelper::LoadFileToString(Text, *Path)) {
        OutError = TEXT("missing ") + Path;
        return false;
    }
    if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text), Root) || !Root.IsValid()) {
        OutError = TEXT("not json");
        return false;
    }
    if (Root->GetStringField(TEXT("script_version")) != ScriptVersion) {
        OutError = FString::Printf(TEXT("registry is bound to ScriptLock %s, this build expects %s"), *Root->GetStringField(TEXT("script_version")), ScriptVersion);
        return false;
    }
    const TArray<TSharedPtr<FJsonValue>>* Scenes = nullptr;
    if (!Root->TryGetArrayField(TEXT("scenes"), Scenes)) {
        OutError = TEXT("no scenes");
        return false;
    }
    for (const TSharedPtr<FJsonValue>& V : *Scenes) {
        const TSharedPtr<FJsonObject> O = V->AsObject();
        FGenesisSceneRegistryEntry E;
        E.SceneID = FName(O->GetStringField(TEXT("scene_id")));
        E.WorkingTitle = O->GetStringField(TEXT("working_title"));
        E.Category = O->GetStringField(TEXT("category"));
        E.bInteractive = O->GetBoolField(TEXT("interactive_no_auto_decision"));
        O->TryGetStringField(TEXT("open_conflict"), E.OpenConflict);           // null -> stays empty
        E.ApprovalStatus = O->GetStringField(TEXT("approval_status"));
        FString ReplayOf;
        if (O->TryGetStringField(TEXT("replay_of"), ReplayOf)) {
            E.ReplayOf = FName(ReplayOf);
        }
        Registry.Add(E.SceneID, E);
    }
    return Registry.Num() > 0;
}

bool UGenesisCinematicSubsystem::IsAllowedTransition(ECineState From, ECineState To)
{
    switch (From) {
    case ECineState::Eligible:            return To == ECineState::BindingValidated || To == ECineState::Failed;
    case ECineState::BindingValidated:    return To == ECineState::Ready || To == ECineState::Failed;
    case ECineState::Ready:               return To == ECineState::Playing;
    case ECineState::Playing:             return To == ECineState::InGameplaySegment || To == ECineState::AwaitingInteraction || To == ECineState::CommitPending;
    case ECineState::InGameplaySegment:   return To == ECineState::Playing || To == ECineState::Failed;
    case ECineState::AwaitingInteraction: return To == ECineState::CommitPending;
    case ECineState::CommitPending:       return To == ECineState::Committed;
    case ECineState::Committed:           return To == ECineState::HandedBack;
    default:                     return false;      // HandedBack and Failed are final
    }
}

bool UGenesisCinematicSubsystem::Move(FGenesisSceneContract& Contract, ECineState To) const
{
    if (!IsAllowedTransition(Contract.CinematicState, To)) {
        return false;
    }
    Contract.CinematicState = To;
    return true;
}

TArray<FString> UGenesisCinematicSubsystem::ValidateContract(const FGenesisSceneContract& C) const
{
    TArray<FString> Errors;
    const FGenesisSceneRegistryEntry* Entry = FindScene(C.SceneID);
    if (!Entry) {
        Errors.Add(FString::Printf(TEXT("%s is not in the scene registry"), *C.SceneID.ToString()));
        return Errors;
    }
    if (C.ScriptVersion != ScriptVersion) {
        Errors.Add(FString::Printf(TEXT("ScriptVersion must be %s"), ScriptVersion));
    }
    if (!C.GameplaySegmentID.IsNone() && C.SceneID != TEXT("C02")) {
        Errors.Add(FString::Printf(TEXT("%s has no playable segment in ScriptLock %s"), *C.SceneID.ToString(), ScriptVersion));
    }
    if (C.SoulID.IsEmpty() || C.LifeID.IsEmpty() || C.WorldID.IsEmpty()) {
        Errors.Add(TEXT("SoulID, LifeID and WorldID are required"));
    }
    if (C.Language.IsEmpty()) {
        Errors.Add(TEXT("Language is required"));
    }
    if (C.ReturnControlState.IsNone()) {
        Errors.Add(TEXT("ReturnControlState is required"));
    }
    if (!Entry->IsDirectorApproved() && !C.bTechnicalTest) {
        Errors.Add(FString::Printf(TEXT("%s has no director approval (%s): only technical tests may run"), *C.SceneID.ToString(), *Entry->ApprovalStatus));
    }
    if (!Entry->OpenConflict.IsEmpty() && !C.bTechnicalTest) {
        Errors.Add(FString::Printf(TEXT("%s waits for a director decision: %s"), *C.SceneID.ToString(), *Entry->OpenConflict));
    }
    if (!Entry->ReplayOf.IsNone()) {
        // C20: the original C00 recording, the very same master file (never re-rendered)
        const FGenesisReplayRecipe& R = C.ReplayRecipe;
        if (R.Source != EGenesisReplaySource::OriginalRecording || R.SourceSceneID != Entry->ReplayOf) {
            Errors.Add(FString::Printf(TEXT("%s must replay the original recording of %s"), *C.SceneID.ToString(), *Entry->ReplayOf.ToString()));
        }
        if (R.MasterAssetPath.IsEmpty() || R.MasterSha256.Len() != 64) {
            Errors.Add(TEXT("replay needs the master asset path and its SHA-256"));
        }
    }
    else if (C.ReplayRecipe.Source == EGenesisReplaySource::OriginalRecording) {
        Errors.Add(FString::Printf(TEXT("%s is not a replay scene"), *C.SceneID.ToString()));
    }
    return Errors;
}

bool UGenesisCinematicSubsystem::Bind(FGenesisSceneContract& Contract, TArray<FString>& OutErrors) const
{
    if (Contract.CinematicState != ECineState::Eligible) {
        OutErrors.Add(TEXT("contract is not Eligible"));
        return false;
    }
    OutErrors = ValidateContract(Contract);
    if (OutErrors.Num() > 0) {
        Move(Contract, ECineState::Failed);
        return false;
    }
    return Move(Contract, ECineState::BindingValidated) && Move(Contract, ECineState::Ready);
}

bool UGenesisCinematicSubsystem::Play(FGenesisSceneContract& Contract) const
{
    return Move(Contract, ECineState::Playing);
}

bool UGenesisCinematicSubsystem::FinishPlayback(FGenesisSceneContract& Contract) const
{
    if (Contract.HasPendingSegment()) {
        return false;                    // the film cannot end before its playable segment was played
    }
    const FGenesisSceneRegistryEntry* Entry = FindScene(Contract.SceneID);
    return Move(Contract, Entry && Entry->bInteractive ? ECineState::AwaitingInteraction : ECineState::CommitPending);
}

bool UGenesisCinematicSubsystem::BeginSegment(FGenesisSceneContract& Contract) const
{
    return Contract.HasPendingSegment() && Move(Contract, ECineState::InGameplaySegment);
}

bool UGenesisCinematicSubsystem::EndSegment(FGenesisSceneContract& Contract) const
{
    if (!Move(Contract, ECineState::Playing)) {
        return false;
    }
    Contract.bGameplaySegmentDone = true;
    return true;
}

bool UGenesisCinematicSubsystem::Skip(FGenesisSceneContract& Contract, bool bHasSeenBefore) const
{
    if (Contract.CinematicState != ECineState::Playing || Contract.SkipPolicy == EGenesisSkipPolicy::Never
        || (Contract.SkipPolicy == EGenesisSkipPolicy::AfterFirstView && !bHasSeenBefore)) {
        return false;
    }
    if (Contract.HasPendingSegment()) {
        return BeginSegment(Contract);   // skipping the film never skips the playable segment
    }
    return FinishPlayback(Contract);     // interactive: still waits for the decision
}

bool UGenesisCinematicSubsystem::Answer(FGenesisSceneContract& Contract, FName Result) const
{
    if (Contract.CinematicState != ECineState::AwaitingInteraction || Result.IsNone()) {
        return false;
    }
    Contract.InteractionResult = Result;
    return Move(Contract, ECineState::CommitPending);
}

bool UGenesisCinematicSubsystem::Commit(FGenesisSceneContract& Contract, UGenesisWorldStateSubsystem* World)
{
    if (Contract.CinematicState != ECineState::CommitPending) {
        return false;
    }
    const FName Key = Contract.CommitKey();
    if (Contract.bTechnicalTest) {
        TechTestCommits.AddUnique(Key);
    }
    else {
        if (!World) {
            return false;
        }
        const FString After = Contract.InteractionResult.IsNone() ? FString(TEXT("Committed")) : Contract.InteractionResult.ToString();
        World->ApplyEvent(TEXT("Cinematic.Committed"), TEXT("System"), Contract.SceneID, After, Key, Contract.EventEvidenceIDs);
    }
    return Move(Contract, ECineState::Committed);
}

bool UGenesisCinematicSubsystem::HandBack(FGenesisSceneContract& Contract) const
{
    return Move(Contract, ECineState::HandedBack);
}
