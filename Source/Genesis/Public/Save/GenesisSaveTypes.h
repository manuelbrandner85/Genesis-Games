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

/**
 * Ein tatsaechlich geschehenes Ereignis im Kausalgraphen (Ereignis-Wahrheit).
 * Rueckblenden (z. B. C12/C16) duerfen nur zeigen, was hier mit einer EventId belegt ist.
 */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisCausalEvent
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	FName EventId;

	/** Art des Ereignisses, z. B. HELPED, PROMISE_BROKEN (Definitionen in Projekteinstellungen > Genesis Causality). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	FName EventType;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	FDateTime WorldTime;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	FName LocationId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	int32 LifeIndex = 0;

	/** Wer gehandelt hat (Figuren-ID oder Spieler-ID "PLAYER_L<Leben>"). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	FName ActorId;

	/** Wen es direkt betraf. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	TArray<FName> TargetIds;

	/** Wer es gesehen hat (ohne selbst betroffen zu sein). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	TArray<FName> WitnessIds;

	/** Ereignisse, die dieses verursacht haben. Muessen existieren und frueher liegen. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	TArray<FName> CauseEventIds;

	/** -1 (schadet den Betroffenen) .. +1 (hilft ihnen). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	float Valence = 0.f;

	/** 0 (beilaeufig) .. 1 (lebensveraendernd). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	float Magnitude = 0.f;

	/** Optionale Verknuepfung mit Mission, Szene oder Ort (z. B. "L08", "C08"). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	FName ContextTag;
};

UENUM(BlueprintType)
enum class EGenesisMemorySource : uint8
{
	/** Selbst betroffen. */
	Experienced,
	/** Mit angesehen. */
	Witnessed,
	/** Von jemandem erzaehlt bekommen. */
	Heard
};

/** Subjektive Erinnerung einer Figur an ein Ereignis. Kann vom Kausalgraphen abweichen (wahrgenommene Bewertung). */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisNpcMemory
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Memory")
	FName EventId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Memory")
	EGenesisMemorySource Source = EGenesisMemorySource::Experienced;

	/** Von wem sie es gehoert hat (nur bei Heard). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Memory")
	FName HeardFrom;

	/** Wie praesent die Erinnerung beim Entstehen war (0..1); verblasst danach mit der Zeit. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Memory")
	float InitialSalience = 0.f;

	/** Wie die Figur das Ereignis bewertet (-1..1). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Memory")
	float PerceivedValence = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Memory")
	FDateTime FormedAt;
};

/** Haltung einer Figur gegenueber einer anderen (oder dem Spieler eines bestimmten Lebens). */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisAttitude
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Relationship")
	float Trust = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Relationship")
	float Affinity = 0.f;
};

/** Dauerhafter Zustand einer Nicht-Spieler-Figur in der Welt; ueberdauert Leben des Spielers. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisNpcState
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	FName NpcId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	TArray<FGenesisNpcMemory> Memories;

	/** Haltung je Gegenueber (Figuren-ID oder "PLAYER_L<Leben>"). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	TMap<FName, FGenesisAttitude> Attitudes;
};

/** Fortschritt einer Quest im aktuellen Leben. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisQuestState
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName QuestId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName CurrentStepId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	bool bCompleted = false;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName OutcomeId;

	/** Durchlaufene Schritte und Ausloeser in Reihenfolge (Nachvollziehbarkeit, Rueckblick). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FName> History;
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

/**
 * Dauerhafter Zustand eines Weltobjekts (z. B. VS01_BRIDGE_01). Jede Aenderung erhoeht die Version und nennt
 * das verursachende Ereignis: Zustaende aendern sich nur belegt (Datenvertrag ObjectID/Version/EventID).
 */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisWorldObjectState
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	FName ObjectId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	int32 Version = 0;

	/** Zustandswerte, z. B. Passable=1, Closed=0, Damage=1. Fehlende Werte gelten als 0. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	TMap<FName, int32> Values;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	FName LastEventId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	FDateTime LastChange;
};

/** Zustand der Welt, unabhaengig vom aktuellen Leben. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisWorldState
{
	GENERATED_BODY()

	/** Massgebliche Weltzeit (Datum + Uhrzeit). Jahr, Tag, Uhrzeit und Jahreszeit werden daraus abgeleitet. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|World")
	FDateTime WorldDateTime = FDateTime(2026, 1, 1, 8, 0, 0);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|World")
	int64 WorldSeed = 0;

	/** Kausale Weltereignisse (EventID -> Zustand). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|World")
	TMap<FName, int32> EventFlags;

	/** Kausalgraph: alle tatsaechlich geschehenen Ereignisse, in zeitlicher Reihenfolge. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	TArray<FGenesisCausalEvent> CausalEvents;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	int64 NextEventSerial = 1;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	TArray<FGenesisNpcState> Npcs;

	/** Weltobjekte mit Zustand (Bruecke, Werkstatt, Wege). Fehlt ein Objekt, gelten seine Startwerte. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	TArray<FGenesisWorldObjectState> Objects;
};

/** Das aktuelle Leben: Koerper, Lebensdaten, Ort, Beziehungen, Besitz. Das Alter wird aus Weltzeit und Geburt berechnet. */
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

	/** Zeitpunkt der Befruchtung dieses Lebens (Beginn von Phase N01/N02). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	FDateTime ConceptionDateTime = FDateTime(2026, 1, 1);

	/** Erst nach abgeschlossener Geburt (N04) gesetzt. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	bool bBorn = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Life")
	FDateTime BirthDateTime = FDateTime(2026, 1, 1);

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

	/**
	 * Verdecktes Verhaltensprofil dieses Lebens (z. B. Empathy, Reliability). Wird nie als Zahl angezeigt und ist
	 * keine Strafe (Kanon: kein Karma-Gericht); Figuren reagieren darauf nur ueber ihr eigenes Erleben.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Life")
	TMap<FName, float> ConductProfile;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Life")
	TArray<FGenesisQuestState> Quests;

	/** Was der Spieler in diesem Leben selbst weiss (z. B. CrackSeen). Ein neues Leben weiss davon nichts. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Life")
	TMap<FName, int32> Knowledge;
};

/**
 * Soul, World und Life werden immer gemeinsam als ein Bundle geschrieben.
 * Dadurch kann nach einem Absturz nie eine Seele aus Stand N mit einer Welt aus Stand N-1 geladen werden.
 */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisSaveBundle
{
	GENERATED_BODY()

	/**
	 * 1: Jahr/Tag/Uhrzeit + Alter als Zahl. 2: Weltdatum + Zeugung/Geburt (Migration 1 -> 2 beim Laden).
	 * 3: Kausalgraph, NPC-Gedaechtnis, Verhaltensprofil (Schema 2 laedt mit leerem Graphen).
	 * 4: Questfortschritt (aeltere Staende laden ohne Quests).
	 * 5: Weltobjekte mit Version und Spielerwissen je Leben (aeltere Staende: Startwerte, nichts gewusst).
	 */
	static constexpr int32 CurrentSchemaVersion = 5;

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
