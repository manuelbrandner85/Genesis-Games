#pragma once

#include "CoreMinimal.h"
#include "AIController.h"
#include "Character/GenesisCharacter.h"
#include "GameFramework/Actor.h"
#include "GenesisNpc.generated.h"

class UGenesisNpcMemoryComponent;
class USmartObjectComponent;
class USmartObjectDefinition;
class UStateTreeAIComponent;
class UStaticMeshComponent;

/**
 * Nicht-Spieler-Figur. Aussehen ueber die Charakter-Registry (CharacterAssetId = NpcId),
 * Tagesablauf ueber den StateTree des KI-Controllers, Gedaechtnis ueber den Kausalgraphen.
 */
UCLASS()
class GENESIS_API AGenesisNpcCharacter : public AGenesisCharacter
{
	GENERATED_BODY()

public:
	AGenesisNpcCharacter();

	UFUNCTION(BlueprintPure, Category = "Genesis|NPC")
	FName GetNpcId() const { return CharacterAssetId; }

	/** Was der Tagesplan jetzt (Weltzeit) vorsieht. */
	UFUNCTION(BlueprintPure, Category = "Genesis|NPC")
	FName GetScheduledActivity() const;

	UGenesisNpcMemoryComponent* GetMemory() const { return Memory; }

	/** Vom StateTree gesetzt: aktuelle Aktivitaet und ob die Figur an ihrem Platz angekommen ist. */
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "Genesis|NPC")
	FName CurrentActivity;

	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "Genesis|NPC")
	bool bAtActivitySpot = false;

	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "Genesis|NPC")
	FVector ActivitySpotLocation = FVector::ZeroVector;

protected:
	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;

private:
	UPROPERTY(VisibleAnywhere, Category = "Genesis|NPC")
	TObjectPtr<UGenesisNpcMemoryComponent> Memory;
};

/** KI-Controller: fuehrt den Tagesablauf-StateTree aus. */
UCLASS()
class GENESIS_API AGenesisNpcAIController : public AAIController
{
	GENERATED_BODY()

public:
	AGenesisNpcAIController();

	UStateTreeAIComponent* GetStateTreeComponent() const { return StateTree; }

protected:
	virtual void OnPossess(APawn* InPawn) override;

private:
	UPROPERTY(VisibleAnywhere, Category = "Genesis|NPC")
	TObjectPtr<UStateTreeAIComponent> StateTree;
};

/** Ein Ort fuer eine Taetigkeit (Bett, Werkbank, Marktstand, Bank) als Smart Object. */
UCLASS()
class GENESIS_API AGenesisActivitySpot : public AActor
{
	GENERATED_BODY()

public:
	AGenesisActivitySpot();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	TObjectPtr<USmartObjectDefinition> Definition;

	/** Definition an das Smart Object uebergeben (auch fuer Editor-Skripte). */
	UFUNCTION(BlueprintCallable, Category = "Genesis|NPC")
	void ApplyDefinition();

protected:
	virtual void OnConstruction(const FTransform& Transform) override;

private:
	UPROPERTY(VisibleAnywhere, Category = "Genesis|NPC")
	TObjectPtr<UStaticMeshComponent> Visual;

	UPROPERTY(VisibleAnywhere, Category = "Genesis|NPC")
	TObjectPtr<USmartObjectComponent> SmartObject;
};

/** Sicht-Wahrnehmung: wer sieht einen Ort gerade? (Reichweite nach Licht, Blickwinkel, Sichtlinie). */
struct GENESIS_API FGenesisPerception
{
	/** Sichtweite bei der aktuellen Belichtung der Szene (EV100 des Himmels-Controllers). */
	static float GetSightRange(const UWorld* World);

	/** Alle NPCs, die Location sehen koennen. IgnoreActor (z. B. der Handelnde) blockiert die Sicht nicht. */
	static TArray<FName> FindWitnesses(const UWorld* World, const FVector& Location, const AActor* IgnoreActor, const TArray<FName>& ExcludeIds);
};
