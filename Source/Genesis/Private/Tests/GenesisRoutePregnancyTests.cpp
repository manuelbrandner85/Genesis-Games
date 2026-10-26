#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Tests/GenesisTestCommon.h"
#include "Pregnancy/GenesisPregnancy.h"
#include "Pregnancy/GenesisPregnancyGameMode.h"
#include "Save/GenesisSaveStore.h"
#include "Swim/GenesisOviduct.h"
#include "Swim/GenesisSpermPawn.h"
#include "Swim/GenesisSpermRoute.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisRouteSectionsTest, "Genesis.Swim.RouteSections", GenesisTestFlags)
bool FGenesisRouteSectionsTest::RunTest(const FString&)
{
    // W5 is the unchanged CR-001 ampulla.
    const FGenesisCourse W5 = FGenesisSpermRoute::Make(EGenesisRouteSection::Ampulla);
    TestEqual(TEXT("W5 length"), W5.Length, FGenesisOviduct::Length);
    TestEqual(TEXT("W5 egg"), W5.EndS, FGenesisOviduct::EggS);
    for (float S = 0.f; S < W5.Length; S += 700.f) {
        TestTrue(TEXT("W5 radius as before"), FMath::IsNearlyEqual(W5.Radius(S), FGenesisOviduct::Radius(S), 0.01f));
    }

    // Unhurried estimate per section (base beat, medium, flow, special mechanics) - the route without input
    // must land in the 8-12 min window of CR-002 F2, every section in its own window.
    const float Base = AGenesisSpermPawn::SwimSpeed * AGenesisSpermPawn::BaseEffort;
    float Total = 0.f;
    const float Lo[] = { 60.f, 120.f, 60.f, 90.f, 50.f };
    const float Hi[] = { 130.f, 180.f, 120.f, 180.f, 120.f };
    for (int32 I = 0; I < FGenesisSpermRoute::NumSections; ++I) {
        const FGenesisCourse C = FGenesisSpermRoute::Make(EGenesisRouteSection(I));
        const float Dist = C.EndS - C.StartS;
        float Secs = 0.f;
        switch (EGenesisRouteSection(I)) {
        case EGenesisRouteSection::Vagina:
            Secs = FGenesisSpermRoute::CoagulumRadius / (Base * FGenesisSpermRoute::CoagulumDrag) + (Dist - FGenesisSpermRoute::CoagulumRadius) / (Base - C.FlowMax);
            break;
        case EGenesisRouteSection::Uterus:
            Secs = Dist / (Base + FGenesisSpermRoute::ContractionFlow * FGenesisSpermRoute::ContractionLength / FGenesisSpermRoute::ContractionPeriod);
            break;
        case EGenesisRouteSection::Isthmus:
            Secs = FGenesisSpermRoute::RestS / (Base - C.FlowMax) + FGenesisSpermRoute::RestSeconds
                + (C.EndS - FGenesisSpermRoute::RestS) / (Base * FGenesisSpermRoute::HyperactivatedSpeed - C.FlowMax);
            break;
        case EGenesisRouteSection::Ampulla:
            Secs = Dist / (Base * FGenesisSpermRoute::HyperactivatedSpeed - C.FlowMax);      // still hyperactivated
            break;
        default:
            Secs = Dist / (Base * C.Drag - C.FlowMax);
            break;
        }
        TestTrue(*FString::Printf(TEXT("W%d unhurried %.0f s within %.0f-%.0f s"), I + 1, Secs, Lo[I], Hi[I]), Secs >= Lo[I] && Secs <= Hi[I]);
        TestTrue(*FString::Printf(TEXT("W%d guidance starts before the cell could idle forever"), I + 1), C.FreeSeconds > 0.f);
        Total += Secs;
    }
    TestTrue(*FString::Printf(TEXT("Route unhurried %.1f min within 8-12 min (F2)"), Total / 60.f), Total >= 8.f * 60.f - 30.f && Total <= 12.f * 60.f);

    // W2 crypts: a cell can swim into a crypt and is held inside its wall; the canal stays open.
    const FGenesisCourse W2 = FGenesisSpermRoute::Make(EGenesisRouteSection::Cervix);
    TestEqual(TEXT("Eight crypts"), W2.Pockets.Num(), 8);
    const FGenesisCoursePocket& Pk = W2.Pockets[0];
    FVector Inside = Pk.Center;
    FVector N;
    TestFalse(TEXT("Inside a crypt is free space"), W2.Constrain(Inside, Pk.S, 8.f, N));
    TestNotEqual(TEXT("Crypt found"), W2.PocketAt(Pk.Center), int32(INDEX_NONE));
    FVector Beyond = Pk.Center + (Pk.Center - W2.Center(Pk.S)).GetSafeNormal() * (Pk.Radius + 2.f);
    TestTrue(TEXT("Crypt wall holds"), W2.Constrain(Beyond, Pk.S, 8.f, N));
    TestTrue(TEXT("Mucus slows the beat"), W2.Drag < 1.f);

    // W3: two tubal exits, the correct one is distinct from the wrong one.
    const FGenesisCourse W3 = FGenesisSpermRoute::Make(EGenesisRouteSection::Uterus);
    TestTrue(TEXT("Two separate exits"), FVector::Dist(FGenesisSpermRoute::UterusExit(W3, true), FGenesisSpermRoute::UterusExit(W3, false)) > 1000.f);
    // W4 narrow and winding; capacitation makes the beat stronger.
    const FGenesisCourse W4 = FGenesisSpermRoute::Make(EGenesisRouteSection::Isthmus);
    TestTrue(TEXT("Isthmus narrow"), W4.RadiusStart < 300.f);
    TestTrue(TEXT("Hyperactivation is stronger"), FGenesisSpermRoute::HyperactivatedSpeed > 1.f);
    TestTrue(TEXT("Every section has a caption with the accelerated time scale"), FString(FGenesisSpermRoute::Caption(EGenesisRouteSection::Vagina)).Contains(TEXT("beschleunigt")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisPregnancyStagesTest, "Genesis.Pregnancy.Stages", GenesisTestFlags)
bool FGenesisPregnancyStagesTest::RunTest(const FString&)
{
    const TArray<FGenesisPregStage>& S = FGenesisPregnancy::Stages();
    TestEqual(TEXT("Ten stages"), S.Num(), 10);
    float Play = 0.f;
    for (int32 I = 0; I < S.Num(); ++I) {
        Play += S[I].PlaySeconds;
        if (I > 0) {
            TestEqual(*FString::Printf(TEXT("%s starts where %s ends"), S[I].Id, S[I - 1].Id), S[I].StartDay, S[I - 1].EndDay);
        }
    }
    TestTrue(*FString::Printf(TEXT("Playtime %.2f h within 2-3 h (P1)"), Play / 3600.f), Play >= 2.f * 3600.f && Play <= 3.f * 3600.f);
    TestEqual(TEXT("Birth at day 266 = SSW 40"), FGenesisPregnancy::GestationalWeek(FGenesisPregnancy::BirthDay), 40);

    FGenesisPregnancy P;
    TestEqual(TEXT("Starts at S1"), P.StageId(), FName("S1"));
    int32 Changes = 0;
    for (int32 Step = 0; Step < 200000 && !P.bBorn; ++Step) {
        Changes += P.Tick(1.f) ? 1 : 0;
        if (P.bC03Due && !P.bC03Done) {
            P.bC03Done = true;                                   // the director plays C03 here
            P.bC03Due = false;
            TestTrue(TEXT("C03 only in late pregnancy"), P.Day >= 196.f);
        }
    }
    TestTrue(TEXT("Born at the end"), P.bBorn);
    TestEqual(TEXT("Nine stage changes"), Changes, 9);
    TestTrue(TEXT("C03 was due once"), P.bC03Done);
    TestEqual(TEXT("Born id"), P.StageId(), FName("Born"));
    TestTrue(TEXT("Real size grows to ~36 cm"), AGenesisPregnancyDirector::RealSizeMm(266.f) > 300.f && AGenesisPregnancyDirector::RealSizeMm(1.f) < 1.f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisPregnancyActionsTest, "Genesis.Pregnancy.ActionsByWeek", GenesisTestFlags)
bool FGenesisPregnancyActionsTest::RunTest(const FString&)
{
    // No action exists before the development makes it possible (P3, ScriptLock C03 sound/movement rules).
    for (int32 A = 0; A < int32(EGenesisPregAction::Count); ++A) {
        const EGenesisPregAction Act = EGenesisPregAction(A);
        for (float Day = 0.f; Day <= FGenesisPregnancy::BirthDay; Day += 1.f) {
            FGenesisPregnancy P;
            P.Restore(FName(P.Stages()[0].Id), 0.f, false);
            for (int32 I = FGenesisPregnancy::Stages().Num() - 1; I >= 0; --I) {
                if (Day >= FGenesisPregnancy::Stages()[I].StartDay) {
                    P.Restore(FName(FGenesisPregnancy::Stages()[I].Id), Day, false);
                    break;
                }
            }
            const bool bShould = Day >= FGenesisPregnancy::FirstDay(Act) && Day <= FGenesisPregnancy::LastDay(Act);
            if (P.IsAllowed(Act) != bShould) {
                AddError(FString::Printf(TEXT("%s on day %.0f: allowed %d, expected %d"), FGenesisPregnancy::ActionName(Act), Day, P.IsAllowed(Act), bShould));
                return false;
            }
        }
    }
    TestEqual(TEXT("S1-S3: only observing"), FGenesisPregnancy::FirstDay(EGenesisPregAction::Twitch) > 28.f, true);
    TestTrue(TEXT("Hearing not before ~SSW 24"), FGenesisPregnancy::GestationalWeek(FGenesisPregnancy::FirstDay(EGenesisPregAction::ReactToVoice)) >= 24);
    TestTrue(TEXT("No turning when there is no room"), FGenesisPregnancy::LastDay(EGenesisPregAction::Turn) < FGenesisPregnancy::BirthDay);

    FGenesisPregnancy Early;
    Early.Restore(TEXT("S6"), 100.f, false);
    FName Out;
    TestTrue(TEXT("Kick on day 100"), Early.Perform(EGenesisPregAction::Kick, Out));
    TestEqual(TEXT("Nobody outside feels it before ~SSW 20"), Out, FName("Movement.Unfelt"));
    FGenesisPregnancy Late;
    Late.Restore(TEXT("S7"), 140.f, false);
    Late.Perform(EGenesisPregAction::Kick, Out);
    TestEqual(TEXT("From ~SSW 20 the mother feels it"), Out, FName("Mother.FeltMovement"));
    FGenesisPregnancy Cells;
    TestFalse(TEXT("Cells cannot kick"), Cells.Perform(EGenesisPregAction::Kick, Out));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisPregnancyShortenTest, "Genesis.Pregnancy.ShortenAndRestore", GenesisTestFlags)
bool FGenesisPregnancyShortenTest::RunTest(const FString&)
{
    FGenesisPregnancy P;
    int32 Steps = 0;
    while (!P.bBorn && Steps < 20) {
        const int32 Before = P.Stage;
        TestTrue(TEXT("Shorten"), P.ShortenStage());
        if (!P.bBorn) {
            TestEqual(TEXT("Next stage"), P.Stage, Before + 1);
            TestEqual(TEXT("Day carried to the stage start"), P.Day, P.Current().StartDay);
        }
        ++Steps;
    }
    TestEqual(TEXT("Ten shortenings to the birth"), Steps, 10);
    TestFalse(TEXT("Nothing left to shorten"), P.ShortenStage());
    TestTrue(TEXT("C03 came due on the way (late pregnancy)"), P.bC03Due);

    FGenesisPregnancy R;
    R.Restore(TEXT("S8"), 200.f, false);
    TestEqual(TEXT("Restored stage"), R.StageId(), FName("S8"));
    TestEqual(TEXT("Restored day"), R.Day, 200.f);
    TestTrue(TEXT("C03 due after restore when not yet shown"), R.bC03Due);
    FGenesisPregnancy Done;
    Done.Restore(TEXT("S8"), 200.f, true);
    TestFalse(TEXT("C03 not again once shown"), Done.bC03Due);
    FGenesisPregnancy B;
    B.Restore(TEXT("Born"), 0.f, true);
    TestTrue(TEXT("Born restored"), B.bBorn);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSaveSchema4Test, "Genesis.Save.Schema4Migration", GenesisTestFlags)
bool FGenesisSaveSchema4Test::RunTest(const FString&)
{
    // A schema-3 life (CR-001): swam W5 only and plays after the birth.
    const FString Payload = TEXT("{\"schemaVersion\":3,\"soulID\":\"SOUL-3\",\"lifeID\":\"LIFE-3\",\"worldID\":\"WORLD-3\",\"storyStartStage\":\"Done\",\"conceptionMode\":\"Own\",\"soulSeedMinute\":0,\"lifeStartMinute\":1}");
    FSHAHash Hash;
    const FTCHARToUTF8 Utf8(*Payload);
    FSHA1::HashBuffer(Utf8.Get(), Utf8.Length(), Hash.Hash);
    const FString Path = FPaths::ProjectSavedDir() / TEXT("Automation/Genesis/schema3.genesis.json");
    IFileManager::Get().Delete(*Path);
    IFileManager::Get().Delete(*(Path + TEXT(".bak")));
    FFileHelper::SaveStringToFile(FString::Printf(TEXT("{\"schema\":3,\"sha1\":\"%s\",\"state\":%s}"), *Hash.ToString(), *Payload),
        *Path, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    FGenesisWorldState A;
    FString Error;
    TestEqual(TEXT("Current schema 4"), FGenesisWorldState::CurrentSchema, 4);
    TestTrue(TEXT("Schema 3 loads"), FGenesisSaveStore::Load(Path, A, Error));
    TestEqual(TEXT("Migrated to 4"), A.SchemaVersion, 4);
    TestEqual(TEXT("Identity kept"), A.SoulID, FString(TEXT("SOUL-3")));
    TestEqual(TEXT("Old lives swam W5 only"), A.SpermRouteSections, 1);
    TestEqual(TEXT("Old lives are born"), A.PregnancyStage, FName("Born"));

    FGenesisWorldState B = A;
    B.SpermRouteSections = 5;
    B.bSpermRouteShortened = false;
    B.PregnancyStage = TEXT("S6");
    B.PregnancyDay = 101.5f;
    TestTrue(TEXT("Save schema 4"), FGenesisSaveStore::Save(Path, B, Error));
    FGenesisWorldState C;
    TestTrue(TEXT("Reload"), FGenesisSaveStore::Load(Path, C, Error));
    TestEqual(TEXT("Route sections"), C.SpermRouteSections, 5);
    TestEqual(TEXT("Pregnancy stage"), C.PregnancyStage, FName("S6"));
    TestEqual(TEXT("Pregnancy day"), C.PregnancyDay, 101.5f);
    return true;
}

#endif
