#include "Swim/GenesisSwimGameMode.h"
#include "Swim/GenesisOviduct.h"
#include "Swim/GenesisSpermPawn.h"
#include "GenesisGameInstance.h"
#include "UI/GenesisMenuWidget.h"
#include "UI/GenesisUserSettings.h"
#include "Blueprint/WidgetTree.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextBlock.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "UObject/ConstructorHelpers.h"

EGenesisRouteSection AGenesisSwimDirector::StandaloneStartSection = EGenesisRouteSection::Vagina;

namespace
{
    constexpr float AutoSwimGuidance = 0.6f;          // auto swim (E2)
    constexpr int32 PlatesPerRing = 20;
    constexpr float RingSpacing = 140.f;
    const int32 OthersPerSection[] = { 60, 50, 40, 25, 40 };   // fewer cells in every section (shown, never counted)

    /** Unit vectors across the course at S (both perpendicular to the tangent). */
    void CrossSection(const FGenesisCourse& C, float S, FVector& OutA, FVector& OutB)
    {
        const FVector T = C.Tangent(S);
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

    FTransform Plate(const FVector& Where, const FVector& Inward, const FVector& Along, float Length, float Width)
    {
        return FTransform(FRotationMatrix::MakeFromXZ(Along, Inward).Rotator(), Where, FVector(Length / 100.f, Width / 100.f, 0.06f));
    }
}

// --- Captions ------------------------------------------------------------------------------------------

void UGenesisSwimHud::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Root"));
    WidgetTree->RootWidget = Root;
    Label = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("Caption"));
    FSlateFontInfo F = Label->GetFont();
    F.Size = 18;
    Label->SetFont(F);
    Label->SetColorAndOpacity(FSlateColor(FLinearColor(0.9f, 0.9f, 0.88f, 1.f)));
    Label->SetShadowOffset(FVector2D(1.f, 1.f));
    Label->SetJustification(ETextJustify::Center);
    UCanvasPanelSlot* S = Root->AddChildToCanvas(Label);
    S->SetAnchors(FAnchors(0.5f, 0.88f));
    S->SetAlignment(FVector2D(0.5f, 0.5f));
    S->SetAutoSize(true);
    Label->SetRenderOpacity(0.f);
}

void UGenesisSwimHud::ShowCaption(const FString& Text, float Seconds)
{
    Caption = Text;
    Left = Total = FMath::Max(Seconds, 0.5f);
    if (Label) {
        Label->SetText(FText::FromString(Text));
    }
}

void UGenesisSwimHud::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    Left = FMath::Max(0.f, Left - InDeltaTime);
    const float Age = Total - Left;
    if (Label) {
        Label->SetRenderOpacity(Left <= 0.f ? 0.f : FMath::Min3(1.f, Age / 0.6f, Left / 0.8f));
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
    Particles = MakeInstances(this, TEXT("Particles"), Sphere.Object);
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
    const UGenesisGameInstance* GI = Cast<UGenesisGameInstance>(GetGameInstance());
    const bool bStory = GI && GI->StoryStart.Step == EGenesisStoryStep::C02Swim;
    Section = bStory ? EGenesisRouteSection::Vagina : StandaloneStartSection;
    SectionSeconds.Init(0.f, FGenesisSpermRoute::NumSections);
    if (APlayerController* PC = GetWorld()->GetFirstPlayerController()) {
        Hud = CreateWidget<UGenesisSwimHud>(PC, UGenesisSwimHud::StaticClass());
        if (Hud) {
            Hud->AddToViewport(5);
        }
    }
    Course = FGenesisSpermRoute::Make(Section);
    BuildSection();
}

void AGenesisSwimDirector::Caption(const FString& Text, float Seconds)
{
    if (Hud) {
        Hud->ShowCaption(Text, Seconds);
    }
}

void AGenesisSwimDirector::ClearSection()
{
    for (UInstancedStaticMeshComponent* C : { Wall.Get(), Cumulus.Get(), Others.Get(), OtherTails.Get(), Particles.Get() }) {
        C->ClearInstances();
    }
    OtherState.Reset();
    AcidZones.Reset();
}

void AGenesisSwimDirector::BuildSection()
{
    ClearSection();
    FRandomStream Rand(2026 + int32(Section));
    const bool bW5 = Section == EGenesisRouteSection::Ampulla;
    Oocyte->SetVisibility(bW5);
    EggLight->SetVisibility(bW5);
    const FVector Egg = Course.EndLocation();
    Oocyte->SetWorldLocation(Egg);
    Zona->SetWorldLocation(Egg);
    EggLight->SetWorldLocation(Egg - Course.Tangent(Course.EndS) * 220.f + FVector(0.f, 0.f, 120.f));

    // Wall: rings of thin plates around the analytic lumen (graybox; real tissue look in phase D).
    TArray<FTransform> Plates;
    const int32 Ring = Section == EGenesisRouteSection::Uterus || Section == EGenesisRouteSection::Vagina ? 40 : PlatesPerRing;
    for (float S = 0.f; S <= Course.Length; S += RingSpacing) {
        FVector A, B;
        CrossSection(Course, S, A, B);
        const FVector C = Course.Center(S);
        const FVector T = Course.Tangent(S);
        const float R = Course.Radius(S);
        for (int32 I = 0; I < Ring; ++I) {
            const float Angle = 2.f * PI * I / Ring;
            const FVector Radial = A * FMath::Cos(Angle) + B * FMath::Sin(Angle);
            const FVector Where = C + Radial * (R + 3.f);
            if (Course.PocketAt(Where, -10.f) != INDEX_NONE) {
                continue;                                  // crypt mouths stay open
            }
            Plates.Add(Plate(Where, -Radial, T, RingSpacing * 1.08f, 2.f * PI * R / Ring * 1.08f));
        }
    }
    // Crypts (W2): pocket walls from points on a sphere, open towards the canal.
    for (const FGenesisCoursePocket& Pk : Course.Pockets) {
        const int32 N = 140;
        for (int32 I = 0; I < N; ++I) {
            const float Y = 1.f - 2.f * (I + 0.5f) / N;
            const float Rr = FMath::Sqrt(1.f - Y * Y);
            const float Phi = I * PI * (3.f - FMath::Sqrt(5.f));
            const FVector Nrm(Rr * FMath::Cos(Phi), Y, Rr * FMath::Sin(Phi));
            const FVector Where = Pk.Center + Nrm * (Pk.Radius + 3.f);
            const float S = Course.Project(Where, Pk.S);
            if ((Where - Course.Center(S)).Size() < Course.Radius(S)) {
                continue;
            }
            Plates.Add(Plate(Where, -Nrm, FVector::CrossProduct(Nrm, FVector::UpVector).GetSafeNormal(0.01f, FVector::ForwardVector), 70.f, 70.f));
        }
    }
    // Both ends closed; W3 has two tubal exits in the end wall (the correct one leads on).
    for (const float S : { 0.f, Course.Length }) {
        const float R = Course.Radius(S) + 10.f;
        if (Section == EGenesisRouteSection::Uterus && S > 0.f) {
            FVector A, B;
            CrossSection(Course, S, A, B);
            const FVector T = Course.Tangent(S);
            for (float X = -R; X <= R; X += 120.f) {
                for (float Y = -R; Y <= R; Y += 120.f) {
                    const FVector Where = Course.Center(S) + A * Y + B * X;
                    if (X * X + Y * Y > R * R) continue;
                    if (FVector::Dist(Where, FGenesisSpermRoute::UterusExit(Course, true)) < 260.f
                        || FVector::Dist(Where, FGenesisSpermRoute::UterusExit(Course, false)) < 260.f) {
                        continue;
                    }
                    Plates.Add(Plate(Where, -T, A, 125.f, 125.f));
                }
            }
            continue;
        }
        Plates.Add(FTransform(FRotationMatrix::MakeFromZ(Course.Tangent(S)).Rotator(), Course.Center(S), FVector(2.f * R / 100.f, 2.f * R / 100.f, 0.06f)));
    }
    Wall->AddInstances(Plates, false, true);

    // Section media as fine particles: coagulum strands (W1), acidic zones (W1), mucus fibres (W2).
    TArray<FTransform> Bits;
    if (Section == EGenesisRouteSection::Vagina) {
        const FVector Start = Course.Center(Course.StartS);
        for (int32 I = 0; I < 500; ++I) {
            Bits.Add(FTransform(FRotator::ZeroRotator, Start + Rand.GetUnitVector() * Rand.FRandRange(0.f, FGenesisSpermRoute::CoagulumRadius),
                FVector(Rand.FRandRange(0.04f, 0.12f), 0.02f, 0.02f)));
        }
        for (const float S : { 1100.f, 1700.f, 2300.f, 2900.f, 3500.f, 4100.f }) {
            FVector A, B;
            CrossSection(Course, S, A, B);
            const float Ang = Rand.FRandRange(0.f, 2.f * PI);
            const FVector Zone = Course.Center(S) + (A * FMath::Cos(Ang) + B * FMath::Sin(Ang)) * (Course.Radius(S) - 220.f);
            AcidZones.Add(Zone);
            for (int32 I = 0; I < 60; ++I) {
                Bits.Add(FTransform(FRotator::ZeroRotator, Zone + Rand.GetUnitVector() * Rand.FRandRange(0.f, FGenesisSpermRoute::AcidZoneRadius()), FVector(0.05f)));
            }
        }
    }
    else if (Section == EGenesisRouteSection::Cervix) {
        for (int32 I = 0; I < 900; ++I) {                  // mucus fibres along the canal
            const float S = Rand.FRandRange(0.f, Course.Length);
            FVector A, B;
            CrossSection(Course, S, A, B);
            const float Ang = Rand.FRandRange(0.f, 2.f * PI);
            const FVector Where = Course.Center(S) + (A * FMath::Cos(Ang) + B * FMath::Sin(Ang)) * Course.Radius(S) * FMath::Sqrt(Rand.FRand());
            Bits.Add(FTransform(Course.Tangent(S).Rotation(), Where, FVector(0.6f, 0.012f, 0.012f)));
        }
    }
    Particles->AddInstances(Bits, false, true);

    // Cumulus cells around the oocyte (W5 only).
    if (bW5) {
        TArray<FTransform> Cells;
        for (int32 I = 0; I < 160; ++I) {
            const FVector Dir = Rand.GetUnitVector();
            Cells.Add(FTransform(FRotator(Rand.FRandRange(0.f, 360.f), Rand.FRandRange(0.f, 360.f), 0.f),
                Egg + Dir * Rand.FRandRange(FGenesisOviduct::ZonaRadius + 15.f, 240.f), FVector(Rand.FRandRange(0.09f, 0.14f))));
        }
        Cumulus->AddInstances(Cells, false, true);
    }

    // The other cells start around the player and swim on their own (no race: no ranking anywhere).
    TArray<FTransform> Heads, Tails;
    const int32 Count = OthersPerSection[int32(Section)];
    for (int32 I = 0; I < Count; ++I) {
        FOther O;
        O.S = Rand.FRandRange(Course.StartS - 100.f, Course.StartS + 550.f);
        FVector A, B;
        CrossSection(Course, O.S, A, B);
        const float Angle = Rand.FRandRange(0.f, 2.f * PI);
        O.P = Course.Center(O.S) + (A * FMath::Cos(Angle) + B * FMath::Sin(Angle)) * Rand.FRandRange(0.f, 0.8f) * Course.Radius(O.S);
        O.H = (Course.Tangent(O.S) + Rand.GetUnitVector() * 0.5f).GetSafeNormal();
        O.Effort = Rand.FRandRange(0.4f, 0.75f);
        O.Seed = Rand.FRandRange(0.f, 100.f);
        OtherState.Add(O);
        Heads.Add(FTransform(O.H.Rotation(), O.P, FVector(0.05f, 0.03f, 0.022f)));
        Tails.Add(FTransform(FRotationMatrix::MakeFromZ(O.H).Rotator(), O.P - O.H * 28.f, FVector(0.007f, 0.007f, 0.45f)));
    }
    Others->AddInstances(Heads, false, true);
    OtherTails->AddInstances(Tails, false, true);
    bPlaced = false;
}

void AGenesisSwimDirector::StartSection(EGenesisRouteSection NewSection)
{
    Section = NewSection;
    Course = FGenesisSpermRoute::Make(Section);
    BuildSection();
    Phase = EGenesisSwimPhase::Free;
    SectionElapsed = 0.f;
    PhaseTime = 0.f;
    StuckTime = 0.f;
    ProgressTime = 0.f;
    ProgressS = Course.StartS;
    if (Section == EGenesisRouteSection::Ampulla) {
        if (UGenesisUserSettings* U = UGenesisUserSettings::Get(); U && !U->bSpermRouteSeen && !bShortened) {
            U->bSpermRouteSeen = true;                     // F3: from now on the route may be shortened
            U->SaveSettings();
        }
    }
}

void AGenesisSwimDirector::EndSection()
{
    SectionSeconds[int32(Section)] = SectionElapsed;
    ++SectionsDone;
    if (Section == EGenesisRouteSection::Ampulla) {
        return;
    }
    NextSection = EGenesisRouteSection(int32(Section) + 1);
    Phase = EGenesisSwimPhase::Transition;
    PhaseTime = 0.f;
    if (AGenesisSpermPawn* Sperm = GetSperm()) {
        Sperm->SetFrozen(true);
    }
    Caption(FGenesisSpermRoute::Caption(NextSection), TransitionSeconds + 3.5f);
}

bool AGenesisSwimDirector::CanShorten() const
{
    const UGenesisUserSettings* U = UGenesisUserSettings::Get();
    return U && U->bSpermRouteSeen && Section != EGenesisRouteSection::Ampulla && Phase != EGenesisSwimPhase::Finished;
}

bool AGenesisSwimDirector::Shorten()
{
    if (!CanShorten()) {
        return false;
    }
    bShortened = true;
    SectionsDone = int32(EGenesisRouteSection::Ampulla);  // W1-W4 shown as a short film (placeholder: caption)
    Caption(TEXT("Der Weg bis in den Eileiter – Zeitraffer"), 3.f);
    StartSection(EGenesisRouteSection::Ampulla);
    if (AGenesisSpermPawn* Sperm = GetSperm()) {
        Sperm->SetCourse(Course);
        Sperm->SetFrozen(false);
        Sperm->SetSpeedFactor(FGenesisSpermRoute::HyperactivatedSpeed);
        Sperm->PlaceAtStart();
        bPlaced = true;
    }
    return true;
}

void AGenesisSwimDirector::SwitchCell(const FString& Why, float NewS, const FVector& Offset)
{
    // F4: no game over - another cell of the same section carries on, the player steers that one.
    ++Switches;
    LastSwitchReason = Why;
    StuckTime = 0.f;
    ProgressTime = 0.f;
    ProgressS = NewS;
    if (AGenesisSpermPawn* Sperm = GetSperm()) {
        Sperm->PlaceAt(NewS, Offset);
        Sperm->SetFrozen(false);
    }
    Caption(TEXT("Eine andere Samenzelle schwimmt weiter"), 3.f);
}

AGenesisSpermPawn* AGenesisSwimDirector::GetSperm() const
{
    const APlayerController* PC = GetWorld()->GetFirstPlayerController();
    return PC ? Cast<AGenesisSpermPawn>(PC->GetPawn()) : nullptr;
}

bool AGenesisSwimDirector::DebugEnterPocket()
{
    AGenesisSpermPawn* Sperm = GetSperm();
    if (!Sperm || Course.Pockets.Num() == 0) {
        return false;
    }
    const FGenesisCoursePocket& Pk = Course.Pockets[0];
    Sperm->PlaceAt(Pk.S);
    Sperm->SetActorLocation(Pk.Center);
    Sperm->SetFrozen(true);                               // a cell caught deep in the crypt
    return true;
}

bool AGenesisSwimDirector::DebugWrongExit()
{
    AGenesisSpermPawn* Sperm = GetSperm();
    if (!Sperm || Section != EGenesisRouteSection::Uterus) {
        return false;
    }
    Sperm->PlaceAt(Course.EndS - 60.f);
    Sperm->SetActorLocation(FGenesisSpermRoute::UterusExit(Course, false));
    return true;
}

void AGenesisSwimDirector::TickMechanics(float DeltaTime)
{
    AGenesisSpermPawn* Sperm = GetSperm();
    const FVector P = Sperm->GetActorLocation();
    const float S = Sperm->GetCourseS();
    float Medium = 1.f;
    switch (Section) {
    case EGenesisRouteSection::Vagina:
        if (FVector::Dist(P, Course.Center(Course.StartS)) < FGenesisSpermRoute::CoagulumRadius) {
            Medium = FGenesisSpermRoute::CoagulumDrag;     // still inside the gel of the ejaculate
        }
        for (const FVector& Z : AcidZones) {
            if (FVector::Dist(P, Z) < FGenesisSpermRoute::AcidZoneRadius()) {
                Medium = FMath::Min(Medium, FGenesisSpermRoute::AcidDrag);
            }
        }
        break;
    case EGenesisRouteSection::Cervix: {
        const int32 Pk = Course.PocketAt(P);
        if (Pk != INDEX_NONE && FVector::Dist(P, Course.Pockets[Pk].Center) < Course.Pockets[Pk].Radius * 0.6f) {
            StuckTime += DeltaTime;
            if (StuckTime > FGenesisSpermRoute::StuckSeconds) {
                SwitchCell(TEXT("crypt"), FMath::Min(Course.Pockets[Pk].S + 200.f, Course.EndS - 100.f), FVector::ZeroVector);
                return;
            }
        }
        else {
            StuckTime = 0.f;
        }
        break;
    }
    case EGenesisRouteSection::Uterus: {
        // Peristaltic waves: for a few seconds the fluid carries the cells towards the tubes.
        const bool bWave = FMath::Fmod(SectionElapsed, FGenesisSpermRoute::ContractionPeriod) < FGenesisSpermRoute::ContractionLength;
        FGenesisCourse Now = Course;
        Now.FlowMax = bWave ? -FGenesisSpermRoute::ContractionFlow : 0.f;
        Sperm->SetCourse(Now);
        Sperm->SetFinalGoal(FGenesisSpermRoute::UterusExit(Course, true));
        if (S >= Course.EndS - 100.f) {
            const bool bCorrect = FVector::Dist(P, FGenesisSpermRoute::UterusExit(Course, true)) < FVector::Dist(P, FGenesisSpermRoute::UterusExit(Course, false));
            if (bCorrect) {
                EndSection();
            }
            else {                                          // the other tube has no oocyte: another cell takes over
                SwitchCell(TEXT("wrong tube"), Course.EndS - 900.f, FVector(0.f, Course.RadiusEnd * 0.4f, 0.f));
            }
            return;
        }
        break;
    }
    case EGenesisRouteSection::Isthmus:
        if (!bRested && S >= FGenesisSpermRoute::RestS) {
            Phase = EGenesisSwimPhase::Resting;            // binding to the epithelium: the reservoir
            PhaseTime = 0.f;
            Sperm->SetFrozen(true);
            Caption(TEXT("Kapazitation – in Wirklichkeit einige Stunden (Zeitsprung)"), FGenesisSpermRoute::RestSeconds + 2.f);
            return;
        }
        break;
    default:
        break;
    }
    Sperm->SetMediumFactor(Medium);
    if (Section != EGenesisRouteSection::Ampulla && Section != EGenesisRouteSection::Uterus && S >= Course.EndS - 30.f) {
        EndSection();
        return;
    }
    // Any section before W5: no headway for a long time (wedged against a wall) -> another cell carries on.
    if (Section != EGenesisRouteSection::Ampulla) {
        if (S > ProgressS + 50.f) {
            ProgressS = S;
            ProgressTime = 0.f;
        }
        else if ((ProgressTime += DeltaTime) > NoProgressSeconds) {
            SwitchCell(TEXT("no headway"), FMath::Min(S + 250.f, Course.EndS - 100.f), FVector::ZeroVector);
        }
    }
}

void AGenesisSwimDirector::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    AGenesisSpermPawn* Sperm = GetSperm();
    if (!Sperm || Phase == EGenesisSwimPhase::Finished) {
        return;
    }
    if (!bPlaced) {
        Sperm->SetCourse(Course);
        Sperm->SetFrozen(false);
        Sperm->PlaceAtStart();
        bPlaced = true;
        if (!bStarted) {
            bStarted = true;
            Caption(FGenesisSpermRoute::Caption(Section), 5.f);
            ProgressS = Course.StartS;
        }
    }
    Elapsed += DeltaTime;
    SectionElapsed += DeltaTime;
    PhaseTime += DeltaTime;
    TickOthers(DeltaTime);

    const UGenesisUserSettings* U = UGenesisUserSettings::Get();
    switch (Phase) {
    case EGenesisSwimPhase::Transition:
        if (PhaseTime >= TransitionSeconds) {
            StartSection(NextSection);
            Sperm->SetCourse(Course);
            Sperm->SetFrozen(false);
            Sperm->PlaceAtStart();
            bPlaced = true;
        }
        return;
    case EGenesisSwimPhase::Resting:
        if (PhaseTime >= FGenesisSpermRoute::RestSeconds) {
            bRested = true;
            Phase = EGenesisSwimPhase::Free;
            Sperm->SetFrozen(false);
            Sperm->SetSpeedFactor(FGenesisSpermRoute::HyperactivatedSpeed);   // hyperactivated from now on
        }
        return;
    case EGenesisSwimPhase::Free:
    case EGenesisSwimPhase::Guided: {
        if (SectionElapsed >= Course.FreeSeconds && Phase == EGenesisSwimPhase::Free) {
            Phase = EGenesisSwimPhase::Guided;
            PhaseTime = 0.f;
        }
        const float TimeGuide = Phase == EGenesisSwimPhase::Guided ? FMath::Clamp(PhaseTime / GuideRampSeconds, 0.f, 1.f) : 0.f;
        Sperm->SetGuidance(FMath::Max(TimeGuide, U && U->bAutoSwim ? AutoSwimGuidance : 0.f));
        if (Section != EGenesisRouteSection::Ampulla) {
            TickMechanics(DeltaTime);
            return;
        }
        const FVector Egg = Course.EndLocation();
        if (FVector::Dist(Sperm->GetActorLocation(), Egg) <= FGenesisOviduct::ZonaRadius + 4.f) {
            Phase = EGenesisSwimPhase::Fusion;
            PhaseTime = 0.f;
            ArrivalSeconds = SectionElapsed;
            Sperm->SetFrozen(true);
            EggLight->SetIntensity(35.f);
        }
        else if (SectionElapsed >= ObjectiveAfter) {
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
            const FVector T = Course.Tangent(Course.EndS);
            FVector A, B;
            CrossSection(Course, Course.EndS, A, B);
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
    const bool bW5 = Section == EGenesisRouteSection::Ampulla;
    const FVector Egg = Course.EndLocation();
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
            // Own course along the centre line with a little wander; in W5 the cells lose their way in
            // the cumulus and never reach the zona on their own.
            const float Wander = FMath::PerlinNoise1D(Elapsed * 0.3f + O.Seed);
            const float Stop = bW5 ? Course.EndS - 300.f : Course.EndS - 150.f;
            const FVector Ahead = Course.Center(FMath::Min(O.S + 300.f, Stop))
                + FVector(0.f, Wander * Course.Radius(O.S) * 0.4f, FMath::PerlinNoise1D(Elapsed * 0.27f + O.Seed * 1.7f) * Course.Radius(O.S) * 0.35f);
            O.H = FMath::Lerp(O.H, (Ahead - O.P).GetSafeNormal(), FMath::Clamp(0.8f * DeltaTime, 0.f, 1.f)).GetSafeNormal();
            const float Speed = O.S > (bW5 ? Course.EndS - 350.f : Course.EndS - 200.f) ? 0.f : AGenesisSpermPawn::SwimSpeed * O.Effort * Course.Drag;
            O.P += (O.H * Speed + Course.Flow(O.P, O.S)) * DeltaTime;
            O.S = Course.Project(O.P, O.S);
            FVector Normal;
            Course.Constrain(O.P, O.S, 8.f, Normal);
        }
        Heads.Add(FTransform(O.H.Rotation(), O.P, FVector(0.05f, 0.03f, 0.022f)));
        Tails.Add(FTransform(FRotationMatrix::MakeFromZ(O.H).Rotator(), O.P - O.H * 28.f, FVector(0.007f, 0.007f, 0.45f)));
    }
    if (Heads.Num() > 0) {
        Others->BatchUpdateInstancesTransforms(0, Heads, true, true);
        OtherTails->BatchUpdateInstancesTransforms(0, Tails, true, true);
    }
}

void AGenesisSwimDirector::ForceFinish(FName InResult)
{
    Result = InResult;
    Finish();
}

void AGenesisSwimDirector::Finish()
{
    if (Section == EGenesisRouteSection::Ampulla && SectionSeconds.IsValidIndex(int32(Section))) {
        SectionSeconds[int32(Section)] = SectionElapsed;
    }
    SectionsDone += 1;                                    // W5 itself
    Phase = EGenesisSwimPhase::Finished;
    UE_LOG(LogTemp, Log, TEXT("Genesis C02-B route finished: %s after %.1f s (W5 arrival %.1f s, %d cell switches, shortened %d)"),
        *Result.ToString(), Elapsed, ArrivalSeconds, Switches, bShortened ? 1 : 0);
    UGenesisGameInstance* GI = Cast<UGenesisGameInstance>(GetGameInstance());
    if (GI && GI->StoryStart.Step == EGenesisStoryStep::C02Swim) {
        GI->StoryStart.Life.SpermRouteSections = SectionsDone;
        GI->StoryStart.Life.bSpermRouteShortened = bShortened;
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
    PauseMenu->StartPauseMenu(EGenesisPauseKind::StoryRoute);
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
