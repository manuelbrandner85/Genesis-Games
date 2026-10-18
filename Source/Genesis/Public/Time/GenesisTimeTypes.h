#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "Save/GenesisSaveTypes.h"
#include "GenesisTimeTypes.generated.h"

UENUM(BlueprintType)
enum class EGenesisSeason : uint8
{
	Winter,
	Spring,
	Summer,
	Autumn
};

/**
 * Zeit- und Lebensphasen-Einstellungen (Projekteinstellungen > Genesis Time).
 * Biologische Grenzen folgen der Embryologie (Tage ab Befruchtung).
 * Die Altersgrenzen nach der Geburt sind Vorschlaege; das Drehbuch nennt nur Szenenalter
 * (C06 ca. 7-9, C07 ca. 11-13, C08 ca. 14-17, C09 ca. 17-22) und keine festen Phasengrenzen.
 */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Genesis Time"))
class GENESIS_API UGenesisTimeSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	/** Spielsekunden pro echter Sekunde im freien Spiel (60 = eine Spielstunde pro echter Minute). */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Time", meta = (ClampMin = "0"))
	float GameSecondsPerRealSecond = 60.f;

	/** Tage ab Befruchtung: Ende der Vor-Embryonalzeit (Zellteilung, Wanderung, Einnistung). */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Biology")
	int32 EmbryoStartDay = 14;

	/** Tage ab Befruchtung: Beginn der Fetalzeit (9. Woche nach Befruchtung). */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Biology")
	int32 FetusStartDay = 56;

	/** Tage ab Befruchtung: errechneter Geburtszeitraum (38 Wochen = 40 SSW). */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Biology")
	int32 BirthStartDay = 266;

	/** Vorschlag, nicht kanonisch. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Life")
	float ChildStartYears = 1.f;

	/** Vorschlag, nicht kanonisch. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Life")
	float AdolescentStartYears = 12.f;

	/** Vorschlag, nicht kanonisch. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Life")
	float AdultStartYears = 18.f;

	/** Vorschlag, nicht kanonisch. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Life")
	float ElderStartYears = 65.f;
};

/** Reine Berechnungen ohne Weltbezug: Alter, Lebensabschnitt, Jahreszeit. */
struct GENESIS_API FGenesisLifeCycle
{
	static constexpr double DaysPerYear = 365.2425;

	/** Alter in Jahren seit der Geburt; 0 vor der Geburt. */
	static double GetAgeYears(const FGenesisLifeState& Life, const FDateTime& Now);

	/** Tage seit der Befruchtung. */
	static double GetDaysSinceConception(const FGenesisLifeState& Life, const FDateTime& Now);

	/**
	 * Lebensabschnitt zum Zeitpunkt Now. Echo bleibt Echo.
	 * Vor der Geburt entscheidet die Zeit seit Befruchtung; "Birth" bleibt bestehen, bis CompleteBirth aufgerufen wird
	 * (die Geburt ist ein Spielereignis, kein Zeitautomatismus).
	 */
	static EGenesisLifeStage ComputeStage(const FGenesisLifeState& Life, const FDateTime& Now, const UGenesisTimeSettings& Settings);

	/** Schliesst die Geburt ab (N04): Geburtszeitpunkt = Now, Abschnitt = Infant. */
	static void CompleteBirth(FGenesisLifeState& Life, const FDateTime& Now);

	/** Auf ganze Millisekunden runden: so genau speichert der Spielstand (ISO 8601), damit Laden verlustfrei ist. */
	static FDateTime ToSavePrecision(const FDateTime& Value);

	/** Meteorologische Jahreszeit, Nordhalbkugel (Primaerwelt Mitteleuropa 2026). */
	static EGenesisSeason GetSeason(const FDateTime& Date);
};
