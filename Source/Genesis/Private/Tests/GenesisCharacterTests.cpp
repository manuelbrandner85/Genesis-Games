#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "AIController.h"
#include "Camera/CameraComponent.h"
#include "Character/GenesisCharacter.h"
#include "Character/GenesisCharacterAppearance.h"
#include "Character/GenesisCharacterRegistry.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "GameFramework/WorldSettings.h"
#include "EnhancedActionKeyMapping.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Input/GenesisInputSet.h"
#include "InputMappingContext.h"

namespace GenesisCharacterTests
{
	static const FName PlayerId = TEXT("CHR_PLAYER_ADULT");
	static const FName ProxyM = TEXT("CHR_TEST_PROXY_M");
	static const FName ProxyF = TEXT("CHR_TEST_PROXY_F");

	/** Eigenstaendige Spielwelt mit Boden fuer Bewegungstests. */
	struct FTestWorld
	{
		UWorld* World = nullptr;

		FTestWorld()
		{
			World = UWorld::CreateWorld(EWorldType::Game, false, TEXT("GenesisCharacterTestWorld"));
			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
			FURL URL;
			World->InitializeActorsForPlay(URL);
			World->BeginPlay();
			// Ohne GameMode setzt niemand HasBegunPlay; das erledigt sonst GameState -> WorldSettings.
			World->GetWorldSettings()->NotifyBeginPlay();
		}

		~FTestWorld()
		{
			World->EndPlay(EEndPlayReason::Quit);
			GEngine->DestroyWorldContext(World);
			World->DestroyWorld(false);
		}

		AGenesisCharacter* SpawnCharacter(float HalfHeight = 90.f)
		{
			FActorSpawnParameters Params;
			Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
			AGenesisCharacter* Character = World->SpawnActor<AGenesisCharacter>(FVector(0.f, 0.f, HalfHeight + 2.f), FRotator::ZeroRotator, Params);
			if (Character)
			{
				// Lokaler Controller wie im Spiel: setzt Bewegungsmodus und laesst Bewegungseingaben zu.
				Character->AIControllerClass = AAIController::StaticClass();
				Character->SpawnDefaultController();
			}
			return Character;
		}
	};

	static bool HasKey(const UInputMappingContext* Context, const UInputAction* Action, const FKey& Key)
	{
		for (const FEnhancedActionKeyMapping& Mapping : Context->GetMappings())
		{
			if (Mapping.Action == Action && Mapping.Key == Key)
			{
				return true;
			}
		}
		return false;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisInputMappingTest, "Genesis.Character.Input.KeyboardMouseAndGamepadMapped",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisInputMappingTest::RunTest(const FString&)
{
	using namespace GenesisCharacterTests;
	const UGenesisInputSet* Set = UGenesisInputSet::CreateDefault(GetTransientPackage());
	const UInputMappingContext* C = Set->Context;

	for (const FKey& Key : { EKeys::W, EKeys::A, EKeys::S, EKeys::D, EKeys::Gamepad_Left2D })
	{
		TestTrue(FString::Printf(TEXT("Bewegen: %s"), *Key.ToString()), HasKey(C, Set->Move, Key));
	}
	TestTrue(TEXT("Umsehen: Maus"), HasKey(C, Set->Look, EKeys::Mouse2D));
	TestTrue(TEXT("Umsehen: rechter Stick"), HasKey(C, Set->Look, EKeys::Gamepad_Right2D));
	TestTrue(TEXT("Springen: Leertaste"), HasKey(C, Set->Jump, EKeys::SpaceBar));
	TestTrue(TEXT("Springen: Controller A"), HasKey(C, Set->Jump, EKeys::Gamepad_FaceButton_Bottom));
	TestTrue(TEXT("Laufen: Shift"), HasKey(C, Set->RunHold, EKeys::LeftShift));
	TestTrue(TEXT("Laufen: linker Stickklick"), HasKey(C, Set->RunToggle, EKeys::Gamepad_LeftThumbstick));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisRegistryContractTest, "Genesis.Character.Registry.AllEntriesMeetContract",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisRegistryContractTest::RunTest(const FString&)
{
	const TArray<FGenesisCharacterRegistryEntry>& Entries = GetDefault<UGenesisCharacterRegistry>()->Entries;
	TestTrue(TEXT("Registry hat Eintraege"), Entries.Num() > 0);

	TSet<FName> Seen;
	for (const FGenesisCharacterRegistryEntry& Entry : Entries)
	{
		TestFalse(FString::Printf(TEXT("ID eindeutig: %s"), *Entry.CharacterAssetId.ToString()), Seen.Contains(Entry.CharacterAssetId));
		Seen.Add(Entry.CharacterAssetId);

		TArray<FString> Errors;
		FGenesisMeasuredProportions Measured;
		const bool bOk = UGenesisCharacterRegistry::ValidateAppearance(Entry.Appearance.LoadSynchronous(), Entry.Contract, Errors, &Measured);
		AddInfo(FString::Printf(TEXT("%s: Hoehe %.2f cm, Anker %.2f cm"), *Entry.CharacterAssetId.ToString(), Measured.HeightCm, Measured.AnchorHeightCm));
		for (const FString& Error : Errors)
		{
			AddError(FString::Printf(TEXT("%s: %s"), *Entry.CharacterAssetId.ToString(), *Error));
		}
		TestTrue(FString::Printf(TEXT("Vertrag erfuellt: %s"), *Entry.CharacterAssetId.ToString()), bOk);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisModelSwapTest, "Genesis.Character.Swap.ModelSwapKeepsLogicAndCamera",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisModelSwapTest::RunTest(const FString&)
{
	using namespace GenesisCharacterTests;
	FTestWorld W;
	AGenesisCharacter* Character = W.SpawnCharacter();
	if (!TestNotNull(TEXT("Figur gespawnt"), Character))
	{
		return false;
	}

	const FGenesisCharacterRegistryEntry* PlayerEntry = UGenesisCharacterRegistry::FindEntry(PlayerId);
	const FGenesisCharacterRegistryEntry* FEntry = UGenesisCharacterRegistry::FindEntry(ProxyF);
	if (!TestNotNull(TEXT("Spieler-Eintrag"), PlayerEntry) || !TestNotNull(TEXT("Test-Eintrag F"), FEntry))
	{
		return false;
	}

	TestEqual(TEXT("Start-ID"), Character->CharacterAssetId, PlayerId);
	TestTrue(TEXT("Start-Mesh = Spieler-Aussehen"),
		Character->GetMesh()->GetSkeletalMeshAsset() == PlayerEntry->Appearance.LoadSynchronous()->Mesh.LoadSynchronous());

	// Spiellogik-Zustand, der den Austausch ueberleben muss.
	Character->WalkSpeed = 140.f;
	Character->Tags.Add(TEXT("MissionState_TestFlag"));
	Character->SetRunning(true);
	// Kamerahoehe ueber der Fusssohle = Boom-Z + Kapselhalbhoehe; sie muss bei jedem Modell gleich bleiben.
	const float CameraAboveFeetBefore = Character->GetCameraBoom()->GetRelativeLocation().Z + Character->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight();

	// Neues Modell fuer DIESELBE Figur (wie spaeter Proxy -> Blender-Master).
	UGenesisCharacterAppearance* NewAppearance = FEntry->Appearance.LoadSynchronous();
	TArray<FString> Errors;
	TestTrue(TEXT("Austausch angenommen"), Character->TryApplyAppearanceAsset(NewAppearance, PlayerEntry->Contract, Errors));
	TestEqual(TEXT("Keine Vertragsfehler"), Errors.Num(), 0);

	TestTrue(TEXT("Mesh gewechselt"), Character->GetMesh()->GetSkeletalMeshAsset() == NewAppearance->Mesh.LoadSynchronous());
	TestTrue(TEXT("Animation gesetzt"), Character->GetMesh()->GetAnimInstance() != nullptr);
	TestEqual(TEXT("Figuren-ID unveraendert"), Character->CharacterAssetId, PlayerId);
	TestEqual(TEXT("Gehgeschwindigkeit unveraendert"), Character->WalkSpeed, 140.f);
	TestTrue(TEXT("Laufzustand unveraendert"), Character->IsRunning());
	TestTrue(TEXT("Missions-Tag unveraendert"), Character->Tags.Contains(TEXT("MissionState_TestFlag")));
	const float CameraAboveFeetAfter = Character->GetCameraBoom()->GetRelativeLocation().Z + Character->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight();
	AddInfo(FString::Printf(TEXT("Kamerahoehe ueber Fusssohle: vorher %.2f cm, nachher %.2f cm"), CameraAboveFeetBefore, CameraAboveFeetAfter));
	TestTrue(TEXT("Kamerahoehe ueber Fusssohle unveraendert (Vertrag)"), FMath::IsNearlyEqual(CameraAboveFeetBefore, CameraAboveFeetAfter, 0.01f));
	TestTrue(TEXT("Kamerahoehe = Vertrags-Ankerhoehe"), FMath::IsNearlyEqual(CameraAboveFeetAfter, PlayerEntry->Contract.AnchorHeightCm, 0.01f));
	TestEqual(TEXT("Kapsel = Aussehen"), Character->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight(), NewAppearance->CapsuleHalfHeight);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisContractRejectTest, "Genesis.Character.Swap.ContractViolationRejected",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisContractRejectTest::RunTest(const FString&)
{
	using namespace GenesisCharacterTests;
	FTestWorld W;
	AGenesisCharacter* Character = W.SpawnCharacter();
	const FGenesisCharacterRegistryEntry* PlayerEntry = UGenesisCharacterRegistry::FindEntry(PlayerId);
	if (!TestNotNull(TEXT("Figur"), Character) || !TestNotNull(TEXT("Eintrag"), PlayerEntry))
	{
		return false;
	}
	USkeletalMesh* MeshBefore = Character->GetMesh()->GetSkeletalMeshAsset();
	const FVector BoomBefore = Character->GetCameraBoom()->GetRelativeLocation();

	// Vertrag einer Kinderfigur (120 cm): ein Erwachsenenmodell muss abgelehnt werden.
	FGenesisProportionContract ChildContract = PlayerEntry->Contract;
	ChildContract.ExpectedHeightCm = 120.f;
	ChildContract.AnchorHeightCm = 105.f;
	ChildContract.RequiredBones.Add(TEXT("bone_that_does_not_exist"));

	AddExpectedError(TEXT("Austausch abgelehnt"), EAutomationExpectedErrorFlags::Contains, 3);
	TArray<FString> Errors;
	TestFalse(TEXT("Austausch abgelehnt"), Character->TryApplyAppearanceAsset(PlayerEntry->Appearance.LoadSynchronous(), ChildContract, Errors));
	TestEqual(TEXT("Drei Verstoesse gemeldet (Hoehe, Anker, Knochen)"), Errors.Num(), 3);
	TestTrue(TEXT("Altes Mesh bleibt"), Character->GetMesh()->GetSkeletalMeshAsset() == MeshBefore);
	TestTrue(TEXT("Kamera bleibt"), Character->GetCameraBoom()->GetRelativeLocation().Equals(BoomBefore, 0.01f));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSwapByIdTest, "Genesis.Character.Swap.ByAssetId",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSwapByIdTest::RunTest(const FString&)
{
	using namespace GenesisCharacterTests;
	FTestWorld W;
	AGenesisCharacter* Character = W.SpawnCharacter();
	if (!TestNotNull(TEXT("Figur"), Character))
	{
		return false;
	}

	TestTrue(TEXT("Wechsel auf F"), Character->ApplyAppearance(ProxyF));
	TestEqual(TEXT("ID = F"), Character->CharacterAssetId, ProxyF);
	TestTrue(TEXT("Mesh = Quinn"), GetNameSafe(Character->GetMesh()->GetSkeletalMeshAsset()).Contains(TEXT("Quinn")));

	TestTrue(TEXT("Wechsel auf M"), Character->ApplyAppearance(ProxyM));
	TestTrue(TEXT("Mesh = Manny"), GetNameSafe(Character->GetMesh()->GetSkeletalMeshAsset()).Contains(TEXT("Manny")));

	AddExpectedError(TEXT("nicht in der Registry"), EAutomationExpectedErrorFlags::Contains, 1);
	TestFalse(TEXT("Unbekannte ID abgelehnt"), Character->ApplyAppearance(TEXT("CHR_DOES_NOT_EXIST")));
	TestEqual(TEXT("ID bleibt M"), Character->CharacterAssetId, ProxyM);
	return true;
}

#endif
