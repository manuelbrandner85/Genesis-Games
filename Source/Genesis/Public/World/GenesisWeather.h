#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "GenesisWeather.generated.h"

/** Wetterlage im Ablauf eines Unwetters (EV24_04 / EV24_07 / EV24_08). */
UENUM(BlueprintType)
enum class EGenesisWeatherPhase : uint8
{
	/** Kein Unwetter in Sicht. */
	Calm,
	/** Vorzeichen: Luftdruck faellt, Wind frischt auf. */
	Precursor,
	/** Messwerte ueberschreiten die Warnschwelle: Warnung ist begruendet. */
	Alert,
	/** Sturm: Wind ueber Sturmschwelle. */
	Storm,
	/** Hoehepunkt vorbei, Wind unter Sturmschwelle. */
	Receding,
	/** Wind wieder unter Warnschwelle. */
	Over,
	/** Genug Zeit vergangen, die Folgen sind Alltag geworden. */
	Settled
};

/**
 * Ein moegliches Unwetter. Alle Zahlen sind Gestaltungs-Startwerte, KEIN Kanon und keine meteorologische Beratung.
 * Der Verlauf ist deterministisch: gleicher WorldSeed + gleiche Weltzeit = gleiche Messwerte.
 */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisStormScenario
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	FName StormId;

	/** Ortszeit, zu der der Luftdruck zu fallen beginnt (Beginn der Vorzeichen). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	FDateTime PrecursorStart = FDateTime(2026, 6, 15, 14, 0, 0);

	/** Druck faellt ueber diese Zeit auf sein Minimum. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float PressureFallHours = 5.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float PressureDropHPa = 18.f;

	/** Wind und Regen setzen so viel spaeter ein als der Druckfall. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float WindLagHours = 2.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float WindRampHours = 5.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float PeakHours = 2.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float DecayHours = 4.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float BaseWindMs = 3.f;

	/** Spitzenboeen, m/s (vor Seed-Streuung). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float PeakWindMs = 26.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float PeakRainMmH = 30.f;

	/** Anstieg des Flusspegels ueber Normal, m (vor Seed-Streuung). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float RiverRiseM = 2.5f;

	/** Pegel folgt dem Regen verzoegert und faellt langsamer. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float RiverLagHours = 1.5f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float RiverDecayHours = 18.f;

	/** Seed-Streuung: Spitzenwind +/- Anteil, Pegelanstieg +/- Anteil, Zeit +/- Minuten. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float WindJitter = 0.12f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float RiverJitter = 0.2f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Weather")
	float TimeJitterMinutes = 30.f;
};

/** Messwerte der Station (R06) zu einem Zeitpunkt. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisWeatherReading
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Weather")
	float PressureHPa = 1013.f;

	/** Druckaenderung der letzten drei Stunden (negativ = fallend). */
	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Weather")
	float PressureTendency3h = 0.f;

	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Weather")
	float WindMs = 0.f;

	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Weather")
	float RainMmH = 0.f;

	/** Pegel ueber Normal, m. */
	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Weather")
	float RiverM = 0.f;

	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Weather")
	EGenesisWeatherPhase Phase = EGenesisWeatherPhase::Calm;
};

/** Konkreter Verlauf eines Szenarios fuer einen WorldSeed (Streuung angewendet, Phasenzeiten berechnet). */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisStormTimeline
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Weather")
	FName StormId;

	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Weather")
	float PeakWindMs = 0.f;

	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Weather")
	float RiverRiseM = 0.f;

	/** Beginn je Phase (Index = EGenesisWeatherPhase). Calm = Minimum. */
	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Weather")
	TArray<FDateTime> PhaseStart;

	FGenesisStormScenario Scenario;
	FDateTime Start;

	EGenesisWeatherPhase GetPhase(const FDateTime& Time) const;
};

/** Projekteinstellungen > Genesis Weather. Gestaltungs-Startwerte, KEIN Kanon. */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Genesis Weather"))
class GENESIS_API UGenesisWeatherSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Weather")
	TArray<FGenesisStormScenario> Storms;

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Weather")
	float NormalPressureHPa = 1013.f;

	/** Warnschwelle der Station: so viel Druckfall in drei Stunden begruendet eine Warnung. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Weather")
	float AlertPressureFall3hHPa = 6.f;

	/** Sturm ab dieser Windgeschwindigkeit (Beaufort 9 ab 20,8 m/s). */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Weather")
	float StormWindMs = 20.8f;

	/** Nach dem Sturm gilt die Lage unter dieser Windgeschwindigkeit als vorbei. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Weather")
	float OverWindMs = 10.f;

	/** So lange nach "vorbei" werden die Folgen zum Alltag (Ende des Missionsangebots). */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Weather")
	float SettledAfterHours = 10.f;
};

/** Wettermodell als reine Funktionen. */
struct GENESIS_API FGenesisWeather
{
	/** Verlauf fuer diesen Seed: Streuung anwenden und die Phasenzeiten minutengenau bestimmen. */
	static FGenesisStormTimeline BuildTimeline(const FGenesisStormScenario& Scenario, int64 WorldSeed, const UGenesisWeatherSettings& Settings);

	/** Messwerte ohne Phase (fuer die Phasenbestimmung selbst). */
	static FGenesisWeatherReading SampleRaw(const FGenesisStormTimeline& Timeline, const FDateTime& Time, const UGenesisWeatherSettings& Settings);

	static FGenesisWeatherReading Sample(const FGenesisStormTimeline& Timeline, const FDateTime& Time, const UGenesisWeatherSettings& Settings);

	/** Hoechster Pegel bzw. Wind im Zeitraum (fuer Zeitraffer: Schwellen werden nicht uebersprungen). */
	static float MaxRiverBetween(const FGenesisStormTimeline& Timeline, const FDateTime& From, const FDateTime& To, const UGenesisWeatherSettings& Settings);
	static float MaxWindBetween(const FGenesisStormTimeline& Timeline, const FDateTime& From, const FDateTime& To, const UGenesisWeatherSettings& Settings);

	static FName PhaseName(EGenesisWeatherPhase Phase);
};
