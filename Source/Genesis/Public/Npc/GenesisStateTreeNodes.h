#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "SmartObjectRuntime.h"
#include "StateTreeConditionBase.h"
#include "StateTreeTaskBase.h"
#include "GenesisStateTreeNodes.generated.h"

class UStateTree;
class USmartObjectDefinition;

USTRUCT()
struct GENESIS_API FGenesisScheduledActivityConditionData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Parameter")
	FName Activity;
};

/** Wahr, wenn der Tagesplan der Figur jetzt (Weltzeit) diese Aktivitaet vorsieht. */
USTRUCT(meta = (DisplayName = "Genesis: Plan sieht Aktivitaet vor"))
struct GENESIS_API FGenesisScheduledActivityCondition : public FStateTreeConditionCommonBase
{
	GENERATED_BODY()

	using FInstanceDataType = FGenesisScheduledActivityConditionData;
	virtual const UStruct* GetInstanceDataType() const override { return FInstanceDataType::StaticStruct(); }
	virtual bool TestCondition(FStateTreeExecutionContext& Context) const override;
};

USTRUCT()
struct GENESIS_API FGenesisActivityTaskData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Parameter")
	FName Activity;

	UPROPERTY()
	FSmartObjectClaimHandle Claim;

	UPROPERTY()
	FVector SlotLocation = FVector::ZeroVector;

	UPROPERTY()
	FRotator SlotRotation = FRotator::ZeroRotator;

	/** Punkt 1 m vor dem Platz: Menschen treten von vorn an einen Sitz- oder Arbeitsplatz, nicht entlang der Reihe. */
	UPROPERTY()
	FVector ApproachLocation = FVector::ZeroVector;

	UPROPERTY()
	bool bApproachReached = false;

	UPROPERTY()
	bool bOccupied = false;

	UPROPERTY()
	float RetryTimer = 0.f;

	/** Wie lange die Figur schon festhaengt (unterwegs, aber ohne Bewegung). */
	UPROPERTY()
	float StuckTimer = 0.f;

	/** Platz, an dem die Figur zuletzt festhing; wird beim naechsten Suchen gemieden. */
	UPROPERTY()
	FSmartObjectSlotHandle AvoidSlot;
};

/**
 * Sucht einen freien Platz fuer die Aktivitaet (Smart Object), reserviert ihn, geht hin und belegt ihn.
 * Endet, sobald der Tagesplan etwas anderes vorsieht; der Platz wird dann freigegeben.
 */
USTRUCT(meta = (DisplayName = "Genesis: Aktivitaet ausfuehren"))
struct GENESIS_API FGenesisActivityTask : public FStateTreeTaskCommonBase
{
	GENERATED_BODY()

	using FInstanceDataType = FGenesisActivityTaskData;
	virtual const UStruct* GetInstanceDataType() const override { return FInstanceDataType::StaticStruct(); }
	virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override;
	virtual EStateTreeRunStatus Tick(FStateTreeExecutionContext& Context, const float DeltaTime) const override;
	virtual void ExitState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override;
};

/** Editor: erzeugt die NPC-Assets reproduzierbar per Skript (Tools/Editor/build_wk_m03_002.py). */
UCLASS()
class GENESIS_API UGenesisNpcAssetBuilder : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** StateTree "Tagesablauf": je Aktivitaet ein Zustand mit Plan-Bedingung und Aktivitaets-Aufgabe; Freizeit als Rueckfall. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Editor")
	static UStateTree* BuildDailyLifeStateTree(const FString& PackageName);

	/** Smart-Object-Definition fuer eine Aktivitaet mit SlotOffsets.Num() Plaetzen (Position relativ, Blickrichtung je Platz). */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Editor")
	static USmartObjectDefinition* BuildActivityDefinition(const FString& PackageName, FName Activity, const TArray<FVector>& SlotOffsets, const TArray<float>& SlotYaws);
};
