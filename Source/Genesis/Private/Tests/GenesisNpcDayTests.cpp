#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR

#include "Causality/GenesisCausality.h"
#include "Causality/GenesisNpcMemoryComponent.h"
#include "AIController.h"
#include "Components/StateTreeAIComponent.h"
#include "Editor.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "Npc/GenesisNpc.h"
#include "Save/GenesisSaveSubsystem.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"
#include "Time/GenesisWorldClockSubsystem.h"

namespace GenesisNpcDayTests
{
	struct FCheckpoint
	{
		int32 Hour;
		int32 Minute;
		const TCHAR* Expected[3]; // NPC_TEST_01..03
	};

	// Erwartung aus den Tagesplaenen in Config/DefaultGame.ini.
	static const FCheckpoint Day[] = {
		{ 3, 0, { TEXT("Sleep"), TEXT("Sleep"), TEXT("Sleep") } },
		{ 9, 0, { TEXT("Work"), TEXT("Market"), TEXT("Market") } },
		{ 12, 30, { TEXT("Market"), TEXT("Market"), TEXT("Leisure") } },
		{ 15, 0, { TEXT("Work"), TEXT("Leisure"), TEXT("Leisure") } },
		{ 21, 30, { TEXT("Leisure"), TEXT("Sleep"), TEXT("Leisure") } },
		{ 23, 30, { TEXT("Sleep"), TEXT("Sleep"), TEXT("Sleep") } },
	};

	class FNpcDayCommand : public IAutomationLatentCommand
	{
	public:
		explicit FNpcDayCommand(FAutomationTestBase* InTest) : Test(InTest) {}

		virtual bool Update() override
		{
			UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
			if (!World)
			{
				return Timeout(30.0, TEXT("Keine PIE-Welt."));
			}
			UGenesisSaveSubsystem* Save = World->GetGameInstance()->GetSubsystem<UGenesisSaveSubsystem>();
			UGenesisWorldClockSubsystem* Clock = World->GetSubsystem<UGenesisWorldClockSubsystem>();
			TArray<AGenesisNpcCharacter*> Npcs;
			for (TActorIterator<AGenesisNpcCharacter> It(World); It; ++It)
			{
				Npcs.Add(*It);
			}
			Npcs.Sort([](const AGenesisNpcCharacter& A, const AGenesisNpcCharacter& B) { return A.GetNpcId().LexicalLess(B.GetNpcId()); });
			if (Npcs.Num() != 3 || !Save || !Clock)
			{
				return Timeout(30.0, FString::Printf(TEXT("Erwartet 3 NPCs, gefunden %d."), Npcs.Num()));
			}
			// Erst starten, wenn das Spiel wirklich laeuft: der GameMode setzt beim Start sein Testprofil (Uhrzeit).
			if (!World->HasBegunPlay() || !Save->HasActiveSoul())
			{
				return Timeout(30.0, TEXT("Spiel startet nicht."));
			}
			if (ReadySince == 0.0)
			{
				ReadySince = FPlatformTime::Seconds();
			}
			if (FPlatformTime::Seconds() - ReadySince < 2.0)
			{
				return false;
			}

			const double Now = FPlatformTime::Seconds();
			if (Index < UE_ARRAY_COUNT(Day))
			{
				const FCheckpoint& C = Day[Index];
				if (!bTimeSet)
				{
					Clock->SetClockRunning(false);
					Save->GetMutable().World.WorldDateTime = FDateTime(2026, 6, 15, C.Hour, C.Minute, 0);
					bTimeSet = true;
					PhaseStart = Now;
					return false;
				}
				bool bAllThere = true;
				for (int32 i = 0; i < 3; ++i)
				{
					bAllThere &= Npcs[i]->CurrentActivity == FName(C.Expected[i]) && Npcs[i]->bAtActivitySpot;
				}
				if (bAllThere || Now - PhaseStart > 60.0)
				{
					FString Line = FString::Printf(TEXT("%02d:%02d nach %.1f s:"), C.Hour, C.Minute, Now - PhaseStart);
					for (int32 i = 0; i < 3; ++i)
					{
						const bool bOk = Npcs[i]->CurrentActivity == FName(C.Expected[i]) && Npcs[i]->bAtActivitySpot;
						Line += FString::Printf(TEXT(" %s=%s%s"), *Npcs[i]->GetNpcId().ToString(), *Npcs[i]->CurrentActivity.ToString(), Npcs[i]->bAtActivitySpot ? TEXT("@Platz") : TEXT("(unterwegs)"));
						Test->TestTrue(FString::Printf(TEXT("%02d:%02d %s bei %s"), C.Hour, C.Minute, *Npcs[i]->GetNpcId().ToString(), C.Expected[i]), bOk);
						if (!bOk)
						{
							const AAIController* Ai = Cast<AAIController>(Npcs[i]->GetController());
							Test->AddInfo(FString::Printf(TEXT("Diagnose %s: Position %s, Ziel %s, Abstand %.0f cm, Bewegungsstatus %d, Geschwindigkeit %.0f"),
								*Npcs[i]->GetNpcId().ToString(), *Npcs[i]->GetActorLocation().ToCompactString(), *Npcs[i]->ActivitySpotLocation.ToCompactString(),
								FVector::Dist2D(Npcs[i]->GetActorLocation(), Npcs[i]->ActivitySpotLocation), Ai ? int32(Ai->GetMoveStatus()) : -1, Npcs[i]->GetVelocity().Size2D()));
						}
					}
					Test->AddInfo(Line);
					++Index;
					bTimeSet = false;
				}
				return false;
			}

			return RunPerception(World, Save, Npcs);
		}

	private:
		bool Timeout(double Seconds, const FString& Message)
		{
			if (Start == 0.0)
			{
				Start = FPlatformTime::Seconds();
			}
			if (FPlatformTime::Seconds() - Start > Seconds)
			{
				Test->AddError(Message);
				return true;
			}
			return false;
		}

		static void Place(AGenesisNpcCharacter* Npc, const FVector& Location, float Yaw)
		{
			Npc->SetActorLocationAndRotation(Location, FRotator(0.f, Yaw, 0.f), false, nullptr, ETeleportType::TeleportPhysics);
		}

		/** Wahrnehmung: Tag (Sichtlinie, Wand, Entfernung, Blickrichtung) und Nacht (kuerzere Sichtweite). */
		bool RunPerception(UWorld* World, UGenesisSaveSubsystem* Save, const TArray<AGenesisNpcCharacter*>& Npcs)
		{
			UGenesisCausalitySubsystem* Causality = World->GetGameInstance()->GetSubsystem<UGenesisCausalitySubsystem>();
			APawn* Player = World->GetFirstPlayerController() ? World->GetFirstPlayerController()->GetPawn() : nullptr;
			if (!Causality || !Player)
			{
				Test->AddError(TEXT("Kausalitaets-Subsystem oder Spielfigur fehlt."));
				return true;
			}
			const double Now = FPlatformTime::Seconds();
			const float Z = Npcs[0]->GetActorLocation().Z;

			switch (PerceptionStage)
			{
			case 0: // Tagesablauf anhalten, Szene aufbauen, Himmel auf Mittag.
				for (AGenesisNpcCharacter* Npc : Npcs)
				{
					if (AGenesisNpcAIController* Ai = Cast<AGenesisNpcAIController>(Npc->GetController()))
					{
						Ai->GetStateTreeComponent()->StopLogic(TEXT("Wahrnehmungstest"));
						Ai->StopMovement();
					}
				}
				Save->GetMutable().World.WorldDateTime = FDateTime(2026, 6, 15, 13, 0, 0);
				Player->SetActorLocation(FVector(-300.f, 0.f, Player->GetActorLocation().Z), false, nullptr, ETeleportType::TeleportPhysics);
				Place(Npcs[0], FVector(200.f, 0.f, Z), 180.f);   // 5 m, schaut hin
				Place(Npcs[1], FVector(-800.f, 0.f, Z), 0.f);    // hinter der Wand
				Place(Npcs[2], FVector(5700.f, 0.f, Z), 180.f);  // 60 m entfernt
				PerceptionStage = 1;
				PhaseStart = Now;
				return false;
			case 1:
				if (Now - PhaseStart < 0.5)
				{
					return false;
				}
				{
					const FGenesisEventSpec Spec = MakeSpec(Causality);
					const FName Event = Causality->RecordEventAt(Spec, Player->GetActorLocation(), Player);
					const FGenesisCausalEvent* E = FGenesisCausality::FindEvent(Save->GetCurrent(), Event);
					Test->AddInfo(FString::Printf(TEXT("Tag, Sichtweite %.0f cm: Zeugen = %s"), FGenesisPerception::GetSightRange(World), E ? *FString::JoinBy(E->WitnessIds, TEXT(","), [](FName N) { return N.ToString(); }) : TEXT("-")));
					Test->TestTrue(TEXT("Tag: nur NPC_TEST_01 (5 m, Blick hin) ist Zeuge"), E && E->WitnessIds.Num() == 1 && E->WitnessIds[0] == Npcs[0]->GetNpcId());
					Test->TestTrue(TEXT("Zeuge erinnert sich"), Npcs[0]->GetMemory()->Remembers(Event));
					Test->TestFalse(TEXT("Hinter der Wand: nichts gesehen"), Npcs[1]->GetMemory()->Remembers(Event));
					Test->TestFalse(TEXT("60 m entfernt: nichts gesehen"), Npcs[2]->GetMemory()->Remembers(Event));

					Place(Npcs[0], FVector(200.f, 0.f, Z), 0.f); // gleiche Stelle, schaut weg
					const FName Behind = Causality->RecordEventAt(Spec, Player->GetActorLocation(), Player);
					Test->TestFalse(TEXT("Wer wegschaut, sieht es nicht"), Npcs[0]->GetMemory()->Remembers(Behind));

					// Nacht: Neumond, Sichtweite schrumpft.
					Save->GetMutable().World.WorldDateTime = FDateTime(2026, 8, 12, 23, 45, 0);
					Place(Npcs[0], FVector(1200.f, 0.f, Z), 180.f); // 15 m
					PerceptionStage = 2;
					PhaseStart = Now;
				}
				return false;
			case 2:
				if (Now - PhaseStart < 0.5)
				{
					return false;
				}
				{
					const FGenesisEventSpec Spec = MakeSpec(Causality);
					const float NightRange = FGenesisPerception::GetSightRange(World);
					const FName Far = Causality->RecordEventAt(Spec, Player->GetActorLocation(), Player);
					Place(Npcs[0], FVector(300.f, 0.f, Z), 180.f); // 6 m
					const FName Near = Causality->RecordEventAt(Spec, Player->GetActorLocation(), Player);
					Test->AddInfo(FString::Printf(TEXT("Nacht, Sichtweite %.0f cm"), NightRange));
					Test->TestTrue(TEXT("Nacht: Sichtweite unter 10 m"), NightRange < 1000.f);
					Test->TestFalse(TEXT("Nacht: 15 m entfernt nicht gesehen"), Npcs[0]->GetMemory()->Remembers(Far));
					Test->TestTrue(TEXT("Nacht: 6 m entfernt gesehen"), Npcs[0]->GetMemory()->Remembers(Near));
					Test->TestEqual(TEXT("Kausalgraph widerspruchsfrei"), FGenesisCausality::ValidateGraph(Save->GetCurrent()).Num(), 0);
				}
				return true;
			default:
				return true;
			}
		}

		static FGenesisEventSpec MakeSpec(const UGenesisCausalitySubsystem* Causality)
		{
			FGenesisEventSpec Spec;
			Spec.EventType = TEXT("ARGUMENT");
			Spec.ActorId = Causality->GetCurrentPlayerId();
			Spec.TargetIds = { TEXT("NPC_OFFSCREEN") };
			return Spec;
		}

		FAutomationTestBase* Test;
		int32 Index = 0;
		bool bTimeSet = false;
		double Start = 0.0;
		double PhaseStart = 0.0;
		double ReadySince = 0.0;
		int32 PerceptionStage = 0;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisNpcDayTest, "Genesis.Npc.PIE.DailyScheduleAndPerception",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisNpcDayTest::RunTest(const FString&)
{
	using namespace GenesisNpcDayTests;
	TestTrue(TEXT("Testlevel geladen"), AutomationOpenMap(TEXT("/Game/Maps/L_GenesisTest")));
	ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
	ADD_LATENT_AUTOMATION_COMMAND(FNpcDayCommand(this));
	ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
	return true;
}

#endif
