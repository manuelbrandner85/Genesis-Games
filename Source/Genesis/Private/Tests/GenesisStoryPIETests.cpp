#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR

#include "Causality/GenesisCausality.h"
#include "Causality/GenesisNpcMemoryComponent.h"
#include "Character/GenesisCharacter.h"
#include "Editor.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "Npc/GenesisNpc.h"
#include "Save/GenesisSaveSubsystem.h"
#include "Story/GenesisStory.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"
#include "Time/GenesisWorldClockSubsystem.h"

namespace GenesisStoryPIETests
{
	/** Spielt TEST_Q01 im laufenden Spiel durch: hingehen, mit der Ansprech-Funktion der Spielfigur reden, antworten. */
	class FPlayQuestCommand : public IAutomationLatentCommand
	{
	public:
		explicit FPlayQuestCommand(FAutomationTestBase* InTest) : Test(InTest) {}

		virtual bool Update() override
		{
			const double Now = FPlatformTime::Seconds();
			if (Start == 0.0)
			{
				Start = Now;
			}
			if (Now - Start > 150.0)
			{
				Test->AddError(FString::Printf(TEXT("Zeitueberschreitung in Phase %d"), Stage));
				return true;
			}

			UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
			APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
			AGenesisCharacter* Player = PC ? Cast<AGenesisCharacter>(PC->GetPawn()) : nullptr;
			UGenesisSaveSubsystem* Save = World ? World->GetGameInstance()->GetSubsystem<UGenesisSaveSubsystem>() : nullptr;
			UGenesisStorySubsystem* Story = World ? World->GetGameInstance()->GetSubsystem<UGenesisStorySubsystem>() : nullptr;
			if (!Player || !Save || !Story || !World->HasBegunPlay() || !Save->HasActiveSoul())
			{
				return false;
			}
			AGenesisNpcCharacter* Market = FindNpc(World, TEXT("NPC_TEST_02"));
			AGenesisNpcCharacter* Workshop = FindNpc(World, TEXT("NPC_TEST_01"));
			AGenesisNpcCharacter* Bystander = FindNpc(World, TEXT("NPC_TEST_03"));
			if (!Market || !Workshop || !Bystander)
			{
				return false;
			}

			switch (Stage)
			{
			case 0: // 09:00: Haendlerin und Nachbarin am Markt, Handwerker in der Werkstatt.
				World->GetSubsystem<UGenesisWorldClockSubsystem>()->SetClockRunning(false);
				Save->GetMutable().World.WorldDateTime = FDateTime(2026, 6, 15, 9, 0, 0);
				Test->TestTrue(TEXT("Testquest automatisch gestartet"), FGenesisStory::FindQuestState(Save->GetCurrent(), TEXT("TEST_Q01")) != nullptr);
				Next();
				return false;
			case 1:
				if (!(Market->bAtActivitySpot && Workshop->bAtActivitySpot && Bystander->bAtActivitySpot))
				{
					return false;
				}
				Test->AddInfo(FString::Printf(TEXT("Ziel: %s"), *Story->GetActiveObjective().ToString()));
				Test->TestFalse(TEXT("Figur ohne Questrolle: kein Gespraech"), StandBehindAndTalk(Player, PC, Bystander));
				Test->TestTrue(TEXT("Haendlerin ansprechen"), StandBehindAndTalk(Player, PC, Market));
				Test->TestTrue(TEXT("Im Gespraech"), Story->IsInDialog());
				Test->AddInfo(FString::Printf(TEXT("%s: %s"), *Story->GetDialogSpeaker().ToString(), *Story->GetDialogText().ToString()));
				Test->TestEqual(TEXT("Drei Antworten"), Story->GetDialogChoiceTexts().Num(), 3);
				Test->TestTrue(TEXT("Antwort 1 (zusagen)"), Story->Choose(0));
				Test->TestFalse(TEXT("Gespraech beendet"), Story->IsInDialog());
				Test->TestEqual(TEXT("Schritt S2"), CurrentStep(Save), FName(TEXT("S2")));
				Next();
				return false;
			case 2:
				if (Now - PhaseStart < 0.3) { return false; }
				Test->TestTrue(TEXT("Handwerker ansprechen"), StandBehindAndTalk(Player, PC, Workshop));
				Test->TestEqual(TEXT("Ohne Vertrauen nur zwei Antworten"), Story->GetDialogChoiceTexts().Num(), 2);
				Test->TestTrue(TEXT("Antwort 1 (danken)"), Story->Choose(0));
				Test->TestEqual(TEXT("Schritt S3"), CurrentStep(Save), FName(TEXT("S3")));
				Next();
				return false;
			case 3:
				if (Now - PhaseStart < 0.3) { return false; }
				{
					Test->TestTrue(TEXT("Zurueck zur Haendlerin"), StandBehindAndTalk(Player, PC, Market));
					const int32 EventsBefore = Save->GetCurrent().World.CausalEvents.Num();
					Test->TestTrue(TEXT("Antwort 1 (Waage abgeben)"), Story->Choose(0));
					const FGenesisQuestState* Q = FGenesisStory::FindQuestState(Save->GetCurrent(), TEXT("TEST_Q01"));
					Test->TestTrue(TEXT("Quest beendet: HELPED_MARKET"), Q && Q->bCompleted && Q->OutcomeId == FName(TEXT("HELPED_MARKET")));
					Test->TestEqual(TEXT("Ein neues Ereignis"), Save->GetCurrent().World.CausalEvents.Num(), EventsBefore + 1);
					const FGenesisCausalEvent& E = Save->GetCurrent().World.CausalEvents.Last();
					Test->AddInfo(FString::Printf(TEXT("Ereignis %s %s -> %s, Zeugen: %s"), *E.EventId.ToString(), *E.EventType.ToString(),
						*FString::JoinBy(E.TargetIds, TEXT(","), [](FName N) { return N.ToString(); }),
						*FString::JoinBy(E.WitnessIds, TEXT(","), [](FName N) { return N.ToString(); })));
					Test->TestTrue(TEXT("Hilfe fuer die Haendlerin eingetragen"), E.EventType == FName(TEXT("HELPED")) && E.TargetIds.Contains(Market->GetNpcId()));
					Test->TestTrue(TEXT("Haendlerin erinnert sich"), Market->GetMemory()->Remembers(E.EventId));
					Test->TestTrue(TEXT("Haendlerin ist dem Spieler nun zugeneigt"), Market->GetMemory()->GetDispositionTowardPlayer() >= EGenesisDisposition::Neutral
						&& Market->GetMemory()->GetAttitudeToward(FGenesisCausality::PlayerSubjectId(0)).Trust > 0.f);
					Test->TestFalse(TEXT("Handwerker in der Werkstatt hat nichts gesehen"), Workshop->GetMemory()->Remembers(E.EventId));
					Test->TestTrue(TEXT("Kein Ziel mehr offen"), Story->GetActiveObjective().IsEmpty());
					Test->TestEqual(TEXT("Kausalgraph widerspruchsfrei"), FGenesisCausality::ValidateGraph(Save->GetCurrent()).Num(), 0);
				}
				return true;
			default:
				return true;
			}
		}

	private:
		void Next()
		{
			++Stage;
			PhaseStart = FPlatformTime::Seconds();
		}

		static AGenesisNpcCharacter* FindNpc(UWorld* World, FName Id)
		{
			for (TActorIterator<AGenesisNpcCharacter> It(World); It; ++It)
			{
				if (It->GetNpcId() == Id) { return *It; }
			}
			return nullptr;
		}

		static FName CurrentStep(const UGenesisSaveSubsystem* Save)
		{
			const FGenesisQuestState* Q = FGenesisStory::FindQuestState(Save->GetCurrent(), TEXT("TEST_Q01"));
			return Q ? Q->CurrentStepId : NAME_None;
		}

		/** Spieler 1,5 m hinter die Figur stellen, zu ihr schauen und die echte Ansprech-Funktion (Taste E) ausloesen. */
		static bool StandBehindAndTalk(AGenesisCharacter* Player, APlayerController* PC, AGenesisNpcCharacter* Npc)
		{
			const FVector Forward = Npc->GetActorForwardVector();
			const FVector Location = Npc->GetActorLocation() - Forward * 150.f;
			Player->SetActorLocationAndRotation(Location, Forward.Rotation(), false, nullptr, ETeleportType::TeleportPhysics);
			PC->SetControlRotation(Forward.Rotation());
			return Player->TryInteract();
		}

		FAutomationTestBase* Test;
		int32 Stage = 0;
		double Start = 0.0;
		double PhaseStart = 0.0;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisQuestPIETest, "Genesis.Story.PIE.PlayTestQuest",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisQuestPIETest::RunTest(const FString&)
{
	using namespace GenesisStoryPIETests;
	TestTrue(TEXT("Testlevel geladen"), AutomationOpenMap(TEXT("/Game/Maps/L_GenesisTest")));
	ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
	ADD_LATENT_AUTOMATION_COMMAND(FPlayQuestCommand(this));
	ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
	return true;
}

#endif
