#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR

#include "Character/GenesisCharacter.h"
#include "Editor.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"
#include "Engine/GameInstance.h"
#include "HAL/FileManager.h"
#include "Misc/Paths.h"
#include "Save/GenesisSaveSubsystem.h"
#include "Time/GenesisWorldClockSubsystem.h"

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

namespace GenesisPIETests
{
	/** Speichert Position, Weltzeit und Leben im laufenden Spiel, veraendert alles und laedt wieder. */
	class FSaveRoundTripCommand : public IAutomationLatentCommand
	{
	public:
		explicit FSaveRoundTripCommand(FAutomationTestBase* InTest) : Test(InTest) {}

		virtual bool Update() override
		{
			UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
			APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
			APawn* Pawn = PC ? PC->GetPawn() : nullptr;
			UGenesisSaveSubsystem* Save = World ? World->GetGameInstance()->GetSubsystem<UGenesisSaveSubsystem>() : nullptr;
			UGenesisWorldClockSubsystem* Clock = World ? World->GetSubsystem<UGenesisWorldClockSubsystem>() : nullptr;
			const double Now = FPlatformTime::Seconds();
			if (StageStart == 0.0)
			{
				StageStart = Now;
			}
			if (!Pawn || !Save || !Clock)
			{
				if (Now - StageStart > 20.0)
				{
					Test->AddError(TEXT("PIE-Spielfigur, Save- oder Clock-Subsystem fehlt."));
					return true;
				}
				return false;
			}

			switch (Stage)
			{
			case 0: // Uhr laeuft im Spiel?
				ClockStart = Clock->GetWorldDateTime();
				Test->TestTrue(TEXT("Testprofil aktiv"), Save->HasActiveSoul());
				Stage = 1;
				StageStart = Now;
				return false;
			case 1:
				if (Now - StageStart > 1.0)
				{
					const double GameSeconds = (Clock->GetWorldDateTime() - ClockStart).GetTotalSeconds();
					Test->AddInfo(FString::Printf(TEXT("Weltuhr: %.1f Spielsekunden in ~1 s Echtzeit"), GameSeconds));
					Test->TestTrue(TEXT("Weltuhr laeuft (ca. 60x)"), GameSeconds > 30.0 && GameSeconds < 600.0);

					// Zustand herstellen und speichern.
					Save->SetDirectoryOverride(FPaths::ProjectIntermediateDir() / TEXT("GenesisPIESaveTest"));
					Pawn->SetActorLocationAndRotation(FVector(300.f, -200.f, Pawn->GetActorLocation().Z), FRotator(0.f, 45.f, 0.f), false, nullptr, ETeleportType::TeleportPhysics);
					Clock->SkipTime(100.f);
					Test->TestTrue(TEXT("Speichern"), Save->SaveToSlot(TEXT("PIERoundTrip")) == EGenesisSaveResult::Ok);
					Saved = Save->GetCurrent();
					SavedLocation = Pawn->GetActorLocation();

					// Alles veraendern.
					Clock->SetClockRunning(false);
					Pawn->SetActorLocation(FVector(0.f, 0.f, Pawn->GetActorLocation().Z), false, nullptr, ETeleportType::TeleportPhysics);
					Clock->SkipTime(400.f);
					Save->GetMutable().Life.MoneyCents += 5000;

					Test->TestTrue(TEXT("Laden"), Save->LoadFromSlot(TEXT("PIERoundTrip")) == EGenesisSaveResult::Ok);
					const FGenesisSaveBundle& L = Save->GetCurrent();
					const FVector Loaded = Pawn->GetActorLocation();
					Test->AddInfo(FString::Printf(TEXT("Position gespeichert %s, geladen %s"), *SavedLocation.ToString(), *Loaded.ToString()));
					Test->TestTrue(TEXT("Position wiederhergestellt"), Loaded.Equals(SavedLocation, 1.f));
					Test->TestTrue(TEXT("Blickrichtung wiederhergestellt"), FMath::IsNearlyEqual(Pawn->GetActorRotation().Yaw, 45.f, 0.5f));
					Test->AddInfo(FString::Printf(TEXT("Weltzeit-Abweichung: %lld Ticks (100 ns)"), (L.World.WorldDateTime - Saved.World.WorldDateTime).GetTicks()));
					Test->TestEqual(TEXT("Weltzeit exakt"), L.World.WorldDateTime, Saved.World.WorldDateTime);
					Test->TestEqual(TEXT("Alter exakt"), FGenesisLifeCycle::GetAgeYears(L.Life, L.World.WorldDateTime),
						FGenesisLifeCycle::GetAgeYears(Saved.Life, Saved.World.WorldDateTime));
					Test->TestTrue(TEXT("Lebensabschnitt"), L.Life.Stage == Saved.Life.Stage);
					Test->TestEqual(TEXT("Geld zurueckgesetzt"), L.Life.MoneyCents, Saved.Life.MoneyCents);
					Test->TestEqual(TEXT("Ort"), L.Life.LocationId, FName(TEXT("/Game/Maps/L_GenesisTest")));
					Test->AddInfo(FString::Printf(TEXT("Geladen: %s, Alter %.3f, Jahreszeit %d"), *L.World.WorldDateTime.ToString(),
						FGenesisLifeCycle::GetAgeYears(L.Life, L.World.WorldDateTime), int32(FGenesisLifeCycle::GetSeason(L.World.WorldDateTime))));

					IFileManager::Get().DeleteDirectory(*(FPaths::ProjectIntermediateDir() / TEXT("GenesisPIESaveTest")), false, true);
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
		FDateTime ClockStart;
		FGenesisSaveBundle Saved;
		FVector SavedLocation = FVector::ZeroVector;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisPIESaveRoundTripTest, "Genesis.Save.PIE.PositionTimeAgeRoundTrip",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisPIESaveRoundTripTest::RunTest(const FString&)
{
	using namespace GenesisPIETests;
	TestTrue(TEXT("Testlevel geladen"), AutomationOpenMap(TestMap));
	ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
	ADD_LATENT_AUTOMATION_COMMAND(FSaveRoundTripCommand(this));
	ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
	return true;
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
