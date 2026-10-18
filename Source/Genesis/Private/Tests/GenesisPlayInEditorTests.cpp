#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR

#include "Character/GenesisCharacter.h"
#include "Editor.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"

namespace GenesisPIETests
{
	static const TCHAR* TestMap = TEXT("/Game/Maps/L_GenesisTest");

	/** Steuert die Spielfigur im laufenden PIE wie ein Spieler und misst Gehen, Laufen, Springen. */
	class FDriveCharacterCommand : public IAutomationLatentCommand
	{
	public:
		explicit FDriveCharacterCommand(FAutomationTestBase* InTest) : Test(InTest) {}

		virtual bool Update() override
		{
			UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
			APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
			AGenesisCharacter* Character = PC ? Cast<AGenesisCharacter>(PC->GetPawn()) : nullptr;
			const double Now = FPlatformTime::Seconds();
			if (StageStart == 0.0)
			{
				StageStart = Now;
			}
			if (!Character)
			{
				if (Now - StageStart > 20.0)
				{
					Test->AddError(TEXT("Keine GenesisCharacter-Spielfigur im PIE gefunden."));
					return true;
				}
				return false;
			}

			UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
			const double Elapsed = Now - StageStart;
			auto NextStage = [this, Now](int32 Next) { Stage = Next; StageStart = Now; };

			switch (Stage)
			{
			case 0: // Landen lassen.
				if (Elapsed > 1.0)
				{
					Test->TestTrue(TEXT("Steht auf dem Boden"), Movement->IsMovingOnGround());
					Test->TestTrue(TEXT("Spieler steuert GenesisCharacter"), Character->IsPlayerControlled());
					Start = Character->GetActorLocation();
					NextStage(1);
				}
				return false;
			case 1: // 2 s gehen, wie W gedrueckt.
				Character->AddMovementInput(Character->GetActorForwardVector(), 1.f);
				if (Elapsed > 2.0)
				{
					const float Speed = Character->GetVelocity().Size2D();
					const float Distance = FVector::Dist2D(Start, Character->GetActorLocation());
					Test->AddInfo(FString::Printf(TEXT("Gehen: %.1f cm/s, %.1f cm in 2 s"), Speed, Distance));
					Test->TestTrue(TEXT("Gehtempo ~ WalkSpeed"), FMath::IsNearlyEqual(Speed, Character->WalkSpeed, Character->WalkSpeed * 0.1f));
					Test->TestTrue(TEXT("Mindestens 2 m gegangen"), Distance > 200.f);
					Character->SetRunning(true);
					NextStage(2);
				}
				return false;
			case 2: // 1,5 s laufen.
				Character->AddMovementInput(Character->GetActorForwardVector(), 1.f);
				if (Elapsed > 1.5)
				{
					const float Speed = Character->GetVelocity().Size2D();
					Test->AddInfo(FString::Printf(TEXT("Laufen: %.1f cm/s"), Speed));
					Test->TestTrue(TEXT("Lauftempo ~ RunSpeed"), FMath::IsNearlyEqual(Speed, Character->RunSpeed, Character->RunSpeed * 0.1f));
					Character->SetRunning(false);
					NextStage(3);
				}
				return false;
			case 3: // Abbremsen, dann springen.
				if (Elapsed > 1.0)
				{
					GroundZ = PeakZ = Character->GetActorLocation().Z;
					Character->Jump();
					NextStage(4);
				}
				return false;
			case 4:
				PeakZ = FMath::Max(PeakZ, Character->GetActorLocation().Z);
				if (Elapsed > 0.2)
				{
					Character->StopJumping();
				}
				if (Elapsed > 1.5)
				{
					const float Height = PeakZ - GroundZ;
					Test->AddInfo(FString::Printf(TEXT("Sprunghoehe: %.1f cm"), Height));
					Test->TestTrue(TEXT("Realistische Sprunghoehe 30-60 cm"), Height > 30.f && Height < 60.f);
					Test->TestTrue(TEXT("Wieder gelandet"), Movement->IsMovingOnGround());
					return true;
				}
				return false;
			default:
				return true;
			}
		}

	private:
		FAutomationTestBase* Test;
		int32 Stage = 0;
		double StageStart = 0.0;
		FVector Start = FVector::ZeroVector;
		float GroundZ = 0.f;
		float PeakZ = 0.f;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisPIEMovementTest, "Genesis.Character.PIE.WalkRunJumpInTestLevel",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisPIEMovementTest::RunTest(const FString&)
{
	using namespace GenesisPIETests;
	TestTrue(TEXT("Testlevel geladen"), AutomationOpenMap(TestMap));
	ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
	ADD_LATENT_AUTOMATION_COMMAND(FDriveCharacterCommand(this));
	ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
	return true;
}

#endif
