#include "Player/GenesisPlayerController.h"
#include "Interaction/GenesisInteractableProp.h"
#include "Npc/GenesisNpc.h"
#include "Save/GenesisSaveStore.h"
#include "UI/GenesisHudWidget.h"
#include "World/GenesisFlussdorfDirector.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Blueprint/UserWidget.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"

const FString AGenesisPlayerController::SaveSlot = TEXT("Flussdorf");

namespace
{
    /** Greetings when there is nothing to settle (Startwerte, DRAFT_NEEDS_APPROVAL). */
    const TCHAR* Greeting(FName Who)
    {
        if (Who == TEXT("N01")) return TEXT("Moin. Viel zu tun heute.");
        if (Who == TEXT("N02")) return TEXT("Guten Tag.");
        if (Who == TEXT("N03")) return TEXT("Guten Morgen! Was darf es sein?");
        return TEXT("");
    }
}

AGenesisPlayerController::AGenesisPlayerController()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AGenesisPlayerController::BeginPlay()
{
    Super::BeginPlay();
    if (IsLocalController()) {
        Hud = CreateWidget<UGenesisHudWidget>(this, UGenesisHudWidget::StaticClass());
        if (Hud) {
            Hud->AddToViewport();
            Hud->OnChoiceClicked.BindUObject(this, &AGenesisPlayerController::Choose);
        }
    }
}

FGenesisPresence AGenesisPlayerController::CurrentPresence() const
{
    const UGenesisFlussdorfDirector* D = GetWorld()->GetSubsystem<UGenesisFlussdorfDirector>();
    return D ? D->GetPresence() : FGenesisPresence();
}

FText AGenesisPlayerController::NameOf(FName Who) const
{
    for (TActorIterator<AGenesisNpc> It(GetWorld()); It; ++It) {
        if (It->NpcID == Who) {
            return It->RoleName;
        }
    }
    for (TActorIterator<AGenesisInteractableProp> It(GetWorld()); It; ++It) {
        if (It->InteractionId == Who) {
            return It->Label;
        }
    }
    return FText::FromName(Who);
}

void AGenesisPlayerController::PlayerTick(float DeltaTime)
{
    Super::PlayerTick(DeltaTime);
    if (!IsInDialog()) {
        UpdateFocus();
    }
}

void AGenesisPlayerController::UpdateFocus()
{
    const APawn* Me = GetPawn();
    FocusTarget = NAME_None;
    FText Prompt;
    if (!Me) {
        return;
    }
    const FVector From = Me->GetActorLocation();
    const FVector Forward = Me->GetActorForwardVector();
    float Best = ReachCm;
    for (TActorIterator<AGenesisNpc> It(GetWorld()); It; ++It) {
        const FVector To = It->GetActorLocation() - From;
        const float D = To.Size2D();
        if (It->IsInsidePrivate() || D > Best || FVector::DotProduct(To.GetSafeNormal2D(), Forward) < 0.2f) {
            continue;
        }
        Best = D;
        FocusTarget = It->NpcID;
        const FGenesisPresence P = CurrentPresence();
        const FName* Region = P.Find(It->NpcID);
        Prompt = (Region && !Region->IsNone())
            ? FText::FromString(FString::Printf(TEXT("[E] Mit %s sprechen"), *It->RoleName.ToString()))
            : FText::FromString(FString::Printf(TEXT("%s ist gerade unterwegs"), *It->RoleName.ToString()));
    }
    for (TActorIterator<AGenesisInteractableProp> It(GetWorld()); It; ++It) {
        const FVector To = It->GetActorLocation() - From;
        const float D = To.Size2D();
        if (D > Best || FVector::DotProduct(To.GetSafeNormal2D(), Forward) < 0.2f) {
            continue;
        }
        Best = D;
        FocusTarget = It->InteractionId;
        Prompt = FText::FromString(FString::Printf(TEXT("[E] %s untersuchen"), *It->Label.ToString()));
    }
    if (Hud) {
        Hud->SetPrompt(Prompt);
    }
}

void AGenesisPlayerController::HandleInteract()
{
    if (IsInDialog()) {
        CloseDialog();
        return;
    }
    if (!FocusTarget.IsNone()) {
        const FGenesisPresence P = CurrentPresence();
        const FName* Region = P.Find(FocusTarget);
        const bool bPerson = FocusTarget.ToString().StartsWith(TEXT("N"));
        if (!bPerson || (Region && !Region->IsNone())) {
            OpenDialog(FocusTarget);
        }
    }
}

void AGenesisPlayerController::OpenDialog(FName Target)
{
    DialogTarget = Target;
    Highlight = 0;
    LastReply = FGenesisReply{ Target, FText::FromString(Greeting(Target)) };
    SetIgnoreMoveInput(true);
    SetIgnoreLookInput(true);
    SetShowMouseCursor(true);
    FInputModeGameAndUI Mode;
    Mode.SetHideCursorDuringCapture(false);
    SetInputMode(Mode);
    RefreshDialog();
}

void AGenesisPlayerController::RefreshDialog()
{
    UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    Choices = WS ? FGenesisWorkshopContract::Choices(*WS, DialogTarget, CurrentPresence()) : TArray<FGenesisChoice>();
    Highlight = FMath::Clamp(Highlight, 0, Choices.Num());
    if (Hud) {
        const FText Speaker = LastReply.Speaker.IsNone() ? FText::FromString(TEXT("Beobachtung")) : NameOf(LastReply.Speaker);
        Hud->ShowDialog(Speaker, LastReply.Line, Choices, Highlight);
    }
}

void AGenesisPlayerController::Choose(int32 Index)
{
    if (!IsInDialog()) {
        return;
    }
    if (Index >= Choices.Num()) {
        CloseDialog();                                   // last entry: end the conversation
        return;
    }
    if (!Choices.IsValidIndex(Index) || !Choices[Index].bEnabled) {
        return;
    }
    UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    if (!WS) {
        return;
    }
    LastReply = FGenesisWorkshopContract::Execute(*WS, DialogTarget, Choices[Index].Action, CurrentPresence());
    if (UGenesisFlussdorfDirector* D = GetWorld()->GetSubsystem<UGenesisFlussdorfDirector>()) {
        D->Refresh();                                     // appointments etc. take effect at once
    }
    Highlight = 0;
    RefreshDialog();
}

void AGenesisPlayerController::MoveHighlight(int32 Delta)
{
    if (IsInDialog()) {
        Highlight = (Highlight + Delta + Choices.Num() + 1) % (Choices.Num() + 1);
        RefreshDialog();
    }
}

void AGenesisPlayerController::CloseDialog()
{
    DialogTarget = NAME_None;
    Choices.Reset();
    SetIgnoreMoveInput(false);
    SetIgnoreLookInput(false);
    SetShowMouseCursor(false);
    SetInputMode(FInputModeGameOnly());
    if (Hud) {
        Hud->HideDialog();
    }
}

bool AGenesisPlayerController::SaveGame(FString* OutError)
{
    UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    if (!WS) {
        return false;
    }
    FGenesisWorldState S = WS->GetState();
    if (const APawn* Me = GetPawn()) {
        S.PlayerLocation = Me->GetActorLocation();
        S.PlayerRotation = GetControlRotation();
        S.bHasPlayerTransform = true;
    }
    FString Err;
    const bool bOk = FGenesisSaveStore::Save(FGenesisSaveStore::SlotPath(SaveSlot), S, Err);
    if (Hud) {
        Hud->ShowNote(FText::FromString(bOk ? FString::Printf(TEXT("Gespeichert – %s"), *WS->GetClockText()) : TEXT("Speichern fehlgeschlagen: ") + Err));
    }
    if (OutError) *OutError = Err;
    return bOk;
}

bool AGenesisPlayerController::LoadGame(FString* OutError)
{
    UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    FGenesisWorldState S;
    FString Err;
    bool bBackup = false;
    if (!WS || !FGenesisSaveStore::Load(FGenesisSaveStore::SlotPath(SaveSlot), S, Err, &bBackup)) {
        if (Hud) Hud->ShowNote(FText::FromString(TEXT("Kein Spielstand geladen: ") + Err));
        if (OutError) *OutError = Err;
        return false;
    }
    CloseDialog();
    WS->ResetState(S);
    if (APawn* Me = GetPawn(); Me && S.bHasPlayerTransform) {
        Me->SetActorLocation(S.PlayerLocation, false, nullptr, ETeleportType::ResetPhysics);
        SetControlRotation(S.PlayerRotation);
    }
    if (UGenesisFlussdorfDirector* D = GetWorld()->GetSubsystem<UGenesisFlussdorfDirector>()) {
        D->SnapResidentsToSchedule();
    }
    if (Hud) {
        Hud->ShowNote(FText::FromString(FString::Printf(TEXT("Geladen – %s%s"), *WS->GetClockText(), bBackup ? TEXT(" (Sicherungskopie)") : TEXT(""))));
    }
    return true;
}
