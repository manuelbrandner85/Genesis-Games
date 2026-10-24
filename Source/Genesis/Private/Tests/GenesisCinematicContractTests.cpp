#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Tests/GenesisTestCommon.h"
#include "Cinematic/GenesisCinematicSubsystem.h"
#include "UI/GenesisMenuFlow.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Save/GenesisSaveStore.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"
#include "Engine/GameInstance.h"

namespace
{
    UGenesisCinematicSubsystem* NewCinematics(FAutomationTestBase& Test)
    {
        UGenesisCinematicSubsystem* C = NewObject<UGenesisCinematicSubsystem>(NewObject<UGameInstance>(GetTransientPackage()));   // ClassWithin GameInstance
        FString Error;
        Test.TestTrue(TEXT("Scene registry loads"), C->LoadRegistry(UGenesisCinematicSubsystem::DefaultRegistryPath(), Error));
        return C;
    }

    FGenesisSceneContract TechContract(FName Scene)
    {
        FGenesisSceneContract C;
        C.SceneID = Scene;
        C.SoulID = TEXT("SOUL-TEST");
        C.LifeID = TEXT("LIFE-1");
        C.WorldID = TEXT("WORLD-TEST");
        C.ReturnControlState = TEXT("Gameplay");
        C.VariantID = TEXT("TECH");
        C.bTechnicalTest = true;
        return C;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSceneRegistryTest, "Genesis.Cinematic.Registry", GenesisTestFlags)
bool FGenesisSceneRegistryTest::RunTest(const FString&)
{
    UGenesisCinematicSubsystem* C = NewCinematics(*this);
    TestEqual(TEXT("22 scenes C00-C21"), C->NumScenes(), 22);
    for (int32 I = 0; I < 22; ++I) {
        TestNotNull(*FString::Printf(TEXT("C%02d bound"), I), C->FindScene(FName(*FString::Printf(TEXT("C%02d"), I))));
    }
    const FName Interactive[] = { "C05", "C06", "C08", "C10", "C11", "C16", "C20" };
    int32 Count = 0;
    for (int32 I = 0; I < 22; ++I) {
        Count += C->FindScene(FName(*FString::Printf(TEXT("C%02d"), I)))->bInteractive ? 1 : 0;
    }
    TestEqual(TEXT("7 interactive scenes"), Count, 7);
    for (const FName& Id : Interactive) {
        TestTrue(*(Id.ToString() + TEXT(" interactive")), C->FindScene(Id)->bInteractive);
    }
    TestEqual(TEXT("C20 replays C00"), C->FindScene("C20")->ReplayOf, FName("C00"));
    TestFalse(TEXT("C15 conflict open"), C->FindScene("C15")->OpenConflict.IsEmpty());
    TestFalse(TEXT("Nothing director-approved yet"), C->FindScene("C00")->IsDirectorApproved());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisCinematicTransitionsTest, "Genesis.Cinematic.Transitions", GenesisTestFlags)
bool FGenesisCinematicTransitionsTest::RunTest(const FString&)
{
    using E = EGenesisCinematicState;
    const E All[] = { E::Eligible, E::BindingValidated, E::Ready, E::Playing, E::AwaitingInteraction, E::CommitPending, E::Committed, E::HandedBack, E::Failed };
    int32 Allowed = 0;
    for (E From : All) {
        for (E To : All) {
            Allowed += UGenesisCinematicSubsystem::IsAllowedTransition(From, To) ? 1 : 0;
        }
    }
    TestEqual(TEXT("Exactly the 10 transitions of the contract"), Allowed, 10);
    TestFalse(TEXT("No Playing -> Committed (commit is never bypassed)"), UGenesisCinematicSubsystem::IsAllowedTransition(E::Playing, E::Committed));
    TestFalse(TEXT("No Playing -> HandedBack"), UGenesisCinematicSubsystem::IsAllowedTransition(E::Playing, E::HandedBack));
    TestFalse(TEXT("No AwaitingInteraction -> Committed"), UGenesisCinematicSubsystem::IsAllowedTransition(E::AwaitingInteraction, E::Committed));
    TestFalse(TEXT("HandedBack is final"), UGenesisCinematicSubsystem::IsAllowedTransition(E::HandedBack, E::Eligible));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisCinematicCanonGuardTest, "Genesis.Cinematic.CanonGuard", GenesisTestFlags)
bool FGenesisCinematicCanonGuardTest::RunTest(const FString&)
{
    UGenesisCinematicSubsystem* C = NewCinematics(*this);
    FGenesisSceneContract Real = TechContract("C00");
    Real.bTechnicalTest = false;
    TArray<FString> Errors;
    TestFalse(TEXT("Unapproved scene cannot bind as canon"), C->Bind(Real, Errors));
    TestEqual(TEXT("Failed state"), Real.CinematicState, EGenesisCinematicState::Failed);

    FGenesisSceneContract Conflict = TechContract("C16");
    Conflict.bTechnicalTest = false;
    Errors.Reset();
    C->Bind(Conflict, Errors);
    TestTrue(TEXT("CON33-01 reported"), Errors.ContainsByPredicate([](const FString& S) { return S.Contains(TEXT("CON33-01")); }));

    FGenesisSceneContract Missing = TechContract("C03");
    Missing.SoulID.Reset();
    Errors.Reset();
    TestFalse(TEXT("Contract without SoulID fails"), C->Bind(Missing, Errors));

    FGenesisSceneContract Unknown = TechContract("C99");
    Errors.Reset();
    TestFalse(TEXT("Unknown scene fails"), C->Bind(Unknown, Errors));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisCinematicSkipCommitTest, "Genesis.Cinematic.SkipCommit", GenesisTestFlags)
bool FGenesisCinematicSkipCommitTest::RunTest(const FString&)
{
    UGenesisCinematicSubsystem* C = NewCinematics(*this);
    TArray<FString> Errors;

    // Non-interactive scene: skip goes to CommitPending, the commit still happens once.
    FGenesisSceneContract A = TechContract("C03");
    TestTrue(TEXT("Bind"), C->Bind(A, Errors));
    TestEqual(TEXT("Ready"), A.CinematicState, EGenesisCinematicState::Ready);
    TestFalse(TEXT("No skip before playing"), C->Skip(A, false));
    TestTrue(TEXT("Play"), C->Play(A));
    TestTrue(TEXT("Skip"), C->Skip(A, false));
    TestEqual(TEXT("Skip lands on CommitPending"), A.CinematicState, EGenesisCinematicState::CommitPending);
    TestFalse(TEXT("No hand-back before commit"), C->HandBack(A));
    TestTrue(TEXT("Commit"), C->Commit(A, nullptr));
    TestFalse(TEXT("Second commit refused"), C->Commit(A, nullptr));
    TestTrue(TEXT("Hand back"), C->HandBack(A));
    TestEqual(TEXT("Tech commit recorded once"), C->TechTestCommits.Num(), 1);

    // Interactive scene: skipping never decides for the player.
    FGenesisSceneContract B = TechContract("C05");
    C->Bind(B, Errors);
    C->Play(B);
    TestTrue(TEXT("Skip interactive"), C->Skip(B, false));
    TestEqual(TEXT("Skip waits for the decision"), B.CinematicState, EGenesisCinematicState::AwaitingInteraction);
    TestFalse(TEXT("No commit without decision"), C->Commit(B, nullptr));
    TestFalse(TEXT("Empty answer refused"), C->Answer(B, NAME_None));
    TestTrue(TEXT("Answer"), C->Answer(B, TEXT("Choice_A")));
    TestTrue(TEXT("Commit interactive"), C->Commit(B, nullptr));

    // Skip policies
    FGenesisSceneContract N = TechContract("C04");
    N.SkipPolicy = EGenesisSkipPolicy::AfterFirstView;
    C->Bind(N, Errors);
    C->Play(N);
    TestFalse(TEXT("AfterFirstView: first view not skippable"), C->Skip(N, false));
    TestTrue(TEXT("AfterFirstView: second view skippable"), C->Skip(N, true));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisCinematicLedgerCommitTest, "Genesis.Cinematic.LedgerCommitIdempotent", GenesisTestFlags)
bool FGenesisCinematicLedgerCommitTest::RunTest(const FString&)
{
    UGenesisCinematicSubsystem* C = NewCinematics(*this);
    UGenesisWorldStateSubsystem* W = NewObject<UGenesisWorldStateSubsystem>(GetTransientPackage());
    W->EnsureIdentity();

    // Technical tests never write the world ledger.
    FGenesisSceneContract T = TechContract("C03");
    TArray<FString> Errors;
    C->Bind(T, Errors);
    C->Play(T);
    C->FinishPlayback(T);
    C->Commit(T, W);
    TestEqual(TEXT("Tech test leaves the ledger empty"), W->GetState().Ledger.Num(), 0);

    // A canonical commit (contract state forced, as an approved scene would reach it): applied once.
    FGenesisSceneContract R = TechContract("C03");
    R.bTechnicalTest = false;
    R.LifeID = W->GetState().LifeID;
    R.CinematicState = EGenesisCinematicState::CommitPending;
    TestTrue(TEXT("Commit"), C->Commit(R, W));
    FGenesisSceneContract Again = R;
    Again.CinematicState = EGenesisCinematicState::CommitPending;
    C->Commit(Again, W);
    TestEqual(TEXT("Ledger has the commit once"), W->GetState().Ledger.Num(), 1);
    TestTrue(TEXT("Commit key applied"), W->WasApplied(R.CommitKey()));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisCinematicReplayTest, "Genesis.Cinematic.C20ReplayIdentity", GenesisTestFlags)
bool FGenesisCinematicReplayTest::RunTest(const FString&)
{
    UGenesisCinematicSubsystem* C = NewCinematics(*this);
    TArray<FString> Errors;

    FGenesisSceneContract Rerender = TechContract("C20");
    Rerender.ReplayRecipe.Source = EGenesisReplaySource::ArchiveRender;
    Rerender.ReplayRecipe.SourceSceneID = TEXT("C00");
    TestFalse(TEXT("C20 as new render is refused"), C->Bind(Rerender, Errors));

    FGenesisSceneContract Ok = TechContract("C20");
    Ok.ReplayRecipe.RecipeID = TEXT("RR_C20_FROM_C00");
    Ok.ReplayRecipe.Source = EGenesisReplaySource::OriginalRecording;
    Ok.ReplayRecipe.SourceSceneID = TEXT("C00");
    Ok.ReplayRecipe.MasterAssetPath = TEXT("/Game/Genesis/Cinematics/C00/Master");
    Ok.ReplayRecipe.MasterSha256 = FString::ChrN(64, TEXT('a'));
    Errors.Reset();
    TestTrue(TEXT("C20 from the C00 original recording binds"), C->Bind(Ok, Errors));
    for (const FString& E : Errors) {
        AddError(E);
    }

    FGenesisSceneContract Wrong = TechContract("C03");
    Wrong.ReplayRecipe.Source = EGenesisReplaySource::OriginalRecording;
    Errors.Reset();
    TestFalse(TEXT("Only replay scenes may use an original recording"), C->Bind(Wrong, Errors));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisMenuFlowTest, "Genesis.Menu.FlowGraph", GenesisTestFlags)
bool FGenesisMenuFlowTest::RunTest(const FString&)
{
    FGenesisMenuFlow Flow;
    FString Error;
    TestTrue(TEXT("Menu flow loads"), Flow.LoadFromFile(FGenesisMenuFlow::DefaultPath(), Error));
    TestEqual(TEXT("14 nodes"), Flow.Nodes.Num(), 14);
    for (const FString& E : Flow.Validate()) {
        AddError(TEXT("Menu graph: ") + E);
    }
    TestEqual(TEXT("Starts at BOOT"), Flow.Current, FName("BOOT"));
    TestFalse(TEXT("No jump BOOT -> IN_GAME"), Flow.Go("IN_GAME"));
    TestTrue(TEXT("BOOT -> TITLE_CARD"), Flow.Go("TITLE_CARD"));
    TestTrue(TEXT("-> MAIN_MENU"), Flow.Go("MAIN_MENU"));
    TestTrue(TEXT("-> NEW_GAME"), Flow.Go("NEW_GAME"));
    TestTrue(TEXT("-> IN_GAME"), Flow.Go("IN_GAME"));
    TestTrue(TEXT("-> PAUSE_MENU"), Flow.Go("PAUSE_MENU"));
    TestTrue(TEXT("-> SETTINGS"), Flow.Go("SETTINGS"));
    TestTrue(TEXT("Settings back to the pause menu"), Flow.Go("PAUSE_MENU"));
    TestTrue(TEXT("-> MAIN_MENU"), Flow.Go("MAIN_MENU"));
    TestTrue(TEXT("-> QUIT"), Flow.Go("QUIT"));
    TestTrue(TEXT("-> EXIT"), Flow.Go("EXIT"));

    // The validator really finds dead ends.
    FGenesisMenuFlow Broken = Flow;
    Broken.Nodes.FindChecked("CREDITS").Edges.Reset();
    TestTrue(TEXT("Dead end detected"), Broken.Validate().Num() > 0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSaveMigrationTest, "Genesis.Save.MigrateSchema1", GenesisTestFlags)
bool FGenesisSaveMigrationTest::RunTest(const FString&)
{
    // A schema-1 file as G6 wrote it (no identity fields).
    const FString Payload = TEXT("{\"schemaVersion\":1,\"worldMinute\":510,\"playerMoneyGE\":40}");
    FSHAHash Hash;
    const FTCHARToUTF8 Utf8(*Payload);
    FSHA1::HashBuffer(Utf8.Get(), Utf8.Length(), Hash.Hash);
    const FString Path = FPaths::ProjectSavedDir() / TEXT("Automation/Genesis/schema1.genesis.json");
    IFileManager::Get().Delete(*Path);
    IFileManager::Get().Delete(*(Path + TEXT(".bak")));
    FFileHelper::SaveStringToFile(FString::Printf(TEXT("{\"schema\":1,\"sha1\":\"%s\",\"state\":%s}"), *Hash.ToString(), *Payload),
        *Path, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);

    FGenesisWorldState A, B;
    FString Error;
    TestTrue(TEXT("Schema 1 loads"), FGenesisSaveStore::Load(Path, A, Error));
    TestEqual(TEXT("Migrated to current schema"), A.SchemaVersion, FGenesisWorldState::CurrentSchema);
    TestEqual(TEXT("Data kept"), A.PlayerMoneyGE, 40);
    TestFalse(TEXT("SoulID created"), A.SoulID.IsEmpty());
    TestNotEqual(TEXT("Soul and life differ"), A.SoulID, A.LifeID);
    FGenesisSaveStore::Load(Path, B, Error);
    TestEqual(TEXT("Migration is deterministic"), A.SoulID, B.SoulID);

    TestTrue(TEXT("Save as schema 2"), FGenesisSaveStore::Save(Path, A, Error));
    FGenesisWorldState C;
    TestTrue(TEXT("Reload"), FGenesisSaveStore::Load(Path, C, Error));
    TestEqual(TEXT("Identity survives save/load"), C.WorldID, A.WorldID);
    return true;
}

#endif
