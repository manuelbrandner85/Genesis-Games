#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "Save/GenesisSaveTypes.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "GenesisCausality.generated.h"

/** Wie ein Ereignistyp auf Betroffene wirkt. Werte sind Gestaltungsdaten, keine Spielerbewertung. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisEventTypeDef
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	FName EventType;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	float DefaultValence = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	float DefaultMagnitude = 0.3f;

	/** Aenderung des Vertrauens der Betroffenen gegenueber dem Handelnden (direkt betroffen = voller Wert). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	float TrustDelta = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	float AffinityDelta = 0.f;

	/** Aenderung des verdeckten Verhaltensprofils, wenn der Spieler handelt. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Causality")
	TMap<FName, float> ConductDeltas;
};

/** Projekteinstellungen > Genesis Causality. */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Genesis Causality"))
class GENESIS_API UGenesisCausalitySettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Causality")
	TArray<FGenesisEventTypeDef> EventTypes;

	/** Zeugen erleben ein Ereignis schwaecher als Betroffene. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Causality")
	float WitnessFactor = 0.5f;

	/** Gehoertes wirkt schwaecher als Gesehenes und haengt vom Vertrauen in den Erzaehler ab. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Causality")
	float HeardFactor = 0.25f;

	/** Halbwertszeit einer beilaeufigen Erinnerung; wichtige Erinnerungen halten bis zu (1 + Scale) mal laenger. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Memory")
	float BaseHalfLifeDays = 60.f;

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Memory")
	float MagnitudeHalfLifeScale = 20.f;

	/** Darunter gilt eine Erinnerung als vergessen. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Memory")
	float ForgetThreshold = 0.05f;

	/** Ab dieser Bedeutung wird ein Ereignis nie ganz vergessen. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Memory")
	float PermanentMagnitude = 0.8f;

	const FGenesisEventTypeDef* FindType(FName EventType) const;
};

/** Beschreibung eines neuen Ereignisses. Zeit, Ort und Leben ergaenzt der Kausalgraph aus dem Spielstand. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisEventSpec
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Causality")
	FName EventType;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Causality")
	FName ActorId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Causality")
	TArray<FName> TargetIds;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Causality")
	TArray<FName> WitnessIds;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Causality")
	TArray<FName> CauseEventIds;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Causality")
	FName LocationId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Causality")
	FName ContextTag;

	/** < 0: Standardwert des Typs verwenden. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Causality")
	float MagnitudeOverride = -1.f;
};

/** Grobe Haltung fuer Verhalten und Dialogwahl (nie als Zahl im HUD). */
UENUM(BlueprintType)
enum class EGenesisDisposition : uint8
{
	Hostile,
	Wary,
	Neutral,
	Warm,
	Close
};

/** Kausalgraph und Figurengedaechtnis als reine Funktionen auf dem Spielstand. */
struct GENESIS_API FGenesisCausality
{
	/** Spieler-Identitaet eines bestimmten Lebens. Neue Leben sind fuer Figuren neue Menschen. */
	static FName PlayerSubjectId(int32 LifeIndex);

	/** Traegt ein Ereignis ein, bildet Erinnerungen und aendert Haltungen. Liefert die EventId oder NAME_None mit Fehler. */
	static FName RecordEvent(FGenesisSaveBundle& Bundle, const FGenesisEventSpec& Spec, const UGenesisCausalitySettings& Settings, FString* OutError = nullptr);

	/** Figur From erzaehlt Figur To von einem Ereignis (Geruecht). Liefert false, wenn From es nicht weiss oder To es schon kennt. */
	static bool ShareMemory(FGenesisSaveBundle& Bundle, FName FromNpc, FName ToNpc, FName EventId, const UGenesisCausalitySettings& Settings);

	static const FGenesisCausalEvent* FindEvent(const FGenesisSaveBundle& Bundle, FName EventId);
	static const FGenesisNpcState* FindNpc(const FGenesisSaveBundle& Bundle, FName NpcId);

	static float GetCurrentSalience(const FGenesisNpcMemory& Memory, const FGenesisCausalEvent& Event, const FDateTime& Now, const UGenesisCausalitySettings& Settings);

	/** Erinnerungen einer Figur, staerkste zuerst, nur ueber MinSalience. */
	static TArray<FGenesisNpcMemory> GetMemories(const FGenesisSaveBundle& Bundle, FName NpcId, const FDateTime& Now, const UGenesisCausalitySettings& Settings, float MinSalience = 0.f);

	static FGenesisAttitude GetAttitude(const FGenesisSaveBundle& Bundle, FName NpcId, FName SubjectId);

	static EGenesisDisposition ToDisposition(const FGenesisAttitude& Attitude);

	/** Alle Ursachen eines Ereignisses (Vorfahren im Graphen), naechste zuerst. */
	static TArray<FName> GetCauseChain(const FGenesisSaveBundle& Bundle, FName EventId);

	/** Entfernt vergessene, unwichtige Erinnerungen. Liefert die Anzahl. */
	static int32 PruneForgotten(FGenesisSaveBundle& Bundle, const FDateTime& Now, const UGenesisCausalitySettings& Settings);

	/** Widerspruchspruefung: eindeutige IDs, Ursachen existieren und liegen frueher, keine Zyklen, Erinnerungen belegt. */
	static TArray<FString> ValidateGraph(const FGenesisSaveBundle& Bundle);
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FGenesisEventRecorded, FName, EventId);

/** Zugang zum Kausalgraphen im laufenden Spiel (arbeitet auf dem aktuellen Spielstand). */
UCLASS()
class GENESIS_API UGenesisCausalitySubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Genesis|Causality")
	FName RecordEvent(const FGenesisEventSpec& Spec);

	UFUNCTION(BlueprintCallable, Category = "Genesis|Causality")
	bool ShareMemory(FName FromNpc, FName ToNpc, FName EventId);

	UFUNCTION(BlueprintPure, Category = "Genesis|Causality")
	FName GetCurrentPlayerId() const;

	UFUNCTION(BlueprintPure, Category = "Genesis|Causality")
	FGenesisAttitude GetAttitude(FName NpcId, FName SubjectId) const;

	UFUNCTION(BlueprintPure, Category = "Genesis|Causality")
	TArray<FName> GetCauseChain(FName EventId) const;

	UPROPERTY(BlueprintAssignable, Category = "Genesis|Causality")
	FGenesisEventRecorded OnEventRecorded;

private:
	FGenesisSaveBundle* GetBundle() const;
};
