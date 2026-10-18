#include "Time/GenesisSolar.h"

namespace
{
	double Wrap360(double Degrees)
	{
		const double Wrapped = FMath::Fmod(Degrees, 360.0);
		return Wrapped < 0.0 ? Wrapped + 360.0 : Wrapped;
	}

	/** Letzter Sonntag eines Monats, 01:00 UTC. */
	FDateTime LastSundayOneUtc(int32 Year, int32 Month)
	{
		const int32 LastDay = FDateTime::DaysInMonth(Year, Month);
		FDateTime Day(Year, Month, LastDay, 1, 0, 0);
		while (Day.GetDayOfWeek() != EDayOfWeek::Sunday)
		{
			Day -= FTimespan::FromDays(1.0);
		}
		return Day;
	}
}

bool FGenesisSolar::IsEuSummerTime(const FDateTime& Utc)
{
	const int32 Year = Utc.GetYear();
	return Utc >= LastSundayOneUtc(Year, 3) && Utc < LastSundayOneUtc(Year, 10);
}

FDateTime FGenesisSolar::LocalToUtc(const FDateTime& Local, double StandardUtcOffsetHours, bool bEuSummerTime)
{
	const FDateTime StandardUtc = Local - FTimespan::FromHours(StandardUtcOffsetHours);
	if (bEuSummerTime && IsEuSummerTime(StandardUtc - FTimespan::FromHours(1.0)))
	{
		return StandardUtc - FTimespan::FromHours(1.0);
	}
	return StandardUtc;
}

FGenesisSunPosition FGenesisSolar::Compute(const FDateTime& Utc, double LatitudeDeg, double LongitudeDeg)
{
	// Tage seit J2000.0 (2000-01-01 12:00 UTC).
	const double N = Utc.GetJulianDay() - 2451545.0;

	const double MeanLongitude = Wrap360(280.460 + 0.9856474 * N);
	const double MeanAnomaly = FMath::DegreesToRadians(Wrap360(357.528 + 0.9856003 * N));
	const double EclipticLongitude = FMath::DegreesToRadians(MeanLongitude + 1.915 * FMath::Sin(MeanAnomaly) + 0.020 * FMath::Sin(2.0 * MeanAnomaly));
	const double Obliquity = FMath::DegreesToRadians(23.439 - 0.0000004 * N);

	const double RightAscension = FMath::Atan2(FMath::Cos(Obliquity) * FMath::Sin(EclipticLongitude), FMath::Cos(EclipticLongitude));
	const double Declination = FMath::Asin(FMath::Sin(Obliquity) * FMath::Sin(EclipticLongitude));

	// Sternzeit Greenwich in Grad, daraus Stundenwinkel am Ort.
	const double Gmst = Wrap360(280.46061837 + 360.98564736629 * N);
	const double HourAngle = FMath::DegreesToRadians(Wrap360(Gmst + LongitudeDeg) - FMath::RadiansToDegrees(RightAscension));
	const double Latitude = FMath::DegreesToRadians(LatitudeDeg);

	const double SinElevation = FMath::Sin(Latitude) * FMath::Sin(Declination) + FMath::Cos(Latitude) * FMath::Cos(Declination) * FMath::Cos(HourAngle);
	const double Elevation = FMath::Asin(FMath::Clamp(SinElevation, -1.0, 1.0));
	const double Azimuth = FMath::Atan2(-FMath::Sin(HourAngle),
		FMath::Tan(Declination) * FMath::Cos(Latitude) - FMath::Sin(Latitude) * FMath::Cos(HourAngle));

	FGenesisSunPosition Result;
	Result.ElevationDeg = FMath::RadiansToDegrees(Elevation);
	Result.AzimuthDeg = Wrap360(FMath::RadiansToDegrees(Azimuth));
	return Result;
}

double FGenesisSolar::GetClearSkyEV100(double SunElevationDeg)
{
	struct FPoint { double Elevation; double EV; };
	static const FPoint Table[] = {
		// Unter -6 Grad aus der Himmelshelligkeit abgeleitet (GetTwilightZenithLuminance): der Zenit liegt in der
		// Daemmerung ca. 1,5 Blenden, in der Nacht ca. 3 Blenden unter Mittelgrau - wie in der Nachtfotografie, damit
		// es sichtbar dunkler wird. Abgeglichen an Messungen der Bildhelligkeit (docs/evidence/WK-M02-006).
		{ -18.0, -7.0 },  // astronomische Nacht ohne Mond (Milchstrasse: EV -7..-6)
		{ -15.0, -6.0 },
		{ -12.0, -3.0 },  // Ende nautische Daemmerung
		{ -9.0, 2.5 },
		{ -6.0, 5.0 },    // Ende buergerliche Daemmerung
		{ -3.0, 9.5 },    // kurz nach Sonnenuntergang
		{ 0.0, 11.5 },    // Sonne am Horizont
		{ 2.0, 12.5 },
		{ 6.0, 13.5 },    // goldene Stunde
		{ 15.0, 14.5 },
		{ 30.0, 15.0 },   // Sunny-16
	};
	constexpr int32 Num = UE_ARRAY_COUNT(Table);

	if (SunElevationDeg <= Table[0].Elevation)
	{
		return Table[0].EV;
	}
	for (int32 i = 1; i < Num; ++i)
	{
		if (SunElevationDeg <= Table[i].Elevation)
		{
			const double Alpha = (SunElevationDeg - Table[i - 1].Elevation) / (Table[i].Elevation - Table[i - 1].Elevation);
			return FMath::Lerp(Table[i - 1].EV, Table[i].EV, Alpha);
		}
	}
	return Table[Num - 1].EV;
}

namespace
{
	/** Ekliptikale Laenge der Sonne in Grad (fuer die Mondphase). */
	double SunEclipticLongitudeDeg(double N)
	{
		const double MeanLongitude = Wrap360(280.460 + 0.9856474 * N);
		const double MeanAnomaly = FMath::DegreesToRadians(Wrap360(357.528 + 0.9856003 * N));
		return Wrap360(MeanLongitude + 1.915 * FMath::Sin(MeanAnomaly) + 0.020 * FMath::Sin(2.0 * MeanAnomaly));
	}

	void HorizontalFromEquatorial(double RaRad, double DecRad, double LstDeg, double LatitudeDeg, double& OutElevationDeg, double& OutAzimuthDeg)
	{
		const double HourAngle = FMath::DegreesToRadians(LstDeg) - RaRad;
		const double Lat = FMath::DegreesToRadians(LatitudeDeg);
		const double SinEl = FMath::Sin(Lat) * FMath::Sin(DecRad) + FMath::Cos(Lat) * FMath::Cos(DecRad) * FMath::Cos(HourAngle);
		OutElevationDeg = FMath::RadiansToDegrees(FMath::Asin(FMath::Clamp(SinEl, -1.0, 1.0)));
		OutAzimuthDeg = Wrap360(FMath::RadiansToDegrees(FMath::Atan2(-FMath::Sin(HourAngle),
			FMath::Tan(DecRad) * FMath::Cos(Lat) - FMath::Sin(Lat) * FMath::Cos(HourAngle))));
	}

	double Sind(double Deg) { return FMath::Sin(FMath::DegreesToRadians(Deg)); }
	double Cosd(double Deg) { return FMath::Cos(FMath::DegreesToRadians(Deg)); }
}

double FGenesisSolar::GetLocalSiderealTimeDeg(const FDateTime& Utc, double LongitudeDeg)
{
	const double N = Utc.GetJulianDay() - 2451545.0;
	return Wrap360(280.46061837 + 360.98564736629 * N + LongitudeDeg);
}

FGenesisMoonState FGenesisSolar::ComputeMoon(const FDateTime& Utc, double LatitudeDeg, double LongitudeDeg)
{
	const double N = Utc.GetJulianDay() - 2451545.0;
	const double Lp = Wrap360(218.3164477 + 13.17639648 * N);
	const double D = Wrap360(297.8501921 + 12.19074912 * N);
	const double M = Wrap360(357.5291092 + 0.98560028 * N);
	const double Mp = Wrap360(134.9633964 + 13.06499295 * N);
	const double F = Wrap360(93.2720950 + 13.22935024 * N);

	const double Lambda = Lp + 6.289 * Sind(Mp) + 1.274 * Sind(2.0 * D - Mp) + 0.658 * Sind(2.0 * D)
		+ 0.214 * Sind(2.0 * Mp) - 0.186 * Sind(M) - 0.114 * Sind(2.0 * F);
	const double Beta = 5.128 * Sind(F) + 0.281 * Sind(Mp + F) + 0.278 * Sind(Mp - F) + 0.173 * Sind(2.0 * D - F);
	const double DistanceKm = 385001.0 - 20905.0 * Cosd(Mp) - 3699.0 * Cosd(2.0 * D - Mp) - 2956.0 * Cosd(2.0 * D);
	const double Eps = 23.439 - 0.0000004 * N;

	const double X = Cosd(Beta) * Cosd(Lambda);
	const double Y = Cosd(Eps) * Cosd(Beta) * Sind(Lambda) - Sind(Eps) * Sind(Beta);
	const double Z = Sind(Eps) * Cosd(Beta) * Sind(Lambda) + Cosd(Eps) * Sind(Beta);
	const double Ra = FMath::Atan2(Y, X);
	const double Dec = FMath::Asin(FMath::Clamp(Z, -1.0, 1.0));

	FGenesisMoonState Moon;
	HorizontalFromEquatorial(Ra, Dec, GetLocalSiderealTimeDeg(Utc, LongitudeDeg), LatitudeDeg, Moon.ElevationDeg, Moon.AzimuthDeg);
	// Horizontparallaxe: der Mond steht vom Erdboden aus gesehen bis ca. 1 Grad tiefer.
	const double Parallax = FMath::RadiansToDegrees(FMath::Asin(6378.14 / DistanceKm));
	Moon.ElevationDeg -= Parallax * Cosd(Moon.ElevationDeg);

	const double Elongation = FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(Cosd(Beta) * Cosd(Lambda - SunEclipticLongitudeDeg(N)), -1.0, 1.0)));
	Moon.PhaseAngleDeg = 180.0 - Elongation;
	Moon.IlluminatedFraction = (1.0 + Cosd(Moon.PhaseAngleDeg)) * 0.5;
	const double A = Moon.PhaseAngleDeg;
	Moon.IlluminanceLux = 0.267 * FMath::Pow(10.0, -0.4 * (0.026 * A + 4e-9 * A * A * A * A)) * FMath::Square(384400.0 / DistanceKm);
	return Moon;
}

FGenesisCelestialBasis FGenesisSolar::GetCelestialBasis(const FDateTime& Utc, double LatitudeDeg, double LongitudeDeg)
{
	const double Lst = GetLocalSiderealTimeDeg(Utc, LongitudeDeg);
	const double Lat = LatitudeDeg;
	// Welt: X = Nord, Y = Ost, Z = oben. Q0 = Aequator im Meridian (Sued, gehoben), W = Westpunkt.
	const FVector Pole(Cosd(Lat), 0.0, Sind(Lat));
	const FVector Q0(-Sind(Lat), 0.0, Cosd(Lat));
	const FVector West(0.0, -1.0, 0.0);
	// Stundenwinkel H = LST - RA; ein Stern bei (RA, Dec) liegt bei cos(Dec)(cos H Q0 + sin H W) + sin(Dec) Pol.
	FGenesisCelestialBasis Basis;
	Basis.AxisRA0 = Cosd(Lst) * Q0 + Sind(Lst) * West;
	const FVector AxisRA6 = Sind(Lst) * Q0 - Cosd(Lst) * West;
	Basis.AxisRA18 = -AxisRA6;
	Basis.AxisPole = Pole;
	return Basis;
}

FVector FGenesisSolar::EquatorialToWorld(double RightAscensionDeg, double DeclinationDeg, const FGenesisCelestialBasis& Basis)
{
	return Cosd(DeclinationDeg) * Cosd(RightAscensionDeg) * Basis.AxisRA0
		- Cosd(DeclinationDeg) * Sind(RightAscensionDeg) * Basis.AxisRA18
		+ Sind(DeclinationDeg) * Basis.AxisPole;
}

double FGenesisSolar::GetMoonEV100(const FGenesisMoonState& Moon)
{
	if (Moon.ElevationDeg <= 0.0 || Moon.IlluminanceLux <= 0.0)
	{
		return -100.0;
	}
	// Horizontale Beleuchtungsstaerke mit Extinktion 0,2 mag pro Luftmasse.
	const double SinAlt = Sind(Moon.ElevationDeg);
	const double Airmass = 1.0 / FMath::Max(SinAlt, 0.03);
	const double Horizontal = Moon.IlluminanceLux * SinAlt * FMath::Pow(10.0, -0.4 * 0.2 * Airmass);
	// Bezug: Vollmond (0,267 lx) in 50 Grad Hoehe -> ca. 0,166 lx horizontal = EV -2,5.
	constexpr double ReferenceLux = 0.166;
	return -2.5 + FMath::Log2(Horizontal / ReferenceLux);
}

double FGenesisSolar::CombineEV100(double SunEV100, double MoonEV100)
{
	return FMath::Log2(FMath::Pow(2.0, SunEV100) + FMath::Pow(2.0, MoonEV100));
}

double FGenesisSolar::GetTwilightZenithLuminance(double SunElevationDeg)
{
	const double Depression = -SunElevationDeg;
	if (Depression <= 5.0 || Depression >= 18.0)
	{
		return 0.0;
	}
	struct FPoint { double Depression; double Luminance; };
	static const FPoint Table[] = {
		{ 5.0, 2.5 }, { 6.0, 1.1 }, { 9.0, 0.043 }, { 12.0, 0.0017 }, { 15.0, 0.00043 }, { 18.0, 0.00027 },
	};
	constexpr double NightSky = 0.00027; // Sterne + Airglow liefert das Himmelsmaterial bereits selbst
	double Luminance = NightSky;
	for (int32 i = 1; i < UE_ARRAY_COUNT(Table); ++i)
	{
		if (Depression <= Table[i].Depression)
		{
			// Logarithmisch interpolieren: die Helligkeit faellt exponentiell mit der Sonnentiefe.
			const double Alpha = (Depression - Table[i - 1].Depression) / (Table[i].Depression - Table[i - 1].Depression);
			Luminance = FMath::Exp(FMath::Lerp(FMath::Loge(Table[i - 1].Luminance), FMath::Loge(Table[i].Luminance), Alpha));
			break;
		}
	}
	const double FadeIn = FMath::SmoothStep(5.0, 9.0, Depression);
	return FMath::Max(0.0, Luminance - NightSky) * FadeIn;
}
