#pragma once

#include "CoreMinimal.h"

/** Sonnenstand in Grad: Hoehe ueber dem Horizont und Azimut ab Norden im Uhrzeigersinn. */
struct FGenesisSunPosition
{
	double ElevationDeg = 0.0;
	double AzimuthDeg = 0.0;
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
	 * buergerliche Daemmerung ca. 7, Nacht ohne Mond um -2), linear interpoliert.
	 */
	static double GetClearSkyEV100(double SunElevationDeg);
};
