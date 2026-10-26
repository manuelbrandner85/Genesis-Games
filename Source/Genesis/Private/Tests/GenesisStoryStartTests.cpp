#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Tests/GenesisTestCommon.h"
#include "Cinematic/GenesisCinematicSubsystem.h"
#include "Cinematic/GenesisLightStrike.h"
#include "Cinematic/GenesisStoryStart.h"
#include "Save/GenesisSaveStore.h"
#include "Swim/GenesisOviduct.h"
#include "Swim/GenesisSpermPawn.h"
#include "Swim/GenesisSwimGameMode.h"
#include "UI/GenesisUserSettings.h"
#include "Engine/GameInstance.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"

namespace
{
    UGenesisCinematicSubsystem* LoadCinematics(FAutomationTestBase& Test)
    {
        UGenesisCinematicSubsystem* C = NewObject<UGenesisCinematicSubsystem>(NewObject<UGameInstance>(GetTransientPackage()));
        FString Error;
        Test.TestTrue(TEXT("Scene registry (ScriptLock 1.3) loads"), C->LoadRegistry(UGenesisCinematicSubsystem::DefaultRegistryPath(), Error));
        return C;
    }

    FGenesisSceneContract SwimContract()
    {
        FGenesisSceneContract C;
        C.SceneID = TEXT("C02");
        C.SoulID = TEXT("SOUL-TEST");
        C.LifeID = TEXT("LIFE-1");
        C.WorldID = TEXT("WORLD-TEST");
        C.ReturnControlState = TEXT("StoryStart");
        C.VariantID = TEXT("TECH");
        C.bTechnicalTest = true;
        C.GameplaySegmentID = FGenesisStoryStart::SwimSegment;
        return C;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSwimSegmentNoSkipTest, "Genesis.Cinematic.SwimSegmentNoSkip", GenesisTestFlags)
bool FGenesisSwimSegmentNoSkipTest::RunTest(const FString&)
{
    using E = EGenesisCinematicState;
    UGenesisCinematicSubsystem* Cine = LoadCinematics(*this);
    TArray<FString> Errors;

    FGenesisSceneContract C = SwimContract();
    TestTrue(TEXT("C02 with swim segment binds"), Cine->Bind(C, Errors));
    TestTrue(TEXT("Play"), Cine->Play(C));
    TestFalse(TEXT("C02 film cannot end before the swim"), Cine->FinishPlayback(C));
    TestTrue(TEXT("Skipping C02-A is allowed ..."), Cine->Skip(C, false));
    TestEqual(TEXT("... and lands in the swim, not past it"), C.CinematicState, E::InGameplaySegment);
    TestFalse(TEXT("The swim itself cannot be skipped"), Cine->Skip(C, true));
    TestEqual(TEXT("Still swimming"), C.CinematicState, E::InGameplaySegment);
    TestFalse(TEXT("No commit during the swim"), Cine->Commit(C, nullptr));
    TestFalse(TEXT("Swim cannot be re-entered"), Cine->BeginSegment(C));
    TestTrue(TEXT("End of the swim"), Cine->EndSegment(C));
    TestTrue(TEXT("Segment done"), C.bGameplaySegmentDone);
    TestFalse(TEXT("No second swim"), Cine->BeginSegment(C));
    TestTrue(TEXT("C02-C..F skippable after the swim"), Cine->Skip(C, false));
    TestEqual(TEXT("Commit pending"), C.CinematicState, E::CommitPending);
    TestTrue(TEXT("Commit"), Cine->Commit(C, nullptr));
    TestTrue(TEXT("Hand back"), Cine->HandBack(C));

    FGenesisSceneContract Wrong = SwimContract();
    Wrong.SceneID = TEXT("C03");
    Errors.Reset();
    TestFalse(TEXT("Only C02 has a playable segment in ScriptLock 1.3"), Cine->Bind(Wrong, Errors));

    FGenesisSceneContract Plain = SwimContract();
    Plain.GameplaySegmentID = NAME_None;
    Errors.Reset();
    Cine->Bind(Plain, Errors);
    Cine->Play(Plain);
    TestFalse(TEXT("Without a segment there is nothing to enter"), Cine->BeginSegment(Plain));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisStoryStartFlowTest, "Genesis.Cinematic.StoryStartFlow", GenesisTestFlags)
bool FGenesisStoryStartFlowTest::RunTest(const FString&)
{
    using S = EGenesisStoryStep;
    UGenesisCinematicSubsystem* Cine = LoadCinematics(*this);
    FGenesisStoryStart Story;
    TestTrue(TEXT("Start"), Story.Start(*Cine));
    TestEqual(TEXT("Begins with C00"), int32(Story.Step), int32(S::C00));
    TestEqual(TEXT("C00 contract plays"), Story.Scene.CinematicState, EGenesisCinematicState::Playing);
    TestTrue(TEXT("Technical test while no master exists"), Story.Scene.bTechnicalTest);
    TestFalse(TEXT("Soul seeded at C00"), Story.Life.SoulID.IsEmpty());
    TestTrue(TEXT("No life yet in C00"), Story.Life.LifeID.IsEmpty());
    TestTrue(TEXT("C00 asks before skipping"), Story.NeedsSkipConfirmation());
    const FString Soul = Story.Life.SoulID;

    TestTrue(TEXT("C00 skipped"), Story.FinishFilm(*Cine, true));
    TestEqual(TEXT("C01 next"), int32(Story.Step), int32(S::C01));
    TestEqual(TEXT("Skipping C00 still records the soul seed"), Story.Life.StoryStartStage, FName("C00"));
    TestEqual(TEXT("Soul seed time"), Story.Life.SoulSeedMinute, int64(0));
    TestFalse(TEXT("C01 asks only once"), Story.NeedsSkipConfirmation());

    TestTrue(TEXT("C01 to the end"), Story.FinishFilm(*Cine, false));
    TestEqual(TEXT("C02 film"), int32(Story.Step), int32(S::C02Film));
    TestFalse(TEXT("New life before C02"), Story.Life.LifeID.IsEmpty());
    TestTrue(TEXT("Life begins strictly after the soul seed"), Story.Life.LifeStartMinute > Story.Life.SoulSeedMinute);
    TestEqual(TEXT("Same soul"), Story.Life.SoulID, Soul);
    TestEqual(TEXT("C02 contract belongs to the new life"), Story.Scene.LifeID, Story.Life.LifeID);
    TestEqual(TEXT("C02 carries the swim segment"), Story.Scene.GameplaySegmentID, FGenesisStoryStart::SwimSegment);

    TestTrue(TEXT("C02-A skipped"), Story.FinishFilm(*Cine, true));
    TestEqual(TEXT("Skip lands in the swim"), int32(Story.Step), int32(S::C02Swim));
    TestEqual(TEXT("Contract in the gameplay segment"), Story.Scene.CinematicState, EGenesisCinematicState::InGameplaySegment);
    TestFalse(TEXT("Swim not skippable"), Story.CanSkip());
    TestFalse(TEXT("Skip during the swim refused"), Story.FinishFilm(*Cine, true));
    TestFalse(TEXT("Unknown swim result refused (no game over state)"), Story.FinishSwim(*Cine, TEXT("GameOver")));
    TestTrue(TEXT("Another cell fused: the life begins anyway"), Story.FinishSwim(*Cine, TEXT("Other")));
    TestEqual(TEXT("C02 end"), int32(Story.Step), int32(S::C02End));
    TestEqual(TEXT("Conception mode kept"), Story.Life.ConceptionMode, FName("Other"));

    TestTrue(TEXT("C02 to the end"), Story.FinishFilm(*Cine, false));
    TestEqual(TEXT("Title after C02 (E1)"), int32(Story.Step), int32(S::Title));
    TestEqual(TEXT("C00, C01, C02 committed once each (technical, in memory)"), Cine->TechTestCommits.Num(), 3);
    TestEqual(TEXT("Life records the three commits"), Story.Life.StoryStartCommits.Num(), 3);
    Story.Complete();
    TestEqual(TEXT("Done"), int32(Story.Step), int32(S::Done));
    TestEqual(TEXT("Stage Done"), Story.Life.StoryStartStage, FName("Done"));
    TestFalse(TEXT("Not active any more"), Story.IsActive());

    // A second story start is a new soul (a new game), never a copy of the first.
    FGenesisStoryStart Second;
    TestTrue(TEXT("Second start"), Second.Start(*Cine));
    TestNotEqual(TEXT("New soul"), Second.Life.SoulID, Soul);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSaveSchema3Test, "Genesis.Save.Schema3Migration", GenesisTestFlags)
bool FGenesisSaveSchema3Test::RunTest(const FString&)
{
    // A schema-2 file as V4.2/CM3 wrote it (identity, no story start).
    const FString Payload = TEXT("{\"schemaVersion\":2,\"soulID\":\"SOUL-2\",\"lifeID\":\"LIFE-2\",\"worldID\":\"WORLD-2\",\"worldSeed\":7,\"lifeNumber\":1,\"worldMinute\":600,\"playerMoneyGE\":12}");
    FSHAHash Hash;
    const FTCHARToUTF8 Utf8(*Payload);
    FSHA1::HashBuffer(Utf8.Get(), Utf8.Length(), Hash.Hash);
    const FString Path = FPaths::ProjectSavedDir() / TEXT("Automation/Genesis/schema2.genesis.json");
    IFileManager::Get().Delete(*Path);
    IFileManager::Get().Delete(*(Path + TEXT(".bak")));
    FFileHelper::SaveStringToFile(FString::Printf(TEXT("{\"schema\":2,\"sha1\":\"%s\",\"state\":%s}"), *Hash.ToString(), *Payload),
        *Path, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);

    FGenesisWorldState A;
    FString Error;
    TestTrue(TEXT("Current schema is at least 3"), FGenesisWorldState::CurrentSchema >= 3);
    TestTrue(TEXT("Schema 2 loads"), FGenesisSaveStore::Load(Path, A, Error));
    TestEqual(TEXT("Migrated to the current schema"), A.SchemaVersion, FGenesisWorldState::CurrentSchema);
    TestEqual(TEXT("Identity kept"), A.SoulID, FString(TEXT("SOUL-2")));
    TestEqual(TEXT("Life kept"), A.LifeID, FString(TEXT("LIFE-2")));
    TestEqual(TEXT("Data kept"), A.PlayerMoneyGE, 12);
    TestEqual(TEXT("Story start counts as passed"), A.StoryStartStage, FName("Done"));
    TestEqual(TEXT("Marked as migrated"), A.ConceptionMode, FName("Migrated"));
    TestTrue(TEXT("Life after soul seed"), A.LifeStartMinute > A.SoulSeedMinute);

    // A new schema-3 life with its story start survives save and load unchanged.
    FGenesisWorldState B = A;
    B.StoryStartStage = TEXT("Done");
    B.ConceptionMode = TEXT("Own");
    B.SoulSeedMinute = 0;
    B.LifeStartMinute = 1;
    B.StoryStartCommits = { TEXT("CIN_C00_X"), TEXT("CIN_C01_X"), TEXT("CIN_C02_X") };
    TestTrue(TEXT("Save schema 3"), FGenesisSaveStore::Save(Path, B, Error));
    FGenesisWorldState C;
    TestTrue(TEXT("Reload"), FGenesisSaveStore::Load(Path, C, Error));
    TestEqual(TEXT("Conception mode"), C.ConceptionMode, FName("Own"));
    TestEqual(TEXT("Story commits"), C.StoryStartCommits.Num(), 3);
    TestEqual(TEXT("Schema"), C.SchemaVersion, FGenesisWorldState::CurrentSchema);

    // A file from a newer build is refused, never half-read.
    const FString Newer = FString::Printf(TEXT("{\"schema\":%d,\"sha1\":\"%s\",\"state\":%s}"), FGenesisWorldState::CurrentSchema + 1, *Hash.ToString(), *Payload);
    FFileHelper::SaveStringToFile(Newer, *Path, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    IFileManager::Get().Delete(*(Path + TEXT(".bak")));
    FGenesisWorldState D;
    TestFalse(TEXT("A newer schema is refused"), FGenesisSaveStore::Load(Path, D, Error));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisFlashDefaultTest, "Genesis.Accessibility.FlashDefault", GenesisTestFlags)
bool FGenesisFlashDefaultTest::RunTest(const FString&)
{
    TestTrue(TEXT("Reduce flashes is ON by default (CR-001)"), UGenesisUserSettings::DefaultReduceFlashes);
    UGenesisUserSettings* Fresh = NewObject<UGenesisUserSettings>(GetTransientPackage());
    Fresh->bReduceFlashes = false;
    Fresh->SetToDefaults();
    TestTrue(TEXT("'Standardwerte' switches flash reduction on"), Fresh->bReduceFlashes);
    UGenesisUserSettings* OldIni = NewObject<UGenesisUserSettings>(GetTransientPackage());
    OldIni->GenesisOptionsVersion = 0;
    OldIni->bReduceFlashes = false;
    OldIni->UpgradeOptions();
    TestTrue(TEXT("An ini from before CR-001 is moved to 'on' once"), OldIni->bReduceFlashes);
    OldIni->bReduceFlashes = false;
    OldIni->UpgradeOptions();
    TestFalse(TEXT("A later choice 'off' is kept"), OldIni->bReduceFlashes);
    TestEqual(TEXT("Options layout 2"), UGenesisUserSettings::CurrentOptionsVersion, 2);

    // Reduced: no strike, only a soft fade; no frame may jump (60 fps).
    const float Dt = 1.f / 60.f;
    float MaxStep = 0.f;
    float Prev = 0.f;
    for (float T = 0.f; T <= FGenesisLightStrike::Duration(true); T += Dt) {
        const float L = FGenesisLightStrike::WhiteLevel(T, true);
        MaxStep = FMath::Max(MaxStep, FMath::Abs(L - Prev));
        Prev = L;
    }
    TestTrue(*FString::Printf(TEXT("Soft fade: largest change per frame %.3f < 0.02"), MaxStep), MaxStep < 0.02f);
    TestTrue(TEXT("Soft rise lasts 1.5 s"), FMath::IsNearlyEqual(FGenesisLightStrike::SoftRise, 1.5f));

    // Normal: exactly one pulse (one rise through 50 %), never a second flash.
    int32 Rises = 0;
    Prev = 0.f;
    for (float T = 0.f; T <= FGenesisLightStrike::Duration(false) + 1.f; T += Dt) {
        const float L = FGenesisLightStrike::WhiteLevel(T, false);
        Rises += Prev < 0.5f && L >= 0.5f ? 1 : 0;
        Prev = L;
    }
    TestEqual(TEXT("At most one pulse"), Rises, 1);
    TestEqual(TEXT("Dark before the point of light"), FGenesisLightStrike::WhiteLevel(0.f, false), 0.f);
    TestEqual(TEXT("Back to the picture at the end"), FGenesisLightStrike::WhiteLevel(FGenesisLightStrike::Duration(false) + 0.01f, false), 0.f);
    const FLinearColor C = FGenesisLightStrike::Color();
    TestTrue(TEXT("White, no saturated red"), C.R - FMath::Min(C.G, C.B) < 0.1f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSwimCourseTest, "Genesis.Swim.Course", GenesisTestFlags)
bool FGenesisSwimCourseTest::RunTest(const FString&)
{
    // Real scale (1 uu = 1 um) and the 60-120 s window (E4) follow from the numbers themselves.
    const float Distance = FGenesisOviduct::EggS - FGenesisOviduct::StartS;
    const float Fastest = Distance / (AGenesisSpermPawn::SwimSpeed - FGenesisOviduct::FlowMax);
    const float Unhurried = Distance / (AGenesisSpermPawn::SwimSpeed * AGenesisSpermPawn::BaseEffort - FGenesisOviduct::FlowMax);
    TestTrue(*FString::Printf(TEXT("Fastest straight swim %.0f s >= 55 s"), Fastest), Fastest >= 55.f);
    TestTrue(*FString::Printf(TEXT("Unhurried swim %.0f s <= 120 s"), Unhurried), Unhurried <= 120.f);
    TestTrue(TEXT("Progressive speed in the human range 25-60 um/s"),
        AGenesisSpermPawn::SwimSpeed * AGenesisSpermPawn::BaseEffort >= 25.f && AGenesisSpermPawn::SwimSpeed * AGenesisSpermPawn::BaseEffort <= 60.f);
    TestEqual(TEXT("Oocyte 120 um across"), FGenesisOviduct::OocyteRadius * 2.f, 120.f);
    TestTrue(TEXT("Guidance starts at 120 s"), FMath::IsNearlyEqual(AGenesisSwimDirector::FreeSeconds, 120.f));

    // Walls: a point outside is pushed back inside, a point inside is left alone.
    for (float S = 0.f; S < FGenesisOviduct::Length; S += 500.f) {
        FVector P = FGenesisOviduct::Center(S) + FVector(0.f, 0.f, 5000.f);
        FVector N;
        TestTrue(TEXT("Outside pushed back"), FGenesisOviduct::Constrain(P, S, 8.f, N));
        FVector Inside = FGenesisOviduct::Center(S);
        TestFalse(TEXT("Centre untouched"), FGenesisOviduct::Constrain(Inside, S, 8.f, N));
        TestTrue(TEXT("Projection finds the course position"), FMath::Abs(FGenesisOviduct::Project(FGenesisOviduct::Center(S), S + 60.f) - S) < 2.f);
        const FVector F = FGenesisOviduct::Flow(FGenesisOviduct::Center(S), S);
        TestTrue(TEXT("Flow runs towards the uterus (against the swim)"), FVector::DotProduct(F, FGenesisOviduct::Tangent(S)) < 0.f);
    }
    return true;
}

#endif
