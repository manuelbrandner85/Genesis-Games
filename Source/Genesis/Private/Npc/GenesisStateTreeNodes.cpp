#include "Npc/GenesisStateTreeNodes.h"

#include "AIController.h"
#include "Navigation/PathFollowingComponent.h"
#include "Genesis.h"
#include "Npc/GenesisNpc.h"
#include "Npc/GenesisNpcTypes.h"
#include "SmartObjectDefinition.h"
#include "SmartObjectRequestTypes.h"
#include "SmartObjectSubsystem.h"
#include "StateTree.h"
#include "StateTreeExecutionContext.h"

#if WITH_EDITOR
#include "Components/StateTreeAIComponentSchema.h"
#include "StateTreeEditorData.h"
#include "StateTreeEditingSubsystem.h"
#include "StateTreeEditorModule.h"
#include "StateTreeEditorSchema.h"
#include "StateTreeCompilerLog.h"
#include "StateTreeState.h"
#include "UObject/Package.h"
#include "UObject/SavePackage.h"
#endif

#if WITH_EDITOR
namespace GenesisAssetBuild
{
	/** Paket fuer ein (Neu-)Erzeugen vorbereiten: vorhandenes Paket voll laden und das alte Objekt beiseiteschieben. */
	UPackage* PreparePackage(const FString& PackageName, FName AssetName)
	{
		UPackage* Package = FindPackage(nullptr, *PackageName);
		if (!Package && FPackageName::DoesPackageExist(PackageName))
		{
			Package = LoadPackage(nullptr, *PackageName, LOAD_None);
		}
		if (Package)
		{
			Package->FullyLoad();
			if (UObject* Existing = StaticFindObjectFast(UObject::StaticClass(), Package, AssetName))
			{
				Existing->ClearFlags(RF_Public | RF_Standalone);
				Existing->Rename(nullptr, GetTransientPackage(), REN_DontCreateRedirectors | REN_NonTransactional);
			}
			return Package;
		}
		return CreatePackage(*PackageName);
	}
}
#endif

namespace
{
	AAIController* GetController(const FStateTreeExecutionContext& Context)
	{
		return Cast<AAIController>(Context.GetOwner());
	}

	AGenesisNpcCharacter* GetNpc(const FStateTreeExecutionContext& Context)
	{
		const AAIController* Controller = GetController(Context);
		return Controller ? Cast<AGenesisNpcCharacter>(Controller->GetPawn()) : nullptr;
	}

	/** Naechsten freien Platz fuer die Aktivitaet reservieren und hingehen. */
	bool ClaimAndMove(FStateTreeExecutionContext& Context, FGenesisActivityTaskData& Data)
	{
		AAIController* Controller = GetController(Context);
		AGenesisNpcCharacter* Npc = GetNpc(Context);
		USmartObjectSubsystem* SmartObjects = Npc ? USmartObjectSubsystem::GetCurrent(Npc->GetWorld()) : nullptr;
		const FGameplayTag Tag = UGenesisNpcSettings::ActivityTag(Data.Activity);
		if (!Controller || !Npc || !SmartObjects || !Tag.IsValid())
		{
			return false;
		}

		FSmartObjectRequestFilter Filter;
		Filter.ActivityRequirements = FGameplayTagQuery::MakeQuery_MatchTag(Tag);
		const FVector Origin = Npc->GetActorLocation();
		FSmartObjectRequest Request(FBox::BuildAABB(Origin, FVector(15000.f)), Filter);
		TArray<FSmartObjectRequestResult> Results;
		SmartObjects->FindSmartObjects(Request, Results, FConstStructView::Make(FSmartObjectActorUserData(Npc)));

		// Naechste freie Plaetze zuerst.
		Results.Sort([SmartObjects, Origin](const FSmartObjectRequestResult& A, const FSmartObjectRequestResult& B)
		{
			const TOptional<FTransform> TA = SmartObjects->GetSlotTransform(A);
			const TOptional<FTransform> TB = SmartObjects->GetSlotTransform(B);
			return FVector::DistSquared(Origin, TA ? TA->GetLocation() : Origin) < FVector::DistSquared(Origin, TB ? TB->GetLocation() : Origin);
		});
		for (const FSmartObjectRequestResult& Result : Results)
		{
			if (Result.SlotHandle == Data.AvoidSlot && Results.Num() > 1)
			{
				continue;
			}
			const FSmartObjectClaimHandle Claim = SmartObjects->MarkSlotAsClaimed(Result.SlotHandle, ESmartObjectClaimPriority::Normal, FConstStructView::Make(FSmartObjectActorUserData(Npc)));
			if (!Claim.IsValid())
			{
				continue;
			}
			const TOptional<FTransform> SlotTransform = SmartObjects->GetSlotTransform(Claim);
			Data.Claim = Claim;
			Data.SlotLocation = SlotTransform ? SlotTransform->GetLocation() : Origin;
			Data.SlotRotation = SlotTransform ? SlotTransform->Rotator() : Npc->GetActorRotation();
			Data.ApproachLocation = Data.SlotLocation - FRotator(0.f, Data.SlotRotation.Yaw, 0.f).Vector() * 100.f;
			Data.bApproachReached = false;
			Controller->MoveToLocation(Data.ApproachLocation, 25.f, false, true, true, false);
			Npc->ActivitySpotLocation = Data.SlotLocation;
			return true;
		}
		return false;
	}
}

bool FGenesisScheduledActivityCondition::TestCondition(FStateTreeExecutionContext& Context) const
{
	const FInstanceDataType& Data = Context.GetInstanceData(*this);
	const AGenesisNpcCharacter* Npc = GetNpc(Context);
	return Npc && Npc->GetScheduledActivity() == Data.Activity;
}

EStateTreeRunStatus FGenesisActivityTask::EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const
{
	FInstanceDataType& Data = Context.GetInstanceData(*this);
	Data.Claim = FSmartObjectClaimHandle();
	Data.bOccupied = false;
	Data.StuckTimer = 0.f;
	Data.AvoidSlot = FSmartObjectSlotHandle();
	Data.RetryTimer = 0.f;
	if (AGenesisNpcCharacter* Npc = GetNpc(Context))
	{
		Npc->CurrentActivity = Data.Activity;
		Npc->bAtActivitySpot = false;
	}
	// Kurze Reaktionszeit vor der Platzsuche; beim Spielstart ist das Smart-Object-System dann bereit.
	Data.RetryTimer = 0.5f;
	return EStateTreeRunStatus::Running;
}

EStateTreeRunStatus FGenesisActivityTask::Tick(FStateTreeExecutionContext& Context, const float DeltaTime) const
{
	FInstanceDataType& Data = Context.GetInstanceData(*this);
	AGenesisNpcCharacter* Npc = GetNpc(Context);
	AAIController* Controller = GetController(Context);
	if (!Npc || !Controller)
	{
		return EStateTreeRunStatus::Failed;
	}
	// Plan sieht etwas anderes vor: Zustand beenden, der StateTree waehlt neu.
	if (Npc->GetScheduledActivity() != Data.Activity)
	{
		return EStateTreeRunStatus::Succeeded;
	}
	if (!Data.Claim.IsValid())
	{
		Data.RetryTimer -= DeltaTime;
		if (Data.RetryTimer <= 0.f)
		{
			Data.RetryTimer = 2.f;
			ClaimAndMove(Context, Data);
		}
		return EStateTreeRunStatus::Running;
	}
	if (Data.bOccupied)
	{
		return EStateTreeRunStatus::Running;
	}

	if (Npc->GetVelocity().Size2D() >= 10.f)
	{
		Data.StuckTimer = 0.f;
	}

	if (!Data.bApproachReached && FVector::Dist2D(Npc->GetActorLocation(), Data.ApproachLocation) < 50.f)
	{
		Data.bApproachReached = true;
		Controller->MoveToLocation(Data.SlotLocation, 20.f, false, true, true, false);
	}

	if (FVector::Dist2D(Npc->GetActorLocation(), Data.SlotLocation) < 60.f)
	{
		Data.StuckTimer = 0.f;
		Controller->StopMovement();
		Npc->SetActorRotation(FRotator(0.f, Data.SlotRotation.Yaw, 0.f));
		if (USmartObjectSubsystem* SmartObjects = USmartObjectSubsystem::GetCurrent(Npc->GetWorld()))
		{
			Data.bOccupied = SmartObjects->MarkSlotAsOccupied(Data.Claim, UGenesisActivityBehaviorDefinition::StaticClass()) != nullptr;
		}
		Npc->bAtActivitySpot = true;
	}
	else if (Npc->GetVelocity().Size2D() < 10.f && (Data.StuckTimer += DeltaTime) > 3.f)
	{
		// Weg versperrt (z. B. sitzt jemand davor): Platz freigeben und einen anderen suchen.
		if (USmartObjectSubsystem* SmartObjects = USmartObjectSubsystem::GetCurrent(Npc->GetWorld()))
		{
			SmartObjects->MarkSlotAsFree(Data.Claim);
		}
		Data.AvoidSlot = Data.Claim.SlotHandle;
		Data.Claim = FSmartObjectClaimHandle();
		Data.StuckTimer = 0.f;
		// Erst einen Schritt zur Seite treten, dann neu planen.
		const FVector Side = FVector::CrossProduct((Data.SlotLocation - Npc->GetActorLocation()).GetSafeNormal2D(), FVector::UpVector);
		Controller->MoveToLocation(Npc->GetActorLocation() + Side * (FMath::RandBool() ? 150.f : -150.f), 30.f, false, true, true, false);
		Data.RetryTimer = 2.f;
		return EStateTreeRunStatus::Running;
	}
	else if (Controller->GetMoveStatus() == EPathFollowingStatus::Idle)
	{
		// Weg verloren oder blockiert: in Abstaenden neu losgehen.
		Data.RetryTimer -= DeltaTime;
		if (Data.RetryTimer <= 0.f)
		{
			Data.RetryTimer = 1.f;
			Controller->MoveToLocation(Data.bApproachReached ? Data.SlotLocation : Data.ApproachLocation, 20.f, false, true, true, false);
		}
	}
	return EStateTreeRunStatus::Running;
}

void FGenesisActivityTask::ExitState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const
{
	FInstanceDataType& Data = Context.GetInstanceData(*this);
	AGenesisNpcCharacter* Npc = GetNpc(Context);
	if (Data.Claim.IsValid() && Npc)
	{
		if (USmartObjectSubsystem* SmartObjects = USmartObjectSubsystem::GetCurrent(Npc->GetWorld()))
		{
			SmartObjects->MarkSlotAsFree(Data.Claim);
		}
	}
	Data.Claim = FSmartObjectClaimHandle();
	if (Npc)
	{
		Npc->bAtActivitySpot = false;
	}
}

UStateTree* UGenesisNpcAssetBuilder::BuildDailyLifeStateTree(const FString& PackageName)
{
#if WITH_EDITOR
	const FName AssetName = FName(*FPackageName::GetShortName(PackageName));
	UPackage* Package = GenesisAssetBuild::PreparePackage(PackageName, AssetName);
	UStateTree* Tree = NewObject<UStateTree>(Package, AssetName, RF_Public | RF_Standalone | RF_Transactional);

	const TSubclassOf<UStateTreeSchema> SchemaClass = UStateTreeAIComponentSchema::StaticClass();
	FStateTreeEditorModule& EditorModule = FStateTreeEditorModule::GetModule();
	UStateTreeEditorData* EditorData = NewObject<UStateTreeEditorData>(Tree, EditorModule.GetEditorDataClass(SchemaClass.Get()), FName(), RF_Transactional);
	Tree->EditorData = EditorData;
	EditorData->Schema = NewObject<UStateTreeSchema>(EditorData, SchemaClass, FName(), RF_Transactional);
	EditorData->EditorSchema = NewObject<UStateTreeEditorSchema>(EditorData, EditorModule.GetEditorSchemaClass(SchemaClass.Get()), FName(), RF_Transactional);

	UStateTreeState& Root = EditorData->AddSubTree(FName(TEXT("Tagesablauf")));
	// Reihenfolge = Prioritaet. Freizeit zuletzt und ohne Bedingung: es gibt immer etwas zu tun.
	const TCHAR* Activities[] = { TEXT("Sleep"), TEXT("Work"), TEXT("Market"), TEXT("Leisure") };
	for (const TCHAR* Activity : Activities)
	{
		UStateTreeState& State = Root.AddChildState(FName(Activity));
		if (FName(Activity) != FName(TEXT("Leisure")))
		{
			State.AddEnterCondition<FGenesisScheduledActivityCondition>().GetInstanceData().Activity = FName(Activity);
		}
		State.AddTask<FGenesisActivityTask>().GetInstanceData().Activity = FName(Activity);
		State.AddTransition(EStateTreeTransitionTrigger::OnStateCompleted, EStateTreeTransitionType::GotoState, &Root);
		State.AddTransition(EStateTreeTransitionTrigger::OnStateFailed, EStateTreeTransitionType::GotoState, &Root);
	}

	FStateTreeCompilerLog Log;
	if (!UStateTreeEditingSubsystem::CompileStateTree(Tree, Log))
	{
		Log.DumpToLog(LogGenesis);
		UE_LOG(LogGenesis, Error, TEXT("StateTree '%s' konnte nicht kompiliert werden."), *PackageName);
		return nullptr;
	}

	FSavePackageArgs SaveArgs;
	SaveArgs.TopLevelFlags = RF_Public | RF_Standalone;
	const FString FileName = FPackageName::LongPackageNameToFilename(PackageName, FPackageName::GetAssetPackageExtension());
	UPackage::SavePackage(Package, Tree, *FileName, SaveArgs);
	return Tree;
#else
	return nullptr;
#endif
}

USmartObjectDefinition* UGenesisNpcAssetBuilder::BuildActivityDefinition(const FString& PackageName, FName Activity, const TArray<FVector>& SlotOffsets, const TArray<float>& SlotYaws)
{
#if WITH_EDITOR
	const FName AssetName = FName(*FPackageName::GetShortName(PackageName));
	UPackage* Package = GenesisAssetBuild::PreparePackage(PackageName, AssetName);
	USmartObjectDefinition* Definition = NewObject<USmartObjectDefinition>(Package, AssetName, RF_Public | RF_Standalone | RF_Transactional);

	const FGameplayTag Tag = UGenesisNpcSettings::ActivityTag(Activity);
	FGameplayTagContainer Tags;
	Tags.AddTag(Tag);
	Definition->SetActivityTags(Tags);

	for (int32 i = 0; i < SlotOffsets.Num(); ++i)
	{
		FSmartObjectSlotDefinition& Slot = Definition->DebugAddSlot();
		Slot.Offset = FVector3f(SlotOffsets[i]);
		Slot.Rotation = FRotator3f(0.f, SlotYaws.IsValidIndex(i) ? SlotYaws[i] : 0.f, 0.f);
		Slot.ActivityTags = Tags;
		UGenesisActivityBehaviorDefinition* Behavior = NewObject<UGenesisActivityBehaviorDefinition>(Definition);
		Behavior->Activity = Activity;
		Slot.BehaviorDefinitions.Add(Behavior);
#if WITH_EDITORONLY_DATA
		Slot.ID = FGuid::NewGuid();
		Slot.Name = FName(*FString::Printf(TEXT("%s_%d"), *Activity.ToString(), i + 1));
#endif
	}

	FSavePackageArgs SaveArgs;
	SaveArgs.TopLevelFlags = RF_Public | RF_Standalone;
	const FString FileName = FPackageName::LongPackageNameToFilename(PackageName, FPackageName::GetAssetPackageExtension());
	UPackage::SavePackage(Package, Definition, *FileName, SaveArgs);
	return Definition;
#else
	return nullptr;
#endif
}
