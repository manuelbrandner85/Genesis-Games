#include "Pregnancy/GenesisPregnancyGameMode.h"
#include "Cinematic/GenesisCinematicSubsystem.h"
#include "GenesisGameInstance.h"
#include "Save/GenesisSaveStore.h"
#include "UI/GenesisMenuWidget.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Camera/CameraComponent.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/SpringArmComponent.h"
#include "UObject/ConstructorHelpers.h"

bool AGenesisPregnancyDirector::bStayAfterBirthForTests = false;

namespace
{
    constexpr float VisualSize = 100.f;     // the child is always shown 100 units long; its real size is labelled

    /** Cavity around the child, as a multiple of the child's size (tube in S1, uterus later, ever tighter). */
    float CavityRatio(int32 Stage)
    {
        const float R[] = { 8.f, 6.f, 5.f, 3.5f, 2.6f, 2.0f, 1.6f, 1.35f, 1.15f, 1.1f };
        return R[FMath::Clamp(Stage, 0, 9)];
    }

    UInstancedStaticMeshComponent* MakeInstances(AActor* Owner, const TCHAR* Name, UStaticMesh* Mesh)
    {
        UInstancedStaticMeshComponent* C = Owner->CreateDefaultSubobject<UInstancedStaticMeshComponent>(Name);
        C->SetupAttachment(Owner->GetRootComponent());
        C->SetStaticMesh(Mesh);
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        C->SetMobility(EComponentMobility::Movable);
        return C;
    }

    UTextBlock* Text(UWidgetTree* Tree, UCanvasPanel* Root, int32 Size, const FAnchors& Anchor, const FVector2D& Align, const FVector2D& Pos)
    {
        UTextBlock* T = Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
        FSlateFontInfo F = T->GetFont();
        F.Size = Size;
        T->SetFont(F);
        T->SetColorAndOpacity(FSlateColor(FLinearColor(0.92f, 0.9f, 0.86f, 1.f)));
        T->SetShadowOffset(FVector2D(1.f, 1.f));
        UCanvasPanelSlot* S = Root->AddChildToCanvas(T);
        S->SetAnchors(Anchor);
        S->SetAlignment(Align);
        S->SetPosition(Pos);
        S->SetAutoSize(true);
        return T;
    }
}

// --- HUD -----------------------------------------------------------------------------------------------

void UGenesisPregnancyHud::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Root"));
    WidgetTree->RootWidget = Root;
    HeaderText = Text(WidgetTree, Root, 22, FAnchors(0.f, 0.f), FVector2D(0.f, 0.f), FVector2D(40.f, 32.f));
    FactsText = Text(WidgetTree, Root, 15, FAnchors(0.f, 0.f), FVector2D(0.f, 0.f), FVector2D(40.f, 66.f));
    ActionsText = Text(WidgetTree, Root, 16, FAnchors(0.f, 1.f), FVector2D(0.f, 1.f), FVector2D(40.f, -40.f));
    OutsideText = Text(WidgetTree, Root, 15, FAnchors(1.f, 1.f), FVector2D(1.f, 1.f), FVector2D(-40.f, -40.f));
    OutsideText->SetJustification(ETextJustify::Right);
    CaptionText = Text(WidgetTree, Root, 20, FAnchors(0.5f, 0.45f), FVector2D(0.5f, 0.5f), FVector2D(0.f, 0.f));
    CaptionText->SetJustification(ETextJustify::Center);
}

void UGenesisPregnancyHud::Refresh(const FString& Header, const FString& Facts, const TArray<FString>& Actions, int32 Selected, const FString& Outside)
{
    HeaderText->SetText(FText::FromString(Header));
    FactsText->SetText(FText::FromString(Facts));
    FString Lines;
    for (int32 I = 0; I < Actions.Num(); ++I) {
        Lines += (I == Selected ? TEXT("›  ") : TEXT("    ")) + Actions[I] + TEXT("\n");
    }
    Lines += TEXT("\n‹ › wählen   ·   A / Leertaste ausführen   ·   RB / T halten: Zeitraffer");
    ActionsText->SetText(FText::FromString(Lines));
    OutsideText->SetText(FText::FromString(Outside));
}

void UGenesisPregnancyHud::ShowCaption(const FString& InText, float Seconds)
{
    Caption = InText;
    CaptionLeft = Seconds;
    CaptionText->SetText(FText::FromString(InText));
}

void UGenesisPregnancyHud::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    CaptionLeft = FMath::Max(0.f, CaptionLeft - InDeltaTime);
    CaptionText->SetRenderOpacity(FMath::Min(1.f, CaptionLeft / 0.8f));
}

// --- View pawn ---------------------------------------------------------------------------------------

AGenesisPregnancyViewPawn::AGenesisPregnancyViewPawn()
{
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    Arm = CreateDefaultSubobject<USpringArmComponent>(TEXT("Arm"));
    Arm->SetupAttachment(RootComponent);
    Arm->TargetArmLength = 260.f;
    Arm->bDoCollisionTest = false;
    Arm->bEnableCameraRotationLag = true;
    Arm->CameraRotationLagSpeed = 6.f;
    Arm->SetRelativeRotation(FRotator(-15.f, 200.f, 0.f));
    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    Camera->SetupAttachment(Arm);
    Camera->SetFieldOfView(50.f);
    ViewLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("ViewLight"));
    ViewLight->SetupAttachment(Camera);
    ViewLight->SetIntensityUnits(ELightUnits::Candelas);
    ViewLight->SetIntensity(40.f);
    ViewLight->SetLightColor(FLinearColor(1.f, 0.93f, 0.86f));
    ViewLight->SetAttenuationRadius(3000.f);
    ViewLight->SetCastShadows(false);
}

void AGenesisPregnancyViewPawn::Orbit(const FVector2D& Delta)
{
    FRotator R = Arm->GetRelativeRotation();
    R.Yaw += Delta.X;
    R.Pitch = FMath::Clamp(R.Pitch + Delta.Y, -70.f, 70.f);
    Arm->SetRelativeRotation(R);
}

void AGenesisPregnancyViewPawn::Zoom(float Delta)
{
    Arm->TargetArmLength = FMath::Clamp(Arm->TargetArmLength + Delta, 90.f, 900.f);
}

// --- Director ----------------------------------------------------------------------------------------

AGenesisPregnancyDirector::AGenesisPregnancyDirector()
{
    PrimaryActorTick.bCanEverTick = true;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    Wall = MakeInstances(this, TEXT("Wall"), Cube.Object);
    Cells = MakeInstances(this, TEXT("Cells"), Sphere.Object);
    Body = MakeInstances(this, TEXT("Body"), Sphere.Object);
    Cord = MakeInstances(this, TEXT("Cord"), Sphere.Object);
    // Light that really reaches the uterus: daylight through belly wall and tissue, deep red, faint.
    BellyLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("BellyLight"));
    BellyLight->SetupAttachment(RootComponent);
    BellyLight->SetIntensityUnits(ELightUnits::Candelas);
    BellyLight->SetLightColor(FLinearColor(1.f, 0.42f, 0.32f));
    BellyLight->SetAttenuationRadius(5000.f);
    BellyLight->SetCastShadows(false);
    BellyLight->SetRelativeLocation(FVector(0.f, 0.f, 600.f));
}

void AGenesisPregnancyDirector::BeginPlay()
{
    Super::BeginPlay();
    if (APlayerController* PC = GetWorld()->GetFirstPlayerController()) {
        Hud = CreateWidget<UGenesisPregnancyHud>(PC, UGenesisPregnancyHud::StaticClass());
        if (Hud) {
            Hud->AddToViewport(5);
        }
    }
}

float AGenesisPregnancyDirector::RealSizeMm(float Day)
{
    // Cell cluster ~0.1-0.2 mm, embryo length (CRL) from week 4, fetus CRL to ~36 cm at the birth.
    static const float D[] = { 0.f, 4.f, 10.f, 28.f, 56.f, 84.f, 126.f, 175.f, 224.f, 266.f };
    static const float M[] = { 0.12f, 0.15f, 0.2f, 4.f, 30.f, 80.f, 160.f, 240.f, 300.f, 360.f };
    for (int32 I = 1; I < UE_ARRAY_COUNT(D); ++I) {
        if (Day <= D[I]) {
            return FMath::Lerp(M[I - 1], M[I], (Day - D[I - 1]) / (D[I] - D[I - 1]));
        }
    }
    return M[UE_ARRAY_COUNT(M) - 1];
}

void AGenesisPregnancyDirector::StartLife()
{
    bStarted = true;
    UGenesisGameInstance* GI = Cast<UGenesisGameInstance>(GetGameInstance());
    UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    if (!WS) {
        return;
    }
    WS->SetPaused(true);                    // world time follows the pregnancy clock here
    bool bNew = false;
    if (GI && GI->bLoadSlotOnStart) {
        GI->bLoadSlotOnStart = false;
        FGenesisWorldState Loaded;
        FString Error;
        if (FGenesisSaveStore::Load(FGenesisSaveStore::SlotPath(GI->ActiveSlot), Loaded, Error)) {
            WS->ResetState(Loaded);
        }
    }
    else {
        WS->EnsureIdentity();
        if (GI && GI->bNewGamePendingSave) {
            GI->bNewGamePendingSave = false;
            GI->TakeStoryLife(WS->GetMutableState());
        }
        bNew = true;
    }
    FGenesisWorldState& S = WS->GetMutableState();
    if (S.PregnancyStage.IsNone()) {
        S.PregnancyStage = TEXT("S1");
        S.PregnancyDay = 0.f;
    }
    Preg.Restore(S.PregnancyStage, S.PregnancyDay, S.bPregnancyC03Done);
    ConceptionMinute = S.WorldMinute - int64(Preg.Day * 24.f * 60.f);
    BuildStage();
    if (Hud) {
        Hud->ShowCaption(FString::Printf(TEXT("%s · %s"), Preg.Current().Id, Preg.Current().Title), 5.f);
    }
    if (bNew) {
        SaveNow();                          // the start save of the new life
    }
}

void AGenesisPregnancyDirector::SyncWorldState()
{
    UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    if (!WS) {
        return;
    }
    FGenesisWorldState& S = WS->GetMutableState();
    S.PregnancyStage = Preg.StageId();
    S.PregnancyDay = Preg.Day;
    S.bPregnancyC03Done = Preg.bC03Done;
    S.WorldMinute = ConceptionMinute + int64(Preg.Day * 24.f * 60.f);
}

bool AGenesisPregnancyDirector::SaveNow(FString* OutError)
{
    SyncWorldState();
    const UGenesisGameInstance* GI = Cast<UGenesisGameInstance>(GetGameInstance());
    const UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    FString Error;
    const bool bOk = GI && WS && FGenesisSaveStore::Save(FGenesisSaveStore::SlotPath(GI->ActiveSlot), WS->GetState(), Error);
    if (OutError) {
        *OutError = Error;
    }
    return bOk;
}

void AGenesisPregnancyDirector::BuildStage()
{
    BuiltStage = Preg.Stage;
    Wall->ClearInstances();
    Cells->ClearInstances();
    Body->ClearInstances();
    Cord->ClearInstances();
    TurnAngle = TurnTarget = 0.f;
    const float Rw = VisualSize * 0.5f * CavityRatio(Preg.Stage);
    // Wall: plates on a sphere (S1: the tube around the cell cluster, later the uterine cavity).
    TArray<FTransform> Plates;
    const int32 N = 900;
    for (int32 I = 0; I < N; ++I) {
        const float Y = 1.f - 2.f * (I + 0.5f) / N;
        const float R = FMath::Sqrt(1.f - Y * Y);
        const float Phi = I * PI * (3.f - FMath::Sqrt(5.f));
        const FVector Nrm(R * FMath::Cos(Phi), R * FMath::Sin(Phi), Y);
        const float Size = 2.f * PI * Rw / FMath::Sqrt(float(N)) * 1.4f;
        Plates.Add(FTransform(FRotationMatrix::MakeFromZ(-Nrm).Rotator(), Nrm * (Rw + 4.f), FVector(Size / 100.f, Size / 100.f, 0.05f)));
    }
    Wall->AddInstances(Plates, false, true);
    if (Preg.Stage >= 3) {                           // placenta on the upper wall, from the embryonic period on
        Cells->AddInstance(FTransform(FRotator::ZeroRotator, FVector(0.f, 0.f, Rw - 6.f), FVector(Rw * 0.7f / 100.f, Rw * 0.7f / 100.f, 0.12f)));
    }
}

void AGenesisPregnancyDirector::UpdateVisual(float DeltaTime)
{
    AnimTime += DeltaTime;
    ActionAnim = FMath::Max(0.f, ActionAnim - DeltaTime);
    TurnAngle = FMath::FInterpTo(TurnAngle, TurnTarget, DeltaTime, 1.5f);
    const float A = ActionAnim > 0.f ? FMath::Sin((1.f - ActionAnim / 0.8f) * PI) : 0.f;     // 0..1..0 over 0.8 s
    const float Day = Preg.Day;
    const float Rw = VisualSize * 0.5f * CavityRatio(Preg.Stage);
    const float Idle = bAsleep ? 0.2f : 1.f;
    TArray<FTransform> T;
    // Heartbeat from ~day 22: ~110/min early, ~140/min later (visualised as a faint pulse of the body).
    const float Bpm = Day >= 22.f ? FMath::Lerp(110.f, 140.f, FMath::Clamp((Day - 22.f) / 100.f, 0.f, 1.f)) : 0.f;
    const float Pulse = Bpm > 0.f ? 0.015f * FMath::Max(0.f, FMath::Sin(AnimTime * Bpm / 60.f * 2.f * PI)) : 0.f;
    if (Preg.Stage <= 1) {
        // S1: dividing cells (2 -> 16) inside the zona; S2: blastocyst (hollow ball + inner cell mass) moving to the wall.
        FVector Center = FVector::ZeroVector;
        if (Preg.Stage == 1) {
            const float Imp = FMath::Clamp((Day - 6.f) / 4.f, 0.f, 1.f);
            Center = FMath::Lerp(FVector::ZeroVector, FVector(0.f, 0.f, -(Rw - VisualSize * 0.35f)), Imp);
            for (int32 I = 0; I < 48; ++I) {
                const float Y = 1.f - 2.f * (I + 0.5f) / 48;
                const float R = FMath::Sqrt(1.f - Y * Y);
                const float Phi = I * PI * (3.f - FMath::Sqrt(5.f));
                T.Add(FTransform(FRotator::ZeroRotator, Center + FVector(R * FMath::Cos(Phi), R * FMath::Sin(Phi), Y) * 45.f, FVector(0.16f)));
            }
            for (int32 I = 0; I < 8; ++I) {
                T.Add(FTransform(FRotator::ZeroRotator, Center + FVector(25.f + (I % 2) * 8.f, (I / 2 - 1.5f) * 8.f, (I % 3) * 6.f), FVector(0.14f)));
            }
        }
        else {
            const int32 Count = FMath::Clamp(1 << (int32(Day * 0.9f) + 1), 2, 16);
            FRandomStream Rand(7);
            const float CellR = 38.f / FMath::Pow(float(Count), 1.f / 3.f);
            for (int32 I = 0; I < Count; ++I) {
                const FVector P = Count == 2 ? FVector(I ? CellR : -CellR, 0.f, 0.f) : Rand.GetUnitVector() * (38.f - CellR) * Rand.FRandRange(0.4f, 1.f);
                T.Add(FTransform(FRotator::ZeroRotator, P + FVector(0.f, 0.f, FMath::Sin(AnimTime * 0.4f + I) * 0.6f), FVector(CellR * 2.f / 100.f)));
            }
        }
        Body->ClearInstances();
        Body->AddInstances(T, false, true);
        Cord->ClearInstances();
        return;
    }
    if (Preg.Stage == 2) {
        // S3: embryonic disc, neural tube and from ~day 22 the first heartbeat.
        T.Add(FTransform(FRotator::ZeroRotator, FVector::ZeroVector, FVector(0.9f, 0.55f, 0.12f)));
        for (int32 I = 0; I < 9; ++I) {
            T.Add(FTransform(FRotator::ZeroRotator, FVector(-36.f + I * 9.f, 0.f, 7.f), FVector(0.08f)));
        }
        const float Heart = Day >= 22.f ? 0.18f * (1.f + 4.f * Pulse) : 0.12f;
        T.Add(FTransform(FRotator::ZeroRotator, FVector(28.f, 0.f, -6.f), FVector(Heart)));
        Body->ClearInstances();
        Body->AddInstances(T, false, true);
        return;
    }
    // From S4: head, torso, arms and legs; proportions shift from a big head towards the newborn's.
    const float Grow = FMath::Clamp((Day - 28.f) / 238.f, 0.f, 1.f);
    const float Head = FMath::Lerp(0.48f, 0.27f, Grow) * VisualSize;
    const float Torso = VisualSize - Head;
    const float Limb = FMath::Lerp(0.12f, 0.42f, Grow) * VisualSize;
    const float Breath = FMath::Sin(AnimTime * 0.6f) * 1.5f * Idle;
    const FRotator BodyRot(0.f, TurnAngle, 0.f);
    const FQuat Q = BodyRot.Quaternion();
    auto Place = [&](const FVector& Local, const FVector& Scale, const FRotator& Rot = FRotator::ZeroRotator) {
        T.Add(FTransform(Q * Rot.Quaternion(), Q.RotateVector(Local), Scale * (1.f + Pulse)));
    };
    const float Jolt = (AnimAction == EGenesisPregAction::Twitch || AnimAction == EGenesisPregAction::ReactToVoice) ? A * 3.f : 0.f;
    const float HeadYaw = AnimAction == EGenesisPregAction::TurnToLight ? A * 35.f : 0.f;
    const float Swallow = AnimAction == EGenesisPregAction::Swallow ? A * 0.04f : 0.f;
    Place(FVector(Torso * 0.5f, 0.f, Breath + Jolt), FVector(Head / 100.f * 2.f * (1.f + Swallow)), FRotator(0.f, HeadYaw, 0.f));                // head
    Place(FVector(0.f, 0.f, Breath), FVector(Torso / 100.f * 1.1f, Torso / 100.f * 0.6f, Torso / 100.f * 0.6f));                                 // torso (curled)
    const float Stretch = AnimAction == EGenesisPregAction::Stretch ? A * 0.35f : 0.f;
    const bool bArmToHead = AnimAction == EGenesisPregAction::ThumbSuck || AnimAction == EGenesisPregAction::Grasp;
    for (int32 Side = -1; Side <= 1; Side += 2) {
        const float ArmLift = Side > 0 && bArmToHead ? A * 50.f : 0.f;
        Place(FVector(Torso * 0.25f, Side * Torso * 0.3f, -4.f + ArmLift * 0.2f), FVector(Limb / 100.f * (1.f + Stretch), 0.1f, 0.1f),
              FRotator(ArmLift, Side * (40.f - ArmLift * 0.5f), 0.f));
        const float Kick = AnimAction == EGenesisPregAction::Kick && Side > 0 ? A * 60.f : 0.f;
        Place(FVector(-Torso * 0.45f, Side * Torso * 0.22f, -6.f), FVector(Limb / 100.f * 1.2f * (1.f + Stretch), 0.12f, 0.12f),
              FRotator(-Kick, Side * 150.f, 0.f));
    }
    Body->ClearInstances();
    Body->AddInstances(T, false, true);
    // Umbilical cord from the belly to the placenta on the upper wall.
    TArray<FTransform> C;
    const FVector From = Q.RotateVector(FVector(0.f, 0.f, Torso * 0.25f));
    const FVector To(0.f, 0.f, Rw - 10.f);
    for (int32 I = 0; I <= 24; ++I) {
        const float U = I / 24.f;
        const FVector P = FMath::Lerp(From, To, U) + FVector(FMath::Sin(U * 9.f + AnimTime * 0.3f) * 12.f, FMath::Cos(U * 7.f) * 10.f, 0.f) * FMath::Sin(U * PI);
        C.Add(FTransform(FRotator::ZeroRotator, P, FVector(0.06f)));
    }
    Cord->ClearInstances();
    Cord->AddInstances(C, false, true);
}

void AGenesisPregnancyDirector::SelectAction(int32 Delta)
{
    const int32 Num = Preg.AllowedActions().Num();
    Selected = Num > 0 ? (Selected + Delta + Num) % Num : 0;
}

EGenesisPregAction AGenesisPregnancyDirector::GetSelectedAction() const
{
    const TArray<EGenesisPregAction> All = Preg.AllowedActions();
    return All.IsValidIndex(Selected) ? All[Selected] : EGenesisPregAction::Observe;
}

bool AGenesisPregnancyDirector::PerformAction(EGenesisPregAction A)
{
    FName Outside;
    if (IsInScene() || !Preg.Perform(A, Outside)) {
        return false;
    }
    AnimAction = A;
    ActionAnim = 0.8f;
    if (A == EGenesisPregAction::Turn) {
        TurnTarget += 180.f;
    }
    if (A == EGenesisPregAction::SleepWake) {
        bAsleep = !bAsleep;
    }
    if (A == EGenesisPregAction::Magnify && Hud) {
        Hud->ShowCaption(FString::Printf(TEXT("Größe in Wirklichkeit: ca. %.1f mm"), RealSizeMm(Preg.Day)), 3.f);
    }
    if (!Outside.IsNone()) {
        UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
        if (WS) {
            const FName Key(*FString::Printf(TEXT("PREG_%s_%d"), *WS->GetState().LifeID.Left(8), WS->GetState().NextEventNumber));
            WS->ApplyEvent(FName(*(FString(TEXT("Pregnancy.")) + FGenesisPregnancy::ActionName(A))), TEXT("Child"), TEXT("Mother"), Outside.ToString(), Key);
        }
        LastOutside = Outside.ToString();
        if (Outside == TEXT("Mother.FeltMovement")) {
            ++OutsideEvents;
            OutsideLine = TEXT("Draußen: Die Schwangere spürt die Bewegung und legt die Hand auf den Bauch.");
        }
        else if (Outside == TEXT("Mother.NoticedReaction")) {
            ++OutsideEvents;
            OutsideLine = TEXT("Draußen: Die Stimme hält kurz inne.");
        }
        else {
            OutsideLine = TEXT("Draußen merkt es noch niemand – nur ein Ultraschall würde es zeigen.");
        }
    }
    return true;
}

bool AGenesisPregnancyDirector::ShortenStage()
{
    if (IsInScene() || !Preg.ShortenStage()) {
        return false;
    }
    if (!Preg.bBorn) {
        BuildStage();
        if (Hud) {
            Hud->ShowCaption(FString::Printf(TEXT("%s · %s"), Preg.Current().Id, Preg.Current().Title), 4.f);
        }
    }
    SaveNow();
    return true;
}

void AGenesisPregnancyDirector::PlayScene(FName SceneID, float Seconds)
{
    UGenesisCinematicSubsystem* Cine = GetGameInstance() ? GetGameInstance()->GetSubsystem<UGenesisCinematicSubsystem>() : nullptr;
    const UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    Scene = FGenesisSceneContract();
    Scene.SceneID = SceneID;
    Scene.VariantID = TEXT("TECH_PREGNANCY");
    Scene.bTechnicalTest = true;               // no produced master yet: never canon, never in the ledger
    Scene.SoulID = WS ? WS->GetState().SoulID : FString();
    Scene.LifeID = WS ? WS->GetState().LifeID : FString();
    Scene.WorldID = WS ? WS->GetState().WorldID : FString();
    Scene.ReturnControlState = TEXT("Pregnancy");
    TArray<FString> Errors;
    if (Cine && Cine->Bind(Scene, Errors)) {
        Cine->Play(Scene);
    }
    SceneLeft = Seconds;
    if (Hud) {
        Hud->ShowCaption(SceneID.ToString() + TEXT(" – technischer Platzhalter (Film folgt)"), Seconds);
    }
}

void AGenesisPregnancyDirector::FinishScene()
{
    UGenesisCinematicSubsystem* Cine = GetGameInstance() ? GetGameInstance()->GetSubsystem<UGenesisCinematicSubsystem>() : nullptr;
    if (Cine && Scene.CinematicState == EGenesisCinematicState::Playing) {
        Cine->FinishPlayback(Scene);
        Cine->Commit(Scene, nullptr);
        Cine->HandBack(Scene);
    }
    if (Scene.SceneID == TEXT("C03")) {
        Preg.bC03Done = true;
        Preg.bC03Due = false;
        SaveNow();
        return;
    }
    if (Scene.SceneID == TEXT("C04")) {
        SaveNow();                            // the birth save: PregnancyStage Born
        bHandedOver = true;
        UGenesisGameInstance* GI = Cast<UGenesisGameInstance>(GetGameInstance());
        if (GI && !bStayAfterBirthForTests) {
            GI->ContinueAfterBirth();
        }
    }
}

void AGenesisPregnancyDirector::RefreshHud()
{
    if (!Hud) {
        return;
    }
    TArray<FString> Names;
    for (EGenesisPregAction A : Preg.AllowedActions()) {
        Names.Add(FGenesisPregnancy::ActionName(A));
    }
    Selected = FMath::Clamp(Selected, 0, FMath::Max(0, Names.Num() - 1));
    const FString Header = Preg.bBorn ? FString(TEXT("Geburt")) : FString::Printf(TEXT("%s · %s"), Preg.Current().Id, Preg.Current().Title);
    const FString Facts = FString::Printf(TEXT("Tag %d seit der Befruchtung · SSW %d · Größe ca. %.1f mm%s"), int32(Preg.Day),
        FGenesisPregnancy::GestationalWeek(Preg.Day), RealSizeMm(Preg.Day), Preg.TimeScale > 1.f ? TEXT(" · Zeitraffer") : TEXT(""));
    Hud->Refresh(Header, Facts, Names, Selected, OutsideLine);
}

void AGenesisPregnancyDirector::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (!bStarted) {
        StartLife();
    }
    if (bHandedOver) {
        return;
    }
    if (SceneLeft > 0.f) {
        SceneLeft -= DeltaTime;               // the pregnancy clock waits during a scene
        if (SceneLeft <= 0.f) {
            FinishScene();
        }
        UpdateVisual(DeltaTime);
        return;
    }
    if (Preg.Tick(DeltaTime)) {
        BuildStage();
        if (Hud) {
            Hud->ShowCaption(FString::Printf(TEXT("%s · %s"), Preg.Current().Id, Preg.Current().Title), 4.f);
        }
        SaveNow();                            // P2: saved between the stages
    }
    if (Preg.bC03Due && !Preg.bC03Done) {
        Preg.bC03Due = false;
        PlayScene(TEXT("C03"), 6.f);
    }
    else if (Preg.bBorn) {
        SyncWorldState();
        PlayScene(TEXT("C04"), 6.f);
    }
    // Daylight outside reaches the child only as a faint red glow (and only during the day).
    const int64 Minute = ConceptionMinute + int64(Preg.Day * 24.f * 60.f);
    const int32 Hour = int32((Minute % (24 * 60)) / 60);
    BellyLight->SetIntensity(Hour >= 7 && Hour < 19 ? 60.f : 6.f);
    UpdateVisual(DeltaTime);
    RefreshHud();
}

// --- Player controller -------------------------------------------------------------------------------

void AGenesisPregnancyPlayerController::BeginPlay()
{
    Super::BeginPlay();
    SetInputMode(FInputModeGameOnly());
    SetShowMouseCursor(false);
}

AGenesisPregnancyDirector* AGenesisPregnancyPlayerController::GetDirector() const
{
    for (TActorIterator<AGenesisPregnancyDirector> It(GetWorld()); It; ++It) {
        return *It;
    }
    return nullptr;
}

void AGenesisPregnancyPlayerController::SetupInputComponent()
{
    Super::SetupInputComponent();
    for (const FKey& Key : { EKeys::Escape, EKeys::P, EKeys::Gamepad_Special_Right }) {
        InputComponent->BindKey(Key, IE_Pressed, this, &AGenesisPregnancyPlayerController::TogglePauseMenu);
    }
    for (const FKey& Key : { EKeys::Q, EKeys::Gamepad_DPad_Left }) {
        InputComponent->BindKey(Key, IE_Pressed, this, &AGenesisPregnancyPlayerController::ActionPrev);
    }
    for (const FKey& Key : { EKeys::E, EKeys::Gamepad_DPad_Right }) {
        InputComponent->BindKey(Key, IE_Pressed, this, &AGenesisPregnancyPlayerController::ActionNext);
    }
    for (const FKey& Key : { EKeys::SpaceBar, EKeys::Enter, EKeys::Gamepad_FaceButton_Bottom }) {
        InputComponent->BindKey(Key, IE_Pressed, this, &AGenesisPregnancyPlayerController::DoAction);
    }
}

void AGenesisPregnancyPlayerController::ActionPrev()
{
    if (AGenesisPregnancyDirector* D = GetDirector()) {
        D->SelectAction(-1);
    }
}

void AGenesisPregnancyPlayerController::ActionNext()
{
    if (AGenesisPregnancyDirector* D = GetDirector()) {
        D->SelectAction(1);
    }
}

void AGenesisPregnancyPlayerController::DoAction()
{
    if (AGenesisPregnancyDirector* D = GetDirector()) {
        D->PerformAction(D->GetSelectedAction());
    }
}

void AGenesisPregnancyPlayerController::PlayerTick(float DeltaTime)
{
    Super::PlayerTick(DeltaTime);
    AGenesisPregnancyViewPawn* View = Cast<AGenesisPregnancyViewPawn>(GetPawn());
    AGenesisPregnancyDirector* D = GetDirector();
    if (!View || !D || PauseMenu) {
        return;
    }
    auto Stick = [this](const FKey& K) {
        const float V = GetInputAnalogKeyState(K);
        return FMath::Abs(V) < 0.25f ? 0.f : V;                    // dead zone against stick drift
    };
    const float X = (IsInputKeyDown(EKeys::D) ? 1.f : 0.f) - (IsInputKeyDown(EKeys::A) ? 1.f : 0.f) + Stick(EKeys::Gamepad_LeftX);
    const float Y = (IsInputKeyDown(EKeys::W) ? 1.f : 0.f) - (IsInputKeyDown(EKeys::S) ? 1.f : 0.f) + Stick(EKeys::Gamepad_LeftY);
    View->Orbit(FVector2D(X, Y) * 70.f * DeltaTime);
    const float Zoom = GetInputAnalogKeyState(EKeys::Gamepad_RightTriggerAxis) - GetInputAnalogKeyState(EKeys::Gamepad_LeftTriggerAxis)
        + (IsInputKeyDown(EKeys::PageDown) ? 1.f : 0.f) - (IsInputKeyDown(EKeys::PageUp) ? 1.f : 0.f);
    View->Zoom(Zoom * 300.f * DeltaTime);
    D->SetTimeLapse(IsInputKeyDown(EKeys::T) || IsInputKeyDown(EKeys::Gamepad_RightShoulder));
}

void AGenesisPregnancyPlayerController::TogglePauseMenu()
{
    if (PauseMenu) {
        ClosePauseMenu();
        return;
    }
    PauseMenu = CreateWidget<UGenesisMenuWidget>(this, UGenesisMenuWidget::StaticClass());
    if (!PauseMenu) {
        return;
    }
    PauseMenu->OnResume.BindUObject(this, &AGenesisPregnancyPlayerController::ClosePauseMenu);
    PauseMenu->AddToViewport(10);
    PauseMenu->StartPauseMenu(EGenesisPauseKind::Pregnancy);
    SetPause(true);
    FInputModeUIOnly Mode;
    Mode.SetWidgetToFocus(PauseMenu->TakeWidget());
    SetInputMode(Mode);
    SetShowMouseCursor(true);
}

void AGenesisPregnancyPlayerController::ClosePauseMenu()
{
    if (PauseMenu) {
        PauseMenu->RemoveFromParent();
        PauseMenu = nullptr;
    }
    SetPause(false);
    SetInputMode(FInputModeGameOnly());
    SetShowMouseCursor(false);
}

// --- Game mode ---------------------------------------------------------------------------------------

AGenesisPregnancyGameMode::AGenesisPregnancyGameMode()
{
    DefaultPawnClass = AGenesisPregnancyViewPawn::StaticClass();
    PlayerControllerClass = AGenesisPregnancyPlayerController::StaticClass();
}

void AGenesisPregnancyGameMode::StartPlay()
{
    Super::StartPlay();
    if (!TActorIterator<AGenesisPregnancyDirector>(GetWorld())) {
        GetWorld()->SpawnActor<AGenesisPregnancyDirector>();
    }
}
