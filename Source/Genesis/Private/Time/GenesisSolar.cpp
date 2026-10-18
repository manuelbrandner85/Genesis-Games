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
		{ -18.0, -2.0 },  // astronomische Nacht, kein Mond
		{ -12.0, 2.0 },   // nautische Daemmerung
		{ -9.0, 4.5 },
		{ -6.0, 7.0 },    // Ende buergerliche Daemmerung
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
