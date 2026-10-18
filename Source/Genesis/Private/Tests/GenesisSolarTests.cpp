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
	TestEqual(TEXT("Tiefe Nacht ohne Mond: EV -7"), FGenesisSolar::GetClearSkyEV100(-40.0), -7.0);
	TestTrue(TEXT("Zwischenwert interpoliert"), FMath::IsNearlyEqual(FGenesisSolar::GetClearSkyEV100(-4.5), 7.25, 1e-9));

	// Monoton: je hoeher die Sonne, desto heller (hoeheres EV), nie Spruenge > 3 EV pro Grad (Daemmerung faellt steil ab).
	double Previous = FGenesisSolar::GetClearSkyEV100(-20.0);
	for (double E = -19.75; E <= 40.0; E += 0.25)
	{
		const double Ev = FGenesisSolar::GetClearSkyEV100(E);
		if (Ev < Previous || Ev - Previous > 0.75)
		{
			AddError(FString::Printf(TEXT("Nicht monoton/glatt bei %.2f Grad: %.3f -> %.3f"), E, Previous, Ev));
			break;
		}
		Previous = Ev;
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisMoonPhaseTest, "Genesis.Sky.Moon.PhasesAtEclipses2026",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisMoonPhaseTest::RunTest(const FString&)
{
	using namespace GenesisSolarTests;
	struct FCase { FDateTime Utc; bool bFull; const TCHAR* Name; };
	const FCase Cases[] = {
		{ FDateTime(2026, 2, 17, 12, 1, 0), false, TEXT("Ringfoermige Sonnenfinsternis 17.02.2026") },
		{ FDateTime(2026, 3, 3, 11, 38, 0), true, TEXT("Totale Mondfinsternis 03.03.2026") },
		{ FDateTime(2026, 8, 12, 17, 46, 0), false, TEXT("Totale Sonnenfinsternis 12.08.2026") },
		{ FDateTime(2026, 8, 28, 4, 13, 0), true, TEXT("Partielle Mondfinsternis 28.08.2026") },
	};
	for (const FCase& C : Cases)
	{
		const FGenesisMoonState Moon = FGenesisSolar::ComputeMoon(C.Utc, Lat, Lon);
		AddInfo(FString::Printf(TEXT("%s: beleuchtet %.4f, Phasenwinkel %.2f, %.4f lx"), C.Name, Moon.IlluminatedFraction, Moon.PhaseAngleDeg, Moon.IlluminanceLux));
		if (C.bFull)
		{
			TestTrue(FString::Printf(TEXT("%s: Vollmond"), C.Name), Moon.IlluminatedFraction > 0.995);
			TestTrue(FString::Printf(TEXT("%s: ca. 0,25-0,32 lx"), C.Name), Moon.IlluminanceLux > 0.2 && Moon.IlluminanceLux < 0.35);
		}
		else
		{
			TestTrue(FString::Printf(TEXT("%s: Neumond"), C.Name), Moon.IlluminatedFraction < 0.005);
			TestTrue(FString::Printf(TEXT("%s: kein Mondlicht"), C.Name), Moon.IlluminanceLux < 0.001);
		}
	}
	return true;
}

namespace GenesisSolarTests
{
	/** Unabhaengiger Rechenweg: klassische Formel Stundenwinkel -> Hoehe/Azimut. */
	static void ClassicAltAz(double RaDeg, double DecDeg, const FDateTime& Utc, double& OutAlt, double& OutAz)
	{
		const double H = FMath::DegreesToRadians(FGenesisSolar::GetLocalSiderealTimeDeg(Utc, Lon) - RaDeg);
		const double D = FMath::DegreesToRadians(DecDeg);
		const double P = FMath::DegreesToRadians(Lat);
		OutAlt = FMath::RadiansToDegrees(FMath::Asin(FMath::Sin(P) * FMath::Sin(D) + FMath::Cos(P) * FMath::Cos(D) * FMath::Cos(H)));
		OutAz = FMath::RadiansToDegrees(FMath::Atan2(-FMath::Sin(H), FMath::Tan(D) * FMath::Cos(P) - FMath::Sin(P) * FMath::Cos(H)));
		OutAz = OutAz < 0.0 ? OutAz + 360.0 : OutAz;
	}

	static void WorldToAltAz(const FVector& V, double& OutAlt, double& OutAz)
	{
		OutAlt = FMath::RadiansToDegrees(FMath::Asin(FMath::Clamp(V.Z, -1.0, 1.0)));
		OutAz = FMath::RadiansToDegrees(FMath::Atan2(V.Y, V.X));
		OutAz = OutAz < 0.0 ? OutAz + 360.0 : OutAz;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisCelestialBasisTest, "Genesis.Sky.Stars.CelestialBasis",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisCelestialBasisTest::RunTest(const FString&)
{
	using namespace GenesisSolarTests;
	const FDateTime Times[] = { FDateTime(2026, 6, 15, 21, 30, 0), FDateTime(2026, 8, 12, 21, 45, 0), FDateTime(2026, 12, 24, 23, 0, 0) };
	for (const FDateTime& Utc : Times)
	{
		const FGenesisCelestialBasis B = FGenesisSolar::GetCelestialBasis(Utc, Lat, Lon);
		TestTrue(TEXT("Achsen normiert"), FMath::IsNearlyEqual(B.AxisRA0.Size(), 1.0, 1e-9) && FMath::IsNearlyEqual(B.AxisRA18.Size(), 1.0, 1e-9) && FMath::IsNearlyEqual(B.AxisPole.Size(), 1.0, 1e-9));
		TestTrue(TEXT("Achsen senkrecht"), FMath::Abs(B.AxisRA0 | B.AxisRA18) < 1e-9 && FMath::Abs(B.AxisRA0 | B.AxisPole) < 1e-9);
		TestTrue(TEXT("Echte Drehung (Determinante +1)"), FMath::IsNearlyEqual((B.AxisRA0 ^ B.AxisRA18) | B.AxisPole, 1.0, 1e-9));

		double Alt, Az;
		WorldToAltAz(FGenesisSolar::EquatorialToWorld(37.95, 89.264, B), Alt, Az);
		TestTrue(TEXT("Polarstern auf Hoehe der Breite (49 +/- 0,8)"), FMath::IsNearlyEqual(Alt, Lat, 0.8));
		TestTrue(TEXT("Polarstern im Norden (+/- 1,2)"), Az < 1.2 || Az > 358.8);

		// Vega und Sirius: Basis gegen klassische Formel.
		const double Stars[][2] = { { 279.2347, 38.7837 }, { 101.2872, -16.7161 } };
		for (const auto& S : Stars)
		{
			double AltB, AzB, AltC, AzC;
			WorldToAltAz(FGenesisSolar::EquatorialToWorld(S[0], S[1], B), AltB, AzB);
			ClassicAltAz(S[0], S[1], Utc, AltC, AzC);
			const double DAz = FMath::Abs(FMath::Fmod(AzB - AzC + 540.0, 360.0) - 180.0);
			TestTrue(FString::Printf(TEXT("Stern RA %.1f: Hoehe gleich (%.4f / %.4f)"), S[0], AltB, AltC), FMath::IsNearlyEqual(AltB, AltC, 1e-6));
			TestTrue(FString::Printf(TEXT("Stern RA %.1f: Azimut gleich"), S[0]), DAz < 1e-6 || FMath::Abs(AltC) > 89.9);
		}
	}
	return true;
}

#endif
