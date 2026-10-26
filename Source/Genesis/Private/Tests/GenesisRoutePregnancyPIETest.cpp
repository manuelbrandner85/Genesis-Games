#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "GenesisGameInstance.h"
#include "Pregnancy/GenesisPregnancyGameMode.h"
#include "Save/GenesisSaveStore.h"
#include "Swim/GenesisSpermPawn.h"
#include "Swim/GenesisSwimGameMode.h"
#include "UI/GenesisMenuWidget.h"
#include "UI/GenesisUserSettings.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Editor.h"
#include "EngineUtils.h"
#include "GameFramework/WorldSettings.h"
#include "HAL/FileManager.h"
#include "HighResScreenshot.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Tests/AutomationCommon.h"
#include "Tests/AutomationEditorCommon.h"

namespace
{
    FString Evidence() { return FPaths::ProjectSavedDir() / TEXT("CR002"); }

    AGenesisSwimDirector* FindRoute(UWorld* World)
    {
        for (TActorIterator<AGenesisSwimDirector> It(World); It; ++It) return *It;
        return nullptr;
    }

    AGenesisPregnancyDirector* FindPregnancy(UWorld* World)
    {
        for (TActorIterator<AGenesisPregnancyDirector> It(World); It; ++It) return *It;
        return nullptr;
    }

    /** The whole route W1-W5 without any input at 8x game speed: every section is reached, no game
     *  over, total in the 8-12 min window (F2). Writes a JSON report and one screenshot per section. */
    class FRouteNoInputDrive : public IAutomationLatentCommand
    {
    public:
        explicit FRouteNoInputDrive(FAutomationTestBase* InTest) : Test(InTest) {}
        virtual bool Update() override
        {
            UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
            AGenesisSwimDirector* D = World ? FindRoute(World) : nullptr;
            if (!D) {
                return ++Frames > 600 ? Fail(TEXT("no route director")) : false;
            }
            if (!bFast) {
                bFast = true;
                World->GetWorldSettings()->SetTimeDilation(8.f);
                IFileManager::Get().MakeDirectory(*Evidence(), true);
            }
            const int32 Sec = int32(D->GetSection());
            if (Sec != LastSection && D->GetSectionElapsed() > 20.f) {
                LastSection = Sec;
                FScreenshotRequest::RequestScreenshot(Evidence() / FString::Printf(TEXT("route_W%d.png"), Sec + 1), false, false);
            }
            if (!D->IsFinished()) {
                return D->GetElapsed() > 900.f ? Fail(TEXT("route did not end within 15 min")) : false;
            }
            const TArray<float> S = D->GetSectionSeconds();
            FString Per;
            for (int32 I = 0; I < S.Num(); ++I) {
                Per += FString::Printf(TEXT("%s\"W%d\": %.1f"), I ? TEXT(", ") : TEXT(""), I + 1, S[I]);
            }
            const FString Report = FString::Printf(TEXT("{\n  \"test\": \"Genesis.Swim.RoutePIE\",\n  \"input\": \"none\",\n  \"result\": \"%s\",\n  \"total_s\": %.1f,\n  \"sections_s\": {%s},\n  \"sections_done\": %d,\n  \"cell_switches\": %d,\n  \"capacitation_rest\": %s\n}\n"),
                *D->GetResult().ToString(), D->GetElapsed(), *Per, D->GetSectionsDone(), D->GetSwitches(), D->HasRested() ? TEXT("true") : TEXT("false"));
            FFileHelper::SaveStringToFile(Report, *(Evidence() / TEXT("route_no_input.json")));
            Test->AddInfo(Report);
            Test->TestEqual(TEXT("All five sections"), D->GetSectionsDone(), 5);
            Test->TestTrue(TEXT("A result, never a game over"), D->GetResult() == FName("Own") || D->GetResult() == FName("Other"));
            Test->TestTrue(TEXT("Capacitation rest in W4"), D->HasRested());
            Test->TestTrue(*FString::Printf(TEXT("Route %.1f min within ~8-12 min"), D->GetElapsed() / 60.f), D->GetElapsed() >= 7.f * 60.f && D->GetElapsed() <= 12.5f * 60.f);
            World->GetWorldSettings()->SetTimeDilation(1.f);
            return true;
        }
    private:
        bool Fail(const TCHAR* Why) { Test->AddError(Why); return true; }
        FAutomationTestBase* Test;
        int32 Frames = 0;
        int32 LastSection = -1;
        bool bFast = false;
    };

    /** F4 and F3: stuck in a crypt / wrong tube -> another cell takes over; shortening only after the first time. */
    class FRouteSwitchDrive : public IAutomationLatentCommand
    {
    public:
        explicit FRouteSwitchDrive(FAutomationTestBase* InTest) : Test(InTest) {}
        virtual bool Update() override
        {
            UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
            AGenesisSwimDirector* D = World ? FindRoute(World) : nullptr;
            if (!D || World->GetTimeSeconds() < Wait) {
                return !D && ++Frames > 600 ? Fail(TEXT("no route director")) : false;
            }
            switch (Step) {
            case 0:
                Test->TestEqual(TEXT("Starts in W2 (test)"), int32(D->GetSection()), int32(EGenesisRouteSection::Cervix));
                Test->TestTrue(TEXT("Into a crypt"), D->DebugEnterPocket());
                return Next(World, FGenesisSpermRoute::StuckSeconds + 2.f);
            case 1:
                Test->TestEqual(TEXT("Stuck in a crypt: another cell took over"), D->GetSwitches(), 1);
                Test->TestEqual(TEXT("Reason"), D->GetLastSwitchReason(), FString(TEXT("crypt")));
                Test->TestFalse(TEXT("No game over"), D->IsFinished());
                Test->TestEqual(TEXT("Still in W2"), int32(D->GetSection()), int32(EGenesisRouteSection::Cervix));
                UGenesisUserSettings::Get()->bSpermRouteSeen = false;
                Test->TestFalse(TEXT("First time: no shortening"), D->CanShorten());
                UGenesisUserSettings::Get()->bSpermRouteSeen = true;
                Test->TestTrue(TEXT("After the first time: shortening offered"), D->CanShorten());
                Test->TestTrue(TEXT("Shorten"), D->Shorten());
                Test->TestEqual(TEXT("Shortened straight to W5"), int32(D->GetSection()), int32(EGenesisRouteSection::Ampulla));
                Test->TestTrue(TEXT("Marked as shortened"), D->WasShortened());
                Test->TestFalse(TEXT("W5 itself is never shortened"), D->CanShorten());
                UGenesisUserSettings::Get()->bSpermRouteSeen = bSeenBefore;
                return true;
            default:
                return true;
            }
        }
        bool bSeenBefore = false;
    private:
        bool Next(UWorld* World, double S) { ++Step; Wait = World->GetTimeSeconds() + S; return false; }
        bool Fail(const TCHAR* Why) { Test->AddError(Why); return true; }
        FAutomationTestBase* Test;
        int32 Step = 0;
        int32 Frames = 0;
        double Wait = 0.0;
    };

    class FRouteWrongTubeDrive : public IAutomationLatentCommand
    {
    public:
        explicit FRouteWrongTubeDrive(FAutomationTestBase* InTest) : Test(InTest) {}
        virtual bool Update() override
        {
            UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
            AGenesisSwimDirector* D = World ? FindRoute(World) : nullptr;
            if (!D || World->GetTimeSeconds() < Wait) {
                return !D && ++Frames > 600 ? Fail(TEXT("no route director")) : false;
            }
            if (Step == 0) {
                Test->TestTrue(TEXT("Into the wrong tube"), D->DebugWrongExit());
                ++Step;
                Wait = World->GetTimeSeconds() + 1.0;
                return false;
            }
            Test->TestEqual(TEXT("Wrong tube: another cell took over"), D->GetSwitches(), 1);
            Test->TestEqual(TEXT("Reason"), D->GetLastSwitchReason(), FString(TEXT("wrong tube")));
            Test->TestEqual(TEXT("Still in W3"), int32(D->GetSection()), int32(EGenesisRouteSection::Uterus));
            return true;
        }
    private:
        bool Fail(const TCHAR* Why) { Test->AddError(Why); return true; }
        FAutomationTestBase* Test;
        int32 Step = 0;
        int32 Frames = 0;
        double Wait = 0.0;
    };

    /** Pregnancy graybox in PIE: stage-gated actions, outside consequences in the ledger, shorten through
     *  all stages, C03 and C04 as scene contracts, saving between stages, birth save = Born. */
    class FPregnancyDrive : public IAutomationLatentCommand
    {
    public:
        explicit FPregnancyDrive(FAutomationTestBase* InTest) : Test(InTest) {}
        virtual bool Update() override
        {
            UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
            AGenesisPregnancyDirector* D = World ? FindPregnancy(World) : nullptr;
            if (!D || World->GetTimeSeconds() < Wait) {
                return !D && ++Frames > 600 ? Fail(TEXT("no pregnancy director")) : false;
            }
            const UGenesisWorldStateSubsystem* WS = World->GetSubsystem<UGenesisWorldStateSubsystem>();
            FGenesisPregnancy& P = D->GetPregnancy();
            switch (Step) {
            case 0:
                IFileManager::Get().MakeDirectory(*Evidence(), true);
                Test->TestEqual(TEXT("Begins at S1"), P.StageId(), FName("S1"));
                Test->TestFalse(TEXT("Cells cannot kick"), D->PerformAction(EGenesisPregAction::Kick));
                Test->TestTrue(TEXT("Observing works"), D->PerformAction(EGenesisPregAction::Magnify));
                FScreenshotRequest::RequestScreenshot(Evidence() / TEXT("pregnancy_S1.png"), false, false);
                for (int32 I = 0; I < 5; ++I) D->ShortenStage();              // -> S6 (day 84)
                return Next(World, 1.0);
            case 1: {
                Test->TestEqual(TEXT("S6"), P.StageId(), FName("S6"));
                const int32 Ledger = WS->GetState().Ledger.Num();
                Test->TestTrue(TEXT("Kick in S6"), D->PerformAction(EGenesisPregAction::Kick));
                Test->TestEqual(TEXT("Before ~SSW 20 nobody outside feels it"), D->GetLastOutside(), FString(TEXT("Movement.Unfelt")));
                Test->TestEqual(TEXT("Still recorded as an event"), WS->GetState().Ledger.Num(), Ledger + 1);
                FScreenshotRequest::RequestScreenshot(Evidence() / TEXT("pregnancy_S6.png"), false, false);
                D->ShortenStage();                                                   // -> S7 (day 126)
                return Next(World, 1.5);
            }
            case 2:
                Test->TestTrue(TEXT("Kick in S7"), D->PerformAction(EGenesisPregAction::Kick));
                Test->TestEqual(TEXT("The mother feels it"), D->GetLastOutside(), FString(TEXT("Mother.FeltMovement")));
                Test->TestTrue(TEXT("Saved between stages"), IFileManager::Get().FileExists(*FGenesisSaveStore::SlotPath(TEXT("Dev"))));
                D->ShortenStage();                                                   // -> S8
                D->ShortenStage();                                                   // -> S9: late pregnancy, C03 due
                return Next(World, 1.0);
            case 3:
                Test->TestTrue(TEXT("C03 plays in late pregnancy"), D->IsInScene());
                FScreenshotRequest::RequestScreenshot(Evidence() / TEXT("pregnancy_S9_C03.png"), false, false);
                return Next(World, 7.0);
            case 4:
                Test->TestTrue(TEXT("C03 done"), P.bC03Done);
                Test->TestFalse(TEXT("No turning without room (S9)"), P.IsAllowed(EGenesisPregAction::Turn));
                D->ShortenStage();                                                   // -> S10
                D->ShortenStage();                                                   // -> born
                return Next(World, 1.0);
            case 5:
                Test->TestTrue(TEXT("Born"), P.bBorn);
                Test->TestTrue(TEXT("C04 plays at the birth"), D->IsInScene());
                return Next(World, 7.0);
            case 6: {
                Test->TestTrue(TEXT("Handed over after the birth"), D->HasHandedOverAfterBirth());
                FGenesisWorldState Saved;
                FString Error;
                Test->TestTrue(TEXT("Birth save loads"), FGenesisSaveStore::Load(FGenesisSaveStore::SlotPath(TEXT("Dev")), Saved, Error));
                Test->TestEqual(TEXT("Saved as born"), Saved.PregnancyStage, FName("Born"));
                Test->TestTrue(TEXT("World time moved on ~38 weeks"), Saved.WorldMinute >= int64(260) * 24 * 60);
                return true;
            }
            default:
                return true;
            }
        }
    private:
        bool Next(UWorld* World, double S) { ++Step; Wait = World->GetTimeSeconds() + S; return false; }
        bool Fail(const TCHAR* Why) { Test->AddError(Why); return true; }
        FAutomationTestBase* Test;
        int32 Step = 0;
        int32 Frames = 0;
        double Wait = 0.0;
    };

    class FPregnancyCleanup : public IAutomationLatentCommand
    {
    public:
        virtual bool Update() override
        {
            AGenesisPregnancyDirector::bStayAfterBirthForTests = false;
            FGenesisSaveStore::SlotDirectoryOverride.Reset();
            return true;
        }
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisRoutePIETest, "Genesis.Swim.RoutePIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisRoutePIETest::RunTest(const FString&)
{
    UGenesisUserSettings::Get()->bAutoSwim = false;
    AGenesisSwimDirector::StandaloneStartSection = EGenesisRouteSection::Vagina;
    AutomationOpenMap(UGenesisGameInstance::SwimMap);
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2.f));
    ADD_LATENT_AUTOMATION_COMMAND(FRouteNoInputDrive(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisRouteSwitchPIETest, "Genesis.Swim.RouteNoGameOverPIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisRouteSwitchPIETest::RunTest(const FString&)
{
    UGenesisUserSettings::Get()->bAutoSwim = false;
    AGenesisSwimDirector::StandaloneStartSection = EGenesisRouteSection::Cervix;
    AutomationOpenMap(UGenesisGameInstance::SwimMap);
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2.f));
    FRouteSwitchDrive* Drive = new FRouteSwitchDrive(this);
    Drive->bSeenBefore = UGenesisUserSettings::Get()->bSpermRouteSeen;
    FAutomationTestFramework::Get().EnqueueLatentCommand(MakeShareable(Drive));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisRouteWrongTubePIETest, "Genesis.Swim.RouteWrongTubePIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisRouteWrongTubePIETest::RunTest(const FString&)
{
    AGenesisSwimDirector::StandaloneStartSection = EGenesisRouteSection::Uterus;
    AutomationOpenMap(UGenesisGameInstance::SwimMap);
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2.f));
    ADD_LATENT_AUTOMATION_COMMAND(FRouteWrongTubeDrive(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisPregnancyPIETest, "Genesis.Pregnancy.PIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FGenesisPregnancyPIETest::RunTest(const FString&)
{
    const FString Dir = FPaths::ProjectSavedDir() / TEXT("Automation/Genesis/PregnancySlots");
    IFileManager::Get().DeleteDirectory(*Dir, false, true);
    FGenesisSaveStore::SlotDirectoryOverride = Dir;
    AGenesisPregnancyDirector::bStayAfterBirthForTests = true;
    AutomationOpenMap(UGenesisGameInstance::PregnancyMap);
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2.f));
    ADD_LATENT_AUTOMATION_COMMAND(FPregnancyDrive(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    ADD_LATENT_AUTOMATION_COMMAND(FPregnancyCleanup());
    return true;
}
#endif
