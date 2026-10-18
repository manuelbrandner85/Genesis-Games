#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Causality/GenesisCausality.h"
#include "GenesisNpcMemoryComponent.generated.h"

/**
 * Gibt einer Figur im Level Zugriff auf ihr Gedaechtnis und ihre Haltungen im Kausalgraphen.
 * Verhalten und Dialoge fragen hier nach; Zahlen werden nie im HUD angezeigt.
 */
UCLASS(ClassGroup = (Genesis), meta = (BlueprintSpawnableComponent))
class GENESIS_API UGenesisNpcMemoryComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	/** Feste Figuren-ID (dieselbe wie in der Charakter-Registry). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	FName NpcId;

	/** Haltung gegenueber dem Spieler des aktuellen Lebens. In einem neuen Leben ist der Spieler ein Fremder. */
	UFUNCTION(BlueprintPure, Category = "Genesis|NPC")
	EGenesisDisposition GetDispositionTowardPlayer() const;

	UFUNCTION(BlueprintPure, Category = "Genesis|NPC")
	FGenesisAttitude GetAttitudeToward(FName SubjectId) const;

	/** Die am staerksten praesenten Erinnerungen (fuer Dialogauswahl), staerkste zuerst. */
	UFUNCTION(BlueprintPure, Category = "Genesis|NPC")
	TArray<FGenesisNpcMemory> GetSalientMemories(int32 MaxCount = 3, float MinSalience = 0.1f) const;

	UFUNCTION(BlueprintPure, Category = "Genesis|NPC")
	bool Remembers(FName EventId) const;

private:
	const FGenesisSaveBundle* GetBundle() const;
};
