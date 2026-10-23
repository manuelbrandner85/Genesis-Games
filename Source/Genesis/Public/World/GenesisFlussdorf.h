#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "Save/GenesisSaveTypes.h"
#include "Subsystems/WorldSubsystem.h"
#include "World/GenesisWeather.h"
#include "GenesisFlussdorf.generated.h"

struct FGenesisEventSpec;
class AGenesisNpcCharacter;

/**
 * Projekteinstellungen > Genesis Flussdorf. Rollen und Objekte aus der V24-Weltbibel;
 * alle Schwellen und Zeiten sind Gestaltungs-Startwerte, KEIN Kanon.
 */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Genesis Flussdorf"))
class GENESIS_API UGenesisFlussdorfSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	/** Level, in denen die Flussdorf-Simulation laeuft. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf")
	TArray<FString> ActiveMaps;

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf")
	FName StormId = TEXT("STORM_VS01");

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Rollen")
	FName WorkshopOwner = TEXT("N01");

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Rollen")
	FName DeliveryDriver = TEXT("N04");

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Rollen")
	FName CommunityCoordinator = TEXT("N05");

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Objekte")
	FName Bridge = TEXT("VS01_BRIDGE_01");

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Objekte")
	FName Workshop = TEXT("R03_WORKSHOP");

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Objekte")
	FName Trail = TEXT("R05_TRAIL");

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Objekte")
	FName Notice = TEXT("R01_NOTICE");

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Objekte")
	FName Station = TEXT("R06_STATION");

	/**
	 * Ungeklaert: N06 (Wetterbeobachtung) ist nicht im Slice. So lange erreicht ein Stationsalarm N05 erst nach
	 * dieser Meldezeit - schneller, wenn jemand die Werte ueberbringt.
	 */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf")
	float AlertRelayMinutes = 90.f;

	/** Wer naeher am Aushang ist, liest eine ausgehaengte Warnung. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf")
	float NoticeReadRangeCm = 800.f;

	/** So lange braucht N01 allein, um die Werkstatt zu sichern (mit Hilfe vor Ort doppelt so schnell). */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf")
	float SecureMinutes = 30.f;

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf")
	float HelpRangeCm = 500.f;

	/** Pegel (m ueber Normal), ab dem der tiefe Uferweg-Abschnitt ueberflutet und danach gesperrt ist. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Schwellen")
	float TrailFloodRiverM = 2.0f;

	/** Pegel, ab dem eine vorgeschaedigte Bruecke (Riss) weiteren Schaden nimmt. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Schwellen")
	float BridgeDamageRiverM = 2.2f;

	/** Pegel, ab dem der Belag ueberflutet ist (unpassierbar). */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Schwellen")
	float BridgeDeckFloodRiverM = 3.2f;

	/** Windspitze, ab der ein ungesichertes Werkstattlager Schaden nimmt. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Flussdorf|Schwellen")
	float WorkshopDamageWindMs = 23.f;
};

/**
 * Regeln des Flussdorfs als reine Funktionen auf dem Spielstand (testbar ohne Level).
 * Jede Zustandsaenderung ist ein Ereignis im Kausalgraphen; jede Regel ist idempotent
 * (zweimal anwenden = einmal), damit Laden und Zeitraffer nichts doppelt buchen.
 */
struct GENESIS_API FGenesisFlussdorfRules
{
	using FRecord = TFunctionRef<FName(const FGenesisEventSpec&)>;

	/** Wetter von From bis To fortschreiben: Phasenwechsel, Alarm-Weitergabe, Schaeden durch Pegel und Wind. */
	static void AdvanceWeather(FGenesisSaveBundle& Bundle, const FGenesisStormTimeline& Timeline, const FDateTime& From, const FDateTime& To,
		FRecord Record, TArray<FName>& OutTriggers);

	/** N05 entscheidet nach eigenem Wissen: oeffentliche Warnung, Pruefauftrag, Sperrung. */
	static void EvaluateCoordinator(FGenesisSaveBundle& Bundle, const FGenesisStormTimeline& Timeline, FRecord Record, TArray<FName>& OutTriggers);

	/** Was die Figur wegen der Lage statt ihres Tagesplans tut (leer = Tagesplan). Ohne Wegfindung. */
	static FName ReactionFor(const FGenesisSaveBundle& Bundle, FName NpcId, FName Scheduled, EGenesisWeatherPhase Phase);

	/** Hat die Figur ein Ereignis dieses Typs erlebt, gesehen oder gehoert? */
	static bool Knows(const FGenesisSaveBundle& Bundle, FName NpcId, FName EventType);

	static bool KnowsWarning(const FGenesisSaveBundle& Bundle, FName NpcId);

	/** Juengstes Ereignis dieses Typs (oder NAME_None). */
	static FName FindLatestEvent(const FGenesisSaveBundle& Bundle, FName EventType);

	static EGenesisWeatherPhase GetProcessedPhase(const FGenesisSaveBundle& Bundle);

	/** Bruecke kann nicht benutzt werden (gesperrt, beschaedigt oder ueberflutet). */
	static bool IsBridgeBlocked(const FGenesisSaveBundle& Bundle);
};

/** Laufende Flussdorf-Simulation im Spiel: Wetter, Station, Aushang, Reaktionen der Figuren. */
UCLASS()
class GENESIS_API UGenesisFlussdorfSubsystem : public UTickableWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;

	/** Ist die Simulation in diesem Level aktiv? */
	UFUNCTION(BlueprintPure, Category = "Genesis|Flussdorf")
	bool IsActive() const;

	UFUNCTION(BlueprintPure, Category = "Genesis|Flussdorf")
	FGenesisWeatherReading GetReading() const;

	/** Platzhalter fuer Gespraechstexte: {Pressure} {Tendency} {Wind} {Rain} {River} {StationStatus} {NoticeText} {BridgeStatus} {TrailStatus} {WorkshopStatus} {DeliveryStatus}. */
	static void AppendTextArgs(const UWorld* World, FFormatNamedArguments& Args);

	const FGenesisStormTimeline& GetTimeline() const { return Timeline; }

private:
	FGenesisSaveBundle* GetBundle() const;
	void EnsureTimeline(const FGenesisSaveBundle& Bundle);
	void UpdateNpcs(FGenesisSaveBundle& Bundle, EGenesisWeatherPhase Phase, double GameMinutes, bool bStormStarted);
	bool HasDeliveryRoute(const AGenesisNpcCharacter* Npc) const;

	FGenesisStormTimeline Timeline;
	bool bTimelineBuilt = false;
	int64 TimelineSeed = 0;
	FDateTime LastTime;
	bool bHasLastTime = false;
	double SecureCarryMinutes = 0.0;
	float RouteCheckTimer = 0.f;
	bool bLastRouteOk = true;
};
