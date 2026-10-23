#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "GenesisPrototypeCharacter.h"
#include "Editor.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "HighResScreenshot.h"

namespace
{
    const TCHAR* TechSmokeMap = TEXT("/Game/Genesis/TechSmoke/Maps/L_TechSmoke");

    /** Drives the real player character in Play-in-Editor: walk 3 s, run 2 s, stop, jump. */
    class FGenesisPIEDrive : public IAutomationLatentCommand
    {
    public:
        explicit FGenesisPIEDrive(FAutomationTestBase* InTest) : Test(InTest) {}

        virtual bool Update() override
        {
            UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
            AGenesisPrototypeCharacter* C = World ? Cast<AGenesisPrototypeCharacter>(UGameplayStatics::GetPlayerPawn(World, 0)) : nullptr;
            if (!C) {
                Test->AddError(TEXT("No PIE world or player is not AGenesisPrototypeCharacter"));
                return true;
            }
            const double Now = World->GetTimeSeconds();   // game time: independent of editor frame rate
            if (Start < 0.0) {
                Start = Now;
                StartPos = C->GetActorLocation();
                Test->TestNotNull(TEXT("Proxy mesh loaded"), C->GetMesh()->GetSkeletalMeshAsset());
                Test->TestNotNull(TEXT("Anim instance running"), C->GetMesh()->GetAnimInstance());
                return false;
            }
            const double T = Now - Start;
            const float Speed = C->GetVelocity().Size2D();
            const float Feet = C->GetActorLocation().Z - C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
            if (T < 3.0) {
                C->AddMovementInput(FVector::ForwardVector, 1.f);
                MaxWalk = FMath::Max(MaxWalk, Speed);
            } else if (T < 5.0) {
                C->SetSprinting(true);
                C->AddMovementInput(FVector::ForwardVector, 1.f);
                MaxRun = FMath::Max(MaxRun, Speed);
                if (!bShot && T > 4.2) {
                    FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir() / TEXT("G5/pie_running.png"), false, false);
                    bShot = true;
                }
            } else if (T < 6.5) {
                C->SetSprinting(false);              // let it come to rest
                GroundZ = Feet;
            } else if (!bJumped) {
                C->Jump();
                bJumped = true;
                JumpStart = Now;
            } else if (Now - JumpStart < 1.4) {
                if (Now - JumpStart > 0.2) {
                    C->StopJumping();
                }
                Peak = FMath::Max(Peak, Feet - GroundZ);
            } else {
                const float Dist = FVector::Dist2D(StartPos, C->GetActorLocation());
                Test->AddInfo(FString::Printf(TEXT("PIE: walk %.1f cm/s, run %.1f cm/s, distance %.0f cm, jump %.1f cm"), MaxWalk, MaxRun, Dist, Peak));
                Test->TestNearlyEqual(TEXT("PIE walking speed"), MaxWalk, AGenesisPrototypeCharacter::WalkSpeed, 3.f);
                Test->TestNearlyEqual(TEXT("PIE running speed"), MaxRun, AGenesisPrototypeCharacter::SprintSpeed, 3.f);
                // 3 s at 1.75 m/s + 2 s at 4.5 m/s minus acceleration, plus the coast to a stop: ~14 m
                Test->TestTrue(TEXT("PIE distance walk 3 s + run 2 s (12.5-14.5 m)"), Dist > 1250.f && Dist < 1450.f);
                Test->TestNearlyEqual(TEXT("PIE jump height"), Peak, AGenesisPrototypeCharacter::JumpHeight, 4.f);
                Test->TestTrue(TEXT("PIE landed"), C->GetCharacterMovement()->IsMovingOnGround());
                return true;
            }
            return false;
        }

    private:
        FAutomationTestBase* Test;
        double Start = -1.0, JumpStart = 0.0;
        FVector StartPos = FVector::ZeroVector;
        float MaxWalk = 0.f, MaxRun = 0.f, GroundZ = 0.f, Peak = 0.f;
        bool bJumped = false, bShot = false;
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisPIEPlayTest, "Genesis.Gameplay.PIEPlaythrough",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisPIEPlayTest::RunTest(const FString&)
{
    AutomationOpenMap(TechSmokeMap);
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(3.f));      // spawn, shaders, settle on the floor
    ADD_LATENT_AUTOMATION_COMMAND(FGenesisPIEDrive(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}
#endif
