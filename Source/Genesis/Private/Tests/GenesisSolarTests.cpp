#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Time/GenesisSolar.h"

namespace GenesisSolarTests
{
	static const double Lat = 49.0;
	static const double Lon = 10.0;

	/** Hoechster Sonnenstand eines Tages (Minutenraster, UTC) und der Zeitpunkt dazu. */
	static FGenesisSunPosition DayMaximum(int32 Year, int32 Month, int32 Day, FDateTime& OutUtc)
	{
		FGenesisSunPosition Best;
		Best.ElevationDeg = -90.0;
		for (int32 Minute = 0; Minute < 24 * 60; ++Minute)
		{
			const FDateTime Utc = FDateTime(Year, Month, Day) + FTimespan::FromMinutes(Minute);
			const FGenesisSunPosition P = FGenesisSolar::Compute(Utc, Lat, Lon);
			if (P.ElevationDeg > Best.ElevationDeg)
			{
				Best = P;
				OutUtc = Utc;
			}
		}
		return Best;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSolarNoonTest, "Genesis.Sky.Solar.NoonElevationAndAzimuth",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSolarNoonTest::RunTest(const FString&)
{
	using namespace GenesisSolarTests;
	FDateTime NoonUtc;

	// Sommersonnenwende: 90 - 49 + 23,44 = 64,44 Grad, Sonne im Sueden.
	FGenesisSunPosition P = DayMaximum(2026, 6, 21, NoonUtc);
	AddInfo(FString::Printf(TEXT("21.06.2026: Hoehe %.3f, Azimut %.2f um %s UTC"), P.ElevationDeg, P.AzimuthDeg, *NoonUtc.ToString(TEXT("%H:%M"))));
	TestTrue(TEXT("Sommer-Mittagshoehe 64,44 +/- 0,1"), FMath::IsNearlyEqual(P.ElevationDeg, 64.44, 0.1));
	TestTrue(TEXT("Mittags im Sueden (180 +/- 1)"), FMath::IsNearlyEqual(P.AzimuthDeg, 180.0, 1.0));
	// Sonnenhoechststand bei 10 Grad Ost: 12:00 - 40 min (+ Zeitgleichung ca. +1,5 min Ende Juni) = ca. 11:21 UTC.
	const double NoonMinutes = NoonUtc.GetHour() * 60.0 + NoonUtc.GetMinute();
	TestTrue(TEXT("Mittag um ca. 11:21 UTC (+/- 3 min)"), FMath::IsNearlyEqual(NoonMinutes, 11.0 * 60.0 + 21.0, 3.0));

	// Wintersonnenwende: 90 - 49 - 23,44 = 17,56 Grad.
	P = DayMaximum(2026, 12, 21, NoonUtc);
	AddInfo(FString::Printf(TEXT("21.12.2026: Hoehe %.3f"), P.ElevationDeg));
	TestTrue(TEXT("Winter-Mittagshoehe 17,56 +/- 0,1"), FMath::IsNearlyEqual(P.ElevationDeg, 17.56, 0.1));

	// Tagundnachtgleiche (20.03.2026, 14:46 UTC): ca. 90 - 49 = 41 Grad (Deklination am Mittag ca. -0,1).
	P = DayMaximum(2026, 3, 20, NoonUtc);
	AddInfo(FString::Printf(TEXT("20.03.2026: Hoehe %.3f"), P.ElevationDeg));
	TestTrue(TEXT("Aequinoktium-Mittagshoehe 41 +/- 0,3"), FMath::IsNearlyEqual(P.ElevationDeg, 41.0, 0.3));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSolarSunriseTest, "Genesis.Sky.Solar.EquinoxSunriseInTheEast",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSolarSunriseTest::RunTest(const FString&)
{
	using namespace GenesisSolarTests;
	// Erster Zeitpunkt mit Hoehe > 0 am 20.03.: Azimut ca. 90 Grad (Osten).
	for (int32 Minute = 0; Minute < 12 * 60; ++Minute)
	{
		const FGenesisSunPosition P = FGenesisSolar::Compute(FDateTime(2026, 3, 20) + FTimespan::FromMinutes(Minute), Lat, Lon);
		if (P.ElevationDeg > 0.0)
		{
			AddInfo(FString::Printf(TEXT("Aufgang 20.03.: %02d:%02d UTC, Azimut %.2f"), Minute / 60, Minute % 60, P.AzimuthDeg));
			TestTrue(TEXT("Aufgang im Osten (90 +/- 1,5)"), FMath::IsNearlyEqual(P.AzimuthDeg, 90.0, 1.5));
			return true;
		}
	}
	AddError(TEXT("Kein Sonnenaufgang gefunden."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisSummerTimeTest, "Genesis.Sky.Solar.EuSummerTime",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisSummerTimeTest::RunTest(const FString&)
{
	// 2026: Beginn 29.03. 01:00 UTC, Ende 25.10. 01:00 UTC.
	TestFalse(TEXT("28.03. Winterzeit"), FGenesisSolar::IsEuSummerTime(FDateTime(2026, 3, 28, 12, 0, 0)));
	TestTrue(TEXT("29.03. 01:00 UTC Sommerzeit"), FGenesisSolar::IsEuSummerTime(FDateTime(2026, 3, 29, 1, 0, 0)));
	TestTrue(TEXT("25.10. 00:59 UTC Sommerzeit"), FGenesisSolar::IsEuSummerTime(FDateTime(2026, 10, 25, 0, 59, 0)));
	TestFalse(TEXT("25.10. 01:00 UTC Winterzeit"), FGenesisSolar::IsEuSummerTime(FDateTime(2026, 10, 25, 1, 0, 0)));

	TestEqual(TEXT("Juni: 12:00 MESZ = 10:00 UTC"), FGenesisSolar::LocalToUtc(FDateTime(2026, 6, 15, 12, 0, 0), 1.0, true), FDateTime(2026, 6, 15, 10, 0, 0));
	TestEqual(TEXT("Januar: 12:00 MEZ = 11:00 UTC"), FGenesisSolar::LocalToUtc(FDateTime(2026, 1, 15, 12, 0, 0), 1.0, true), FDateTime(2026, 1, 15, 11, 0, 0));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisExposureTableTest, "Genesis.Sky.Exposure.ClearSkyEV100",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisExposureTableTest::RunTest(const FString&)
{
	TestEqual(TEXT("Hoher Sonnenstand: Sunny-16 = EV 15"), FGenesisSolar::GetClearSkyEV100(60.0), 15.0);
	TestEqual(TEXT("Horizont: EV 11,5"), FGenesisSolar::GetClearSkyEV100(0.0), 11.5);
	TestEqual(TEXT("Tiefe Nacht: EV -2"), FGenesisSolar::GetClearSkyEV100(-40.0), -2.0);
	TestTrue(TEXT("Zwischenwert interpoliert"), FMath::IsNearlyEqual(FGenesisSolar::GetClearSkyEV100(-4.5), 8.25, 1e-9));

	// Monoton: je hoeher die Sonne, desto heller (hoeheres EV), nie Spruenge > 1 EV pro Grad.
	double Previous = FGenesisSolar::GetClearSkyEV100(-20.0);
	for (double E = -19.75; E <= 40.0; E += 0.25)
	{
		const double Ev = FGenesisSolar::GetClearSkyEV100(E);
		if (Ev < Previous || Ev - Previous > 0.25)
		{
			AddError(FString::Printf(TEXT("Nicht monoton/glatt bei %.2f Grad: %.3f -> %.3f"), E, Previous, Ev));
			break;
		}
		Previous = Ev;
	}
	return true;
}

#endif
