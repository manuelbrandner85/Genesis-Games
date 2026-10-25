#include "Swim/GenesisSwimGameMode.h"
#include "Swim/GenesisOviduct.h"
#include "Swim/GenesisSpermPawn.h"
#include "GenesisGameInstance.h"
#include "UI/GenesisMenuWidget.h"
#include "UI/GenesisUserSettings.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
    constexpr float AutoSwimGuidance = 0.6f;          // auto swim (E2): ~70 s, inside the 60-120 s window
    constexpr int32 PlatesPerRing = 20;
    constexpr float RingSpacing = 140.f;

    /** Unit vectors across the tube at S (both perpendicular to the tangent). */
    void CrossSection(float S, FVector& OutA, FVector& OutB)
    {
        const FVector T = FGenesisOviduct::Tangent(S);
        OutA = FVector::CrossProduct(T, FVector::UpVector).GetSafeNormal();
        OutB = FVector::CrossProduct(OutA, T).GetSafeNormal();
    }

    UStaticMeshComponent* MakeEggPart(AActor* Owner, const TCHAR* Name, UStaticMesh* Mesh, float Radius)
    {
        UStaticMeshComponent* C = Owner->CreateDefaultSubobject<UStaticMeshComponent>(Name);
        C->SetupAttachment(Owner->GetRootComponent());
        C->SetStaticMesh(Mesh);
        C->SetRelativeScale3D(FVector(Radius / 50.f));
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        return C;
    }

    UInstancedStaticMeshComponent* MakeInstances(AActor* Owner, const TCHAR* Name, UStaticMesh* Mesh)
    {
        UInstancedStaticMeshComponent* C = Owner->CreateDefaultSubobject<UInstancedStaticMeshComponent>(Name);
        C->SetupAttachment(Owner->GetRootComponent());
        C->SetStaticMesh(Mesh);
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        C->SetCastShadow(false);
        C->SetMobility(EComponentMobility::Movable);
        return C;
    }
}

// --- Director ----------------------------------------------------------------------------------------

AGenesisSwimDirector::AGenesisSwimDirector()
{
    PrimaryActorTick.bCanEverTick = true;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    Wall = MakeInstances(this, TEXT("Wall"), Cube.Object);
    Cumulus = MakeInstances(this, TEXT("Cumulus"), Sphere.Object);
    Others = MakeInstances(this, TEXT("Others"), Sphere.Object);
    OtherTails = MakeInstances(this, TEXT("OtherTails"), Cylinder.Object);
    Oocyte = MakeEggPart(this, TEXT("Oocyte"), Sphere.Object, FGenesisOviduct::OocyteRadius);
    Zona = MakeEggPart(this, TEXT("Zona"), Sphere.Object, FGenesisOviduct::ZonaRadius);
    Zona->SetVisibility(false);            // graybox: an opaque zona would hide the oocyte; look comes in phase 3
    EggLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("EggLight"));
    EggLight->SetupAttachment(RootComponent);
    EggLight->SetIntensityUnits(ELightUnits::Candelas);
    EggLight->SetIntensity(20.f);
    EggLight->SetAttenuationRadius(1200.f);
    EggLight->SetCastShadows(false);
}

void AGenesisSwimDirector::BeginPlay()
{
    Super::BeginPlay();
    BuildCourse();
}

void AGenesisSwimDirector::BuildCourse()
{
    const FVector Egg = FGenesisOviduct::EggLocation();
    Oocyte->SetWorldLocation(Egg);
    Zona->SetWorldLocation(Egg);
    EggLight->SetWorldLocation(Egg - FGenesisOviduct::Tangent(FGenesisOviduct::EggS) * 220.f + FVector(0.f, 0.f, 120.f));

    // Oviduct wall: rings of thin plates around the analytic tube (graybox; folds in phase 3).
    TArray<FTransform> Plates;
    for (float S = 0.f; S <= FGenesisOviduct::Length; S += RingSpacing) {
        FVector A, B;
        CrossSection(S, A, B);
        const FVector C = FGenesisOviduct::Center(S);
        const FVector T = FGenesisOviduct::Tangent(S);
        const float R = FGenesisOviduct::Radius(S);
        const float Width = 2.f * PI * R / PlatesPerRing * 1.08f;
        for (int32 I = 0; I < PlatesPerRing; ++I) {
            const float Angle = 2.f * PI * I / PlatesPerRing;
            const FVector Radial = A * FMath::Cos(Angle) + B * FMath::Sin(Angle);
            Plates.Add(FTransform(FRotationMatrix::MakeFromXZ(T, -Radial).Rotator(), C + Radial * (R + 3.f),
                FVector(RingSpacing * 1.08f / 100.f, Width / 100.f, 0.06f)));
        }
    }
    for (const float S : { 0.f, FGenesisOviduct::Length }) {      // both ends closed
        const float R = FGenesisOviduct::Radius(S) + 10.f;
        Plates.Add(FTransform(FRotationMatrix::MakeFromZ(FGenesisOviduct::Tangent(S)).Rotator(), FGenesisOviduct::Center(S),
            FVector(2.f * R / 100.f, 2.f * R / 100.f, 0.06f)));
    }
    Wall->AddInstances(Plates, false, true);

    // Cumulus cells (~12 um) in a loose shell around the oocyte; the cell swims through them.
    FRandomStream Rand(2026);
    TArray<FTransform> Cells;
    for (int32 I = 0; I < 160; ++I) {
        const FVector Dir = Rand.GetUnitVector();
        Cells.Add(FTransform(FRotator(Rand.FRandRange(0.f, 360.f), Rand.FRandRange(0.f, 360.f), 0.f),
            Egg + Dir * Rand.FRandRange(FGenesisOviduct::ZonaRadius + 15.f, 240.f), FVector(Rand.FRandRange(0.09f, 0.14f))));
    }
    Cumulus->AddInstances(Cells, false, true);

    // The other cells start around the player and swim on their own (no race: no ranking anywhere).
    TArray<FTransform> Heads, Tails;
    for (int32 I = 0; I < OtherCells; ++I) {
        FOther O;
        O.S = Rand.FRandRange(40.f, 700.f);
        FVector A, B;
        CrossSection(O.S, A, B);
        const float Angle = Rand.FRandRange(0.f, 2.f * PI);
        O.P = FGenesisOviduct::Center(O.S) + (A * FMath::Cos(Angle) + B * FMath::Sin(Angle)) * Rand.FRandRange(0.f, 0.8f) * FGenesisOviduct::Radius(O.S);
        O.H = (FGenesisOviduct::Tangent(O.S) + Rand.GetUnitVector() * 0.5f).GetSafeNormal();
        O.Effort = Rand.FRandRange(0.4f, 0.75f);
        O.Seed = Rand.FRandRange(0.f, 100.f);
        OtherState.Add(O);
        Heads.Add(FTransform(O.H.Rotation(), O.P, FVector(0.05f, 0.03f, 0.022f)));
        Tails.Add(FTransform(FRotationMatrix::MakeFromZ(O.H).Rotator(), O.P - O.H * 28.f, FVector(0.007f, 0.007f, 0.45f)));
    }
    Others->AddInstances(Heads, false, true);
    OtherTails->AddInstances(Tails, false, true);
}

AGenesisSpermPawn* AGenesisSwimDirector::GetSperm() const
{
    const APlayerController* PC = GetWorld()->GetFirstPlayerController();
    return PC ? Cast<AGenesisSpermPawn>(PC->GetPawn()) : nullptr;
}

void AGenesisSwimDirector::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    AGenesisSpermPawn* Sperm = GetSperm();
    if (!Sperm || Phase == EGenesisSwimPhase::Finished) {
        return;
    }
    if (!bPlaced) {
        Sperm->PlaceAtStart();
        bPlaced = true;
    }
    Elapsed += DeltaTime;
    PhaseTime += DeltaTime;
    TickOthers(DeltaTime);

    const FVector Egg = FGenesisOviduct::EggLocation();
    const UGenesisUserSettings* U = UGenesisUserSettings::Get();
    switch (Phase) {
    case EGenesisSwimPhase::Free:
    case EGenesisSwimPhase::Guided: {
        if (Elapsed >= FreeSeconds && Phase == EGenesisSwimPhase::Free) {
            Phase = EGenesisSwimPhase::Guided;
            PhaseTime = 0.f;
        }
        const float TimeGuide = Phase == EGenesisSwimPhase::Guided ? FMath::Clamp(PhaseTime / GuideRampSeconds, 0.f, 1.f) : 0.f;
        Sperm->SetGuidance(FMath::Max(TimeGuide, U && U->bAutoSwim ? AutoSwimGuidance : 0.f));
        if (FVector::Dist(Sperm->GetActorLocation(), Egg) <= FGenesisOviduct::ZonaRadius + 4.f) {
            Phase = EGenesisSwimPhase::Fusion;
            PhaseTime = 0.f;
            ArrivalSeconds = Elapsed;
            Sperm->SetFrozen(true);
            EggLight->SetIntensity(35.f);
        }
        else if (Elapsed >= ObjectiveAfter) {
            // No game over: another cell fuses, seen from outside; the life begins all the same.
            Phase = EGenesisSwimPhase::Objective;
            PhaseTime = 0.f;
            float Best = TNumericLimits<float>::Max();
            for (int32 I = 0; I < OtherState.Num(); ++I) {
                const float D = FVector::Dist(OtherState[I].P, Egg);
                if (D < Best) {
                    Best = D;
                    FusingOther = I;
                }
            }
            const FVector T = FGenesisOviduct::Tangent(FGenesisOviduct::EggS);
            FVector A, B;
            CrossSection(FGenesisOviduct::EggS, A, B);
            const FVector CamPos = Egg - T * 260.f + A * 140.f + B * 70.f;
            ObjectiveCamera = GetWorld()->SpawnActor<ACameraActor>(CamPos, (Egg - CamPos).Rotation());
            if (ObjectiveCamera) {
                ObjectiveCamera->GetCameraComponent()->SetConstraintAspectRatio(false);     // any window shape
                ObjectiveCamera->GetCameraComponent()->SetFieldOfView(60.f);
            }
            if (APlayerController* PC = GetWorld()->GetFirstPlayerController(); PC && ObjectiveCamera) {
                PC->SetViewTargetWithBlend(ObjectiveCamera, 1.f);
            }
            Sperm->SetFrozen(true);
        }
        break;
    }
    case EGenesisSwimPhase::Fusion:
        if (PhaseTime >= FusionSeconds) {
            Result = TEXT("Own");
            Finish();
        }
        break;
    case EGenesisSwimPhase::Objective:
        if (PhaseTime >= ObjectiveSeconds) {
            Result = TEXT("Other");
            Finish();
        }
        break;
    default:
        break;
    }
}

void AGenesisSwimDirector::TickOthers(float DeltaTime)
{
    const FVector Egg = FGenesisOviduct::EggLocation();
    TArray<FTransform> Heads, Tails;
    Heads.Reserve(OtherState.Num());
    Tails.Reserve(OtherState.Num());
    for (int32 I = 0; I < OtherState.Num(); ++I) {
        FOther& O = OtherState[I];
        if (I == FusingOther) {
            // Objective camera: this cell reaches the zona in the first three seconds.
            const FVector Target = Egg + (O.P - Egg).GetSafeNormal() * (FGenesisOviduct::ZonaRadius + 2.f);
            const float A = FMath::Clamp(DeltaTime / FMath::Max(3.f - PhaseTime, DeltaTime), 0.f, 1.f);
            O.H = (Target - O.P).GetSafeNormal(0.01f, O.H);
            O.P = FMath::Lerp(O.P, Target, A);
        }
        else {
            // Own course: against the flow along the centre line, with a little wander; the cells
            // lose their way in the cumulus and never reach the zona on their own.
            const float Wander = FMath::PerlinNoise1D(Elapsed * 0.3f + O.Seed);
            const FVector Ahead = FGenesisOviduct::Center(FMath::Min(O.S + 300.f, FGenesisOviduct::EggS - 300.f))
                + FVector(0.f, Wander * 180.f, FMath::PerlinNoise1D(Elapsed * 0.27f + O.Seed * 1.7f) * 150.f);
            O.H = FMath::Lerp(O.H, (Ahead - O.P).GetSafeNormal(), FMath::Clamp(0.8f * DeltaTime, 0.f, 1.f)).GetSafeNormal();
            const float Speed = O.S > FGenesisOviduct::EggS - 350.f ? 0.f : AGenesisSpermPawn::SwimSpeed * O.Effort;
            O.P += (O.H * Speed + FGenesisOviduct::Flow(O.P, O.S)) * DeltaTime;
            O.S = FGenesisOviduct::Project(O.P, O.S);
            FVector Normal;
            FGenesisOviduct::Constrain(O.P, O.S, 8.f, Normal);
        }
        Heads.Add(FTransform(O.H.Rotation(), O.P, FVector(0.05f, 0.03f, 0.022f)));
        Tails.Add(FTransform(FRotationMatrix::MakeFromZ(O.H).Rotator(), O.P - O.H * 28.f, FVector(0.007f, 0.007f, 0.45f)));
    }
    Others->BatchUpdateInstancesTransforms(0, Heads, true, true);
    OtherTails->BatchUpdateInstancesTransforms(0, Tails, true, true);
}

void AGenesisSwimDirector::ForceFinish(FName InResult)
{
    Result = InResult;
    Finish();
}

void AGenesisSwimDirector::Finish()
{
    Phase = EGenesisSwimPhase::Finished;
    UE_LOG(LogTemp, Log, TEXT("Genesis C02-B swim finished: %s after %.1f s (arrival %.1f s)"), *Result.ToString(), Elapsed, ArrivalSeconds);
    UGenesisGameInstance* GI = Cast<UGenesisGameInstance>(GetGameInstance());
    if (GI && GI->StoryStart.Step == EGenesisStoryStep::C02Swim) {
        GI->FinishSwim(Result);         // C02 continues in the menu map
    }
}

// --- Player controller -------------------------------------------------------------------------------

void AGenesisSwimPlayerController::BeginPlay()
{
    Super::BeginPlay();
    SetInputMode(FInputModeGameOnly());
    SetShowMouseCursor(false);
}

void AGenesisSwimPlayerController::SetupInputComponent()
{
    Super::SetupInputComponent();
    for (const FKey& Key : { EKeys::Escape, EKeys::P, EKeys::Gamepad_Special_Right }) {
        InputComponent->BindKey(Key, IE_Pressed, this, &AGenesisSwimPlayerController::TogglePauseMenu);
    }
}

void AGenesisSwimPlayerController::PlayerTick(float DeltaTime)
{
    Super::PlayerTick(DeltaTime);
    AGenesisSpermPawn* Sperm = Cast<AGenesisSpermPawn>(GetPawn());
    if (!Sperm || PauseMenu) {
        return;
    }
    auto Key = [this](const FKey& K) { return IsInputKeyDown(K) ? 1.f : 0.f; };
    auto Stick = [this](const FKey& K) {
        const float V = GetInputAnalogKeyState(K);
        return FMath::Abs(V) < StickDeadZone ? 0.f : (V - FMath::Sign(V) * StickDeadZone) / (1.f - StickDeadZone);
    };
    FVector2D Steer(Key(EKeys::D) + Key(EKeys::Right) - Key(EKeys::A) - Key(EKeys::Left) + Stick(EKeys::Gamepad_LeftX),
                    Key(EKeys::W) + Key(EKeys::Up) - Key(EKeys::S) - Key(EKeys::Down) + Stick(EKeys::Gamepad_LeftY));
    const UGenesisUserSettings* U = UGenesisUserSettings::Get();
    if (U && U->bInvertCameraY) {
        Steer.Y = -Steer.Y;
    }
    Steer.X = FMath::Clamp(Steer.X, -1.f, 1.f);
    Steer.Y = FMath::Clamp(Steer.Y, -1.f, 1.f);
    const bool bBurst = IsInputKeyDown(EKeys::SpaceBar) || IsInputKeyDown(EKeys::LeftShift) || IsInputKeyDown(EKeys::Gamepad_FaceButton_Bottom)
        || GetInputAnalogKeyState(EKeys::Gamepad_RightTriggerAxis) > 0.3f;
    LastSteer = Steer;
    bLastBurst = bBurst;
    Sperm->SetSwimInput(Steer, bBurst);
}

void AGenesisSwimPlayerController::TogglePauseMenu()
{
    if (PauseMenu) {
        ClosePauseMenu();
        return;
    }
    PauseMenu = CreateWidget<UGenesisMenuWidget>(this, UGenesisMenuWidget::StaticClass());
    if (!PauseMenu) {
        return;
    }
    PauseMenu->OnResume.BindUObject(this, &AGenesisSwimPlayerController::ClosePauseMenu);
    PauseMenu->AddToViewport(10);
    PauseMenu->StartPauseMenu(true);
    SetPause(true);
    FInputModeUIOnly Mode;
    Mode.SetWidgetToFocus(PauseMenu->TakeWidget());
    SetInputMode(Mode);
    SetShowMouseCursor(true);
}

void AGenesisSwimPlayerController::ClosePauseMenu()
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

AGenesisSwimGameMode::AGenesisSwimGameMode()
{
    DefaultPawnClass = AGenesisSpermPawn::StaticClass();
    PlayerControllerClass = AGenesisSwimPlayerController::StaticClass();
}

void AGenesisSwimGameMode::StartPlay()
{
    Super::StartPlay();
    if (!TActorIterator<AGenesisSwimDirector>(GetWorld())) {
        GetWorld()->SpawnActor<AGenesisSwimDirector>();
    }
}
