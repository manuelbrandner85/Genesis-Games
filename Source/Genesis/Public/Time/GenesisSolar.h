#pragma once

#include "CoreMinimal.h"

/** Sonnenstand in Grad: Hoehe ueber dem Horizont und Azimut ab Norden im Uhrzeigersinn. */
struct FGenesisSunPosition
{
	double ElevationDeg = 0.0;
	double AzimuthDeg = 0.0;
};

/** Mondstand, Phase und Beleuchtungsstaerke. */
struct FGenesisMoonState
{
	double ElevationDeg = 0.0;
	double AzimuthDeg = 0.0;
	/** Phasenwinkel Sonne-Mond-Erde in Grad (0 = Vollmond, 180 = Neumond). */
	double PhaseAngleDeg = 180.0;
	/** Beleuchteter Anteil der Mondscheibe 0..1. */
	double IlluminatedFraction = 0.0;
	/** Beleuchtungsstaerke senkrecht zum Mond ausserhalb der Atmosphaere, Lux (Vollmond ca. 0,27 lx). */
	double IlluminanceLux = 0.0;
};

/** Achsen des Himmelsaequatorsystems in Weltkoordinaten (X = Nord, Y = Ost, Z = oben). */
struct FGenesisCelestialBasis
{
	/** Richtung RA = 0 h, Dec = 0. */
	FVector AxisRA0;
	/** Richtung RA = 18 h, Dec = 0 (so gewaehlt, dass die Basis eine echte Drehung ist). */
	FVector AxisRA18;
	/** Himmelsnordpol. */
	FVector AxisPole;
};

/**
 * Astronomische Sonnenstandsberechnung (Naeherung nach dem Astronomical Almanac, Genauigkeit ca. 0,01 Grad
 * zwischen 1950 und 2050) und zur Lichtsituation passende Kamerabelichtung.
 */
struct GENESIS_API FGenesisSolar
{
	/** Ortszeit -> UTC. Mit bEuSummerTime gilt die EU-Regel (letzter Sonntag Maerz 01:00 UTC bis letzter Sonntag Oktober 01:00 UTC). */
	static FDateTime LocalToUtc(const FDateTime& Local, double StandardUtcOffsetHours, bool bEuSummerTime);

	static bool IsEuSummerTime(const FDateTime& Utc);

	static FGenesisSunPosition Compute(const FDateTime& Utc, double LatitudeDeg, double LongitudeDeg);

	/**
	 * Belichtung (EV100) fuer eine Kamera unter freiem Himmel bei klarem Wetter, abhaengig vom Sonnenstand.
	 * Stuetzwerte aus der fotografischen Belichtungstabelle (Sunny-16 = EV 15, kurz nach Sonnenuntergang 9-11,
	 * buergerliche Daemmerung ca. 5, Nacht ohne Mond -7), linear interpoliert. Unter -6 Grad
	 * so gewaehlt, dass der Zenithimmel der Daemmerung 1,5 Blenden unter Mittelgrau liegt (wie in Nachtfotos).
	 */
	static double GetClearSkyEV100(double SunElevationDeg);

	/**
	 * Zusaetzliche Zenit-Leuchtdichte der tiefen Daemmerung in cd/m2 (ueber dem Nachthimmel aus Sternen und Airglow).
	 * Messwerte V-Band nach Patat et al. 2006 (Paranal) und Rozenberg 1966: 6 Grad ca. 1,1 cd/m2, 9 Grad 0,043, 12 Grad 0,0017,
	 * 15 Grad 0,00043, 18 Grad Nachthimmel. Unreals Atmosphaere zeichnet die Daemmerung nur bis ca. 8 Grad unter dem Horizont;
	 * deshalb wird der Anteil zwischen 5 und 9 Grad eingeblendet, damit nichts doppelt zaehlt.
	 */
	static double GetTwilightZenithLuminance(double SunElevationDeg);

	/** Ortssternzeit in Grad. */
	static double GetLocalSiderealTimeDeg(const FDateTime& Utc, double LongitudeDeg);

	/**
	 * Mond nach den Hauptgliedern der Mondtheorie (Genauigkeit ca. 0,5 Grad, inkl. Parallaxe).
	 * Helligkeit nach Allen/Krisciunas-Schaefer: 10^(-0,4 (0,026 a + 4e-9 a^4)), a = Phasenwinkel.
	 */
	static FGenesisMoonState ComputeMoon(const FDateTime& Utc, double LatitudeDeg, double LongitudeDeg);

	/** Lage des Sternenhimmels am Ort zur Zeit (fuer die Sternkarte). */
	static FGenesisCelestialBasis GetCelestialBasis(const FDateTime& Utc, double LatitudeDeg, double LongitudeDeg);

	/** Richtung eines Himmelsobjekts in Weltkoordinaten. */
	static FVector EquatorialToWorld(double RightAscensionDeg, double DeclinationDeg, const FGenesisCelestialBasis& Basis);

	/**
	 * Belichtung fuer Mondlicht allein: Vollmond hoch am Himmel = EV -2,5 (Belichtungstabelle "Landschaft bei Vollmond" -3..-2),
	 * je halbierte Beleuchtungsstaerke eine Stufe weniger.
	 */
	static double GetMoonEV100(const FGenesisMoonState& Moon);

	/** Gesamtbelichtung aus Sonne/Daemmerung und Mond (Lichtmengen addiert). */
	static double CombineEV100(double SunEV100, double MoonEV100);
};
