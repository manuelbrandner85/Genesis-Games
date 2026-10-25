#include "Swim/GenesisSpermPawn.h"
#include "Swim/GenesisOviduct.h"
#include "Camera/CameraComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/SpringArmComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
    constexpr int32 TailSegments = 5;
    constexpr float TailSegmentLength = 9.f;          // principal piece ~45 um
    constexpr float BeatHz = 14.f;                     // human flagellar beat ~10-20 Hz

    UStaticMeshComponent* MakePart(AActor* Owner, USceneComponent* Parent, const TCHAR* Name, UStaticMesh* Mesh, const FVector& Scale, const FVector& Location, const FRotator& Rotation)
    {
        UStaticMeshComponent* C = Owner->CreateDefaultSubobject<UStaticMeshComponent>(Name);
        C->SetupAttachment(Parent);
        C->SetStaticMesh(Mesh);
        C->SetRelativeScale3D(Scale);
        C->SetRelativeLocationAndRotation(Location, Rotation);
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        C->SetCastShadow(false);
        return C;
    }
}

AGenesisSpermPawn::AGenesisSpermPawn()
{
    PrimaryActorTick.bCanEverTick = true;
    AutoPossessPlayer = EAutoReceiveInput::Disabled;
    Body = CreateDefaultSubobject<USceneComponent>(TEXT("Body"));
    RootComponent = Body;

    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    // Basic shapes are 100 uu across; 1 uu = 1 um. Head ~5 x 3 um (flattened oval), midpiece ~5 um.
    Head = MakePart(this, Body, TEXT("Head"), Sphere.Object, FVector(0.05f, 0.03f, 0.022f), FVector::ZeroVector, FRotator::ZeroRotator);
    Midpiece = MakePart(this, Body, TEXT("Midpiece"), Cylinder.Object, FVector(0.012f, 0.012f, 0.05f), FVector(-5.f, 0.f, 0.f), FRotator(-90.f, 0.f, 0.f));
    for (int32 I = 0; I < TailSegments; ++I) {
        const float Thin = 0.008f - 0.001f * I;
        Tail.Add(MakePart(this, Body, *FString::Printf(TEXT("Tail%d"), I), Cylinder.Object, FVector(Thin, Thin, TailSegmentLength / 100.f),
            FVector(-7.5f - TailSegmentLength * (I + 0.5f), 0.f, 0.f), FRotator(-90.f, 0.f, 0.f)));
    }

    Arm = CreateDefaultSubobject<USpringArmComponent>(TEXT("Arm"));
    Arm->SetupAttachment(Body);
    Arm->TargetArmLength = 75.f;
    Arm->SocketOffset = FVector(0.f, 0.f, 14.f);
    Arm->bDoCollisionTest = false;
    Arm->bEnableCameraLag = true;
    Arm->CameraLagSpeed = 5.f;
    Arm->bEnableCameraRotationLag = true;
    Arm->CameraRotationLagSpeed = 4.f;
    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    Camera->SetupAttachment(Arm);
    Camera->SetFieldOfView(70.f);

    // The scene needs a light source: a soft lamp travelling with the view (graybox, no look yet).
    Lamp = CreateDefaultSubobject<UPointLightComponent>(TEXT("Lamp"));
    Lamp->SetupAttachment(Body);
    Lamp->SetRelativeLocation(FVector(-40.f, 0.f, 30.f));
    Lamp->SetIntensityUnits(ELightUnits::Candelas);
    Lamp->SetIntensity(30.f);
    Lamp->SetAttenuationRadius(1400.f);
    Lamp->SetCastShadows(false);
}

void AGenesisSpermPawn::PlaceAtStart()
{
    CourseS = FGenesisOviduct::StartS;
    Heading = FGenesisOviduct::Tangent(CourseS);
    Velocity = FVector::ZeroVector;
    SetActorLocationAndRotation(FGenesisOviduct::Center(CourseS), Heading.Rotation());
}

void AGenesisSpermPawn::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (DeltaTime <= 0.f) {
        return;
    }
    FVector P = GetActorLocation();
    CourseS = FGenesisOviduct::Project(P, CourseS);
    if (bFrozen) {
        Velocity = FVector::ZeroVector;
        AnimateFlagellum(DeltaTime);
        return;
    }

    // Steering: the player turns the heading; guidance (auto swim / after 120 s) pulls it towards
    // a point ahead on the centre line, at the end straight to the oocyte.
    const FVector Up = FMath::Abs(Heading.Z) > 0.95f ? FVector::ForwardVector : FVector::UpVector;
    const FVector Right = FVector::CrossProduct(Up, Heading).GetSafeNormal();
    FVector H = Heading;
    H = H.RotateAngleAxis(SteerInput.X * TurnYawDeg * DeltaTime, Up);
    H = H.RotateAngleAxis(-SteerInput.Y * TurnPitchDeg * DeltaTime, Right);

    const FVector Upstream = FGenesisOviduct::Tangent(CourseS);
    const float Ahead = FMath::Min(CourseS + 260.f, FGenesisOviduct::EggS);
    const FVector Goal = FGenesisOviduct::EggS - CourseS < 400.f ? FGenesisOviduct::EggLocation() : FGenesisOviduct::Center(Ahead);
    const FVector ToGoal = (Goal - P).GetSafeNormal();
    const float SteerAmount = FMath::Clamp(SteerInput.Size(), 0.f, 1.f);
    // Rheotaxis is real and passive: a cell that is not steered turns to swim against the flow.
    H = FMath::Lerp(H, Upstream, FMath::Clamp(RheotaxisRate * (1.f - SteerAmount) * DeltaTime, 0.f, 1.f));
    H = FMath::Lerp(H, ToGoal, FMath::Clamp(Guidance * 1.6f * DeltaTime, 0.f, 1.f));
    Heading = H.GetSafeNormal();

    const float Effort = FMath::Max(bBurstInput ? 1.f : BaseEffort, FMath::Lerp(BaseEffort, 1.f, Guidance));
    const FVector Target = Heading * SwimSpeed * Effort + FGenesisOviduct::Flow(P, CourseS);
    Velocity += (Target - Velocity) * (1.f - FMath::Exp(-DeltaTime / ResponseSeconds));
    P += Velocity * DeltaTime;
    CourseS = FGenesisOviduct::Project(P, CourseS);
    FVector Normal;
    if (FGenesisOviduct::Constrain(P, CourseS, 8.f, Normal)) {
        // Along the wall: the outward part of the motion is taken away, the cell slides on.
        Velocity -= Normal * FMath::Min(0.f, FVector::DotProduct(Velocity, Normal));
        Heading = (Heading - Normal * FMath::Min(0.f, FVector::DotProduct(Heading, Normal)) * 1.2f).GetSafeNormal();
        ++WallContacts;
    }
    SetActorLocationAndRotation(P, Heading.Rotation());
    AnimateFlagellum(DeltaTime);
}

void AGenesisSpermPawn::AnimateFlagellum(float DeltaTime)
{
    // Travelling wave from the midpiece to the tip, amplitude growing towards the end.
    BeatPhase += DeltaTime * BeatHz * 2.f * PI * (bFrozen ? 0.4f : 1.f);
    FVector Prev(-7.5f, 0.f, 0.f);
    for (int32 I = 0; I < Tail.Num(); ++I) {
        const float X = -7.5f - TailSegmentLength * (I + 1);
        const FVector End(X, (0.8f + 1.4f * I) * FMath::Sin(BeatPhase - 1.1f * (I + 1)), 0.f);
        const FVector Dir = (End - Prev).GetSafeNormal();
        Tail[I]->SetRelativeLocationAndRotation((Prev + End) * 0.5f, FRotationMatrix::MakeFromZ(Dir).Rotator());
        Prev = End;
    }
}
