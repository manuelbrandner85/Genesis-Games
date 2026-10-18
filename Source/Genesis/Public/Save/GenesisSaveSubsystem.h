#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Save/GenesisSaveTypes.h"
#include "GenesisSaveSubsystem.generated.h"

/** Haelt den laufenden Soul/World/Life-Stand und speichert ihn transaktional. */
UCLASS()
class GENESIS_API UGenesisSaveSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	/**
	 * Beginnt eine neue Seele: neue SoulId, erstes Leben ab der Befruchtung zum Zeitpunkt WorldDateTime.
	 * Kanon: Die erste Befruchtung liegt strikt nach dem Tod in C00 (2026); das Datum setzt der Prolog.
	 */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Save")
	void StartNewSoul(FName BodyAssetId, FDateTime WorldDateTime);

	/** Nur fuer Testlevel: ein bereits geborenes Leben im angegebenen Alter. Kein Kanon. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Save")
	void StartTestLife(FName BodyAssetId, FDateTime WorldDateTime, float AgeYears);

	UFUNCTION(BlueprintPure, Category = "Genesis|Save")
	bool HasActiveSoul() const { return Current.Soul.SoulId.IsValid(); }

	/** Uebernimmt Figurposition und Ort aus der laufenden Welt und speichert. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Save")
	EGenesisSaveResult SaveToSlot(const FString& Slot);

	/** Laedt und setzt die Figur in der laufenden Welt an die gespeicherte Position. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Save")
	EGenesisSaveResult LoadFromSlot(const FString& Slot);

	UFUNCTION(BlueprintPure, Category = "Genesis|Save")
	const FGenesisSaveBundle& GetCurrent() const { return Current; }

	FGenesisSaveBundle& GetMutable() { return Current; }

	/** Spielstand-Ordner ueberschreiben (Tests). Leer = Standardordner. */
	void SetDirectoryOverride(const FString& InDirectory) { DirectoryOverride = InDirectory; }

private:
	void CaptureFromWorld();
	void ApplyToWorld() const;
	FString GetDirectory() const;

	UPROPERTY()
	FGenesisSaveBundle Current;

	FString DirectoryOverride;
};
