#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "GenesisPrototypeCharacter.h"
#include "AIController.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "GameFramework/WorldSettings.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/CapsuleComponent.h"

namespace
{
    constexpr EAutomationTestFlags GenesisTestFlags = EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::ProductFilter;
    constexpr float Dt = 1.f / 60.f;

    /** Game world with a 40 x 40 m floor (top at z = 0) and an AI-possessed prototype character. */
    struct FMovementWorld
    {
        UWorld* World = nullptr;
        AGenesisPrototypeCharacter* Character = nullptr;

        FMovementWorld()
        {
            World = UWorld::CreateWorld(EWorldType::Game, false);
            FWorldContext& Ctx = GEngine->CreateNewWorldContext(EWorldType::Game);
            Ctx.SetCurrentWorld(World);
            World->InitializeActorsForPlay(FURL());
            World->BeginPlay();
            if (!World->HasBegunPlay()) {
                // No game mode in this bare world: start play directly, otherwise nothing ticks.
                World->GetWorldSettings()->NotifyBeginPlay();
            }

            AStaticMeshActor* Floor = World->SpawnActor<AStaticMeshActor>(FVector(0.f, 0.f, -50.f), FRotator::ZeroRotator);
            Floor->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);   // static refuses a mesh after spawn
            Floor->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
            Floor->SetActorScale3D(FVector(40.f, 40.f, 1.f));

            Character = World->SpawnActor<AGenesisPrototypeCharacter>(FVector(0.f, 0.f, 150.f), FRotator::ZeroRotator);
            AAIController* Ctrl = World->SpawnActor<AAIController>();
            Ctrl->Possess(Character);
        }

        ~FMovementWorld()
        {
            World->EndPlay(EEndPlayReason::Quit);
            GEngine->DestroyWorldContext(World);
            World->DestroyWorld(false);
        }

        /** Advance the simulation; PerFrame runs before each 1/60 s step. */
        template <typename F>
        void Run(float Seconds, F&& PerFrame)
        {
            for (int32 I = 0, N = FMath::RoundToInt(Seconds / Dt); I < N; ++I) {
                PerFrame();
                ++GFrameCounter;      // tick functions run once per engine frame; each step is a new frame
                World->Tick(LEVELTICK_All, Dt);
            }
        }
        void Run(float Seconds) { Run(Seconds, [] {}); }

        float HorizontalSpeed() const { return Character->GetVelocity().Size2D(); }
        float FeetZ() const { return Character->GetActorLocation().Z - Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight(); }
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisLandTest, "Genesis.Gameplay.LandsOnFloor", GenesisTestFlags)
bool FGenesisLandTest::RunTest(const FString&)
{
    FMovementWorld W;
    W.Run(1.5f);
    AddInfo(FString::Printf(TEXT("Landed: feet at %.2f cm, movement mode %d"), W.FeetZ(), int32(W.Character->GetCharacterMovement()->MovementMode)));
    TestTrue(TEXT("Walking on the floor after the drop"), W.Character->GetCharacterMovement()->IsMovingOnGround());
    TestNearlyEqual(TEXT("Feet at floor height (cm)"), W.FeetZ(), 0.f, 3.f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisWalkRunTest, "Genesis.Gameplay.WalkAndRunSpeed", GenesisTestFlags)
bool FGenesisWalkRunTest::RunTest(const FString&)
{
    FMovementWorld W;
    W.Run(1.f);
    const FVector Start = W.Character->GetActorLocation();
    float MaxWalk = 0.f;
    W.Run(3.f, [&] { W.Character->AddMovementInput(FVector::ForwardVector, 1.f); MaxWalk = FMath::Max(MaxWalk, W.HorizontalSpeed()); });
    const float Walked = FVector::Dist2D(Start, W.Character->GetActorLocation());
    AddInfo(FString::Printf(TEXT("Walk: max %.2f cm/s, %.1f cm in 3 s"), MaxWalk, Walked));
    TestNearlyEqual(TEXT("Walking speed cm/s (1.75 m/s)"), MaxWalk, AGenesisPrototypeCharacter::WalkSpeed, 2.f);
    TestTrue(FString::Printf(TEXT("Walked 3 s: %.0f cm (expected 450-525)"), Walked), Walked > 450.f && Walked < 530.f);

    W.Character->SetSprinting(true);
    float MaxRun = 0.f;
    W.Run(2.f, [&] { W.Character->AddMovementInput(FVector::ForwardVector, 1.f); MaxRun = FMath::Max(MaxRun, W.HorizontalSpeed()); });
    AddInfo(FString::Printf(TEXT("Run: max %.2f cm/s"), MaxRun));
    TestNearlyEqual(TEXT("Running speed cm/s (4.5 m/s)"), MaxRun, AGenesisPrototypeCharacter::SprintSpeed, 2.f);

    W.Character->SetSprinting(false);
    W.Run(1.5f);
    TestTrue(TEXT("Comes to a stop without input"), W.HorizontalSpeed() < 1.f);
    TestTrue(TEXT("Faces the walking direction (orient to movement)"), FMath::Abs(W.Character->GetActorRotation().Yaw) < 2.f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisJumpTest, "Genesis.Gameplay.JumpHeight", GenesisTestFlags)
bool FGenesisJumpTest::RunTest(const FString&)
{
    FMovementWorld W;
    W.Run(1.f);
    const float Base = W.FeetZ();
    float Peak = Base;
    W.Character->Jump();
    W.Run(0.2f, [&] { Peak = FMath::Max(Peak, W.FeetZ()); });
    W.Character->StopJumping();
    W.Run(1.3f, [&] { Peak = FMath::Max(Peak, W.FeetZ()); });
    AddInfo(FString::Printf(TEXT("Jump: %.2f cm"), Peak - Base));
    TestNearlyEqual(TEXT("Jump height cm (standing jump ~45 cm)"), Peak - Base, AGenesisPrototypeCharacter::JumpHeight, 3.f);
    TestTrue(TEXT("Landed again"), W.Character->GetCharacterMovement()->IsMovingOnGround());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisCameraRigTest, "Genesis.Gameplay.CameraRig", GenesisTestFlags)
bool FGenesisCameraRigTest::RunTest(const FString&)
{
    FMovementWorld W;
    const USpringArmComponent* Arm = W.Character->GetSpringArm();
    TestEqual(TEXT("Arm length 2.8 m"), Arm->TargetArmLength, 280.f);
    TestTrue(TEXT("Camera collision test on (no clipping into walls)"), Arm->bDoCollisionTest);
    TestTrue(TEXT("Camera follows control rotation"), Arm->bUsePawnControlRotation);
    TestTrue(TEXT("Pitch limits -70..55 deg"), AGenesisPrototypeCharacter::PitchMin == -70.f && AGenesisPrototypeCharacter::PitchMax == 55.f);
    TestNearlyEqual(TEXT("Capsule half height (1.8 m proxy contract)"), W.Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight(), 96.f, 0.01f);
    return true;
}
#endif
