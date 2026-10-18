#pragma once

#include "CoreMinimal.h"
#include "GenesisSaveTypes.generated.h"

/** Lebensabschnitt des aktuellen Lebens (Phasen N01-N09). */
UENUM(BlueprintType)
enum class EGenesisLifeStage : uint8
{
	Conception,
	Embryo,
	Fetus,
	Birth,
	Infant,
	Child,
	Adolescent,
	Adult,
	Elder,
	Echo
};

/** Eine Erinnerung, gebunden an das Leben, in dem sie entstanden ist. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisMemoryRecord
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Memory")
	FName MemoryId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Memory")
	int32 LifeIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Memory")
	int32 WorldYear = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Memory")
	float EmotionalWeight = 0.f;
};

/** Beziehung zu einer Figur, adressiert ueber deren feste Asset-ID. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisRelationship
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Relationship")
	FName CharacterAssetId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Relationship")
	FName RelationKind;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Relationship")
	float Affinity = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Relationship")
	float Trust = 0.f;
};

/** Ueberdauert alle Leben: Identitaet der Seele, Echo-Erinnerungen, Enthuellungs-Guards. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisSoulState
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Soul")
	FGuid SoulId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Soul")
	int32 LivesLived = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Soul")
	TArray<FGenesisMemoryRecord> EchoMemories;

	/** Geschuetzte Enthuellungen (z. B. C19/C20) gelten erst als freigeschaltet, wenn ihr Guard hier steht. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Soul")
	TArray<FName> UnlockedRevealGuards;
};

/** Zustand der Welt, unabhaengig vom aktuellen Leben. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisWorldState
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|World")
	int32 WorldYear = 2026;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|World")
	int32 DayOfYear = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|World")
	float TimeOfDayHours = 8.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|World")
	int64 WorldSeed = 0;

	/** Kausale Weltereignisse (EventID -> Zustand). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|World")
	TMap<FName, int32> EventFlags;
};

/** Das aktuelle Leben: Koerper, Alter, Ort, Beziehungen, Besitz. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisLifeState
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	int32 LifeIndex = 0;

	/** Feste Asset-ID der koerperlichen Identitaet; das Aussehen wird ueber die ID aufgeloest, nie direkt referenziert. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	FName BodyAssetId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	EGenesisLifeStage Stage = EGenesisLifeStage::Conception;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	float AgeYears = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	FName LocationId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	FTransform PlayerTransform;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	TArray<FGenesisRelationship> Relationships;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	TArray<FGenesisMemoryRecord> Memories;

	/** ItemId -> Anzahl. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	TMap<FName, int32> Inventory;

	/** Geld in Cent, um Rundungsfehler zu vermeiden. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	int64 MoneyCents = 0;
};

/**
 * Soul, World und Life werden immer gemeinsam als ein Bundle geschrieben.
 * Dadurch kann nach einem Absturz nie eine Seele aus Stand N mit einer Welt aus Stand N-1 geladen werden.
 */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisSaveBundle
{
	GENERATED_BODY()

	static constexpr int32 CurrentSchemaVersion = 1;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Genesis|Save")
	int32 SchemaVersion = CurrentSchemaVersion;

	/** Steigt mit jedem erfolgreichen Speichern um eins. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Genesis|Save")
	int64 Sequence = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Genesis|Save")
	FDateTime SavedAtUtc;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Save")
	FGenesisSoulState Soul;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Save")
	FGenesisWorldState World;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Save")
	FGenesisLifeState Life;
};

UENUM(BlueprintType)
enum class EGenesisSaveResult : uint8
{
	Ok,
	NotFound,
	IoError,
	VerifyFailed,
	Corrupt,
	SchemaUnsupported
};
