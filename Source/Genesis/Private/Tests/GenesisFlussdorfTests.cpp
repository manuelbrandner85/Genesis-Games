#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Causality/GenesisCausality.h"
#include "Save/GenesisSaveStore.h"
#include "World/GenesisFlussdorf.h"
#include "World/GenesisWeather.h"
#include "World/GenesisWorld.h"

namespace GenesisFlussdorfTests
{
	static const UGenesisWeatherSettings& Weather() { return *GetDefault<UGenesisWeatherSettings>(); }
	static const UGenesisFlussdorfSettings& Village() { return *GetDefault<UGenesisFlussdorfSettings>(); }

	static FGenesisStormTimeline Timeline(int64 Seed)
	{
		const FGenesisStormScenario* Scenario = Weather().Storms.FindByPredicate([](const FGenesisStormScenario& S) { return S.StormId == FName(TEXT("STORM_VS01")); });
		return FGenesisWeather::BuildTimeline(Scenario ? *Scenario : FGenesisStormScenario(), Seed, Weather());
	}

	static FGenesisSaveBundle MakeWorld(int64 Seed)
	{
		FGenesisSaveBundle Bundle;
		Bundle.World.WorldSeed = Seed;
		Bundle.World.WorldDateTime = FDateTime(2026, 6, 15, 10, 0, 0);
		Bundle.Life.LocationId = TEXT("/Game/Maps/L_Flussdorf_Graybox");
		return Bundle;
	}

	static FGenesisEventSpec Spec(FName Type, FName Actor, TArray<FName> Targets)
	{
		FGenesisEventSpec S;
		S.EventType = Type;
		S.ActorId = Actor;
		S.TargetIds = MoveTemp(Targets);
		return S;
	}

	static FName Record(FGenesisSaveBundle& Bundle, const FGenesisEventSpec& S)
	{
		return FGenesisCausality::RecordEvent(Bundle, S, *GetDefault<UGenesisCausalitySettings>());
	}

	/** Welt minutenweise (StepMinutes) bis Until fortschreiben; OnStep darf zwischendurch handeln (Spieler). */
	static TArray<FName> Run(FGenesisSaveBundle& Bundle, const FGenesisStormTimeline& T, const FDateTime& Until, int32 StepMinutes,
		TFunctionRef<void(FGenesisSaveBundle&)> OnStep)
	{
		TArray<FName> Triggers;
		auto Rec = [&Bundle](const FGenesisEventSpec& S) { return Record(Bundle, S); };
		while (Bundle.World.WorldDateTime < Until)
		{
			const FDateTime From = Bundle.World.WorldDateTime;
			Bundle.World.WorldDateTime += FTimespan::FromMinutes(StepMinutes);
			FGenesisFlussdorfRules::AdvanceWeather(Bundle, T, From, Bundle.World.WorldDateTime, Rec, Triggers);
			FGenesisFlussdorfRules::EvaluateCoordinator(Bundle, T, Rec, Triggers);
			OnStep(Bundle);
		}
		return Triggers;
	}

	static int32 Obj(const FGenesisSaveBundle& B, FName Object, const TCHAR* Key)
	{
		return FGenesisWorldStateLib::GetObjectValue(B, Object, Key);
	}

	static const FGenesisCausalEvent* FirstOfType(const FGenesisSaveBundle& B, const TCHAR* Type)
	{
		return B.World.CausalEvents.FindByPredicate([Type](const FGenesisCausalEvent& E) { return E.EventType == FName(Type); });
	}

	static const FDateTime DayTwo(2026, 6, 16, 14, 0, 0);
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisWeatherTimelineTest, "Genesis.Flussdorf.Weather.TimelineFromMeasurements",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisWeatherTimelineTest::RunTest(const FString&)
{
	using namespace GenesisFlussdorfTests;
	const FGenesisStormTimeline T = Timeline(0);
	for (int32 i = 1; i < T.PhaseStart.Num(); ++i)
	{
		AddInfo(FString::Printf(TEXT("%s ab %s"), *FGenesisWeather::PhaseName(EGenesisWeatherPhase(i)).ToString(), *T.PhaseStart[i].ToString(TEXT("%d.%m. %H:%M"))));
		TestTrue(TEXT("Phasen in zeitlicher Reihenfolge"), T.PhaseStart[i] > T.PhaseStart[i - 1]);
	}
	AddInfo(FString::Printf(TEXT("Seed 0: Spitzenwind %.1f m/s, Pegel +%.2f m"), T.PeakWindMs, T.RiverRiseM));

	// Die Warnung hat einen gemessenen Ausloeser: zur Alarmzeit faellt der Druck ueber die Schwelle.
	const FGenesisWeatherReading AtAlert = FGenesisWeather::Sample(T, T.PhaseStart[int32(EGenesisWeatherPhase::Alert)], Weather());
	TestTrue(TEXT("Alarm durch gemessenen Druckfall"), -AtAlert.PressureTendency3h >= Weather().AlertPressureFall3hHPa);
	const FGenesisWeatherReading Before = FGenesisWeather::Sample(T, T.PhaseStart[int32(EGenesisWeatherPhase::Alert)] - FTimespan::FromMinutes(2), Weather());
	TestTrue(TEXT("Kurz davor noch kein Alarmwert"), -Before.PressureTendency3h < Weather().AlertPressureFall3hHPa);
	const FGenesisWeatherReading InStorm = FGenesisWeather::Sample(T, T.PhaseStart[int32(EGenesisWeatherPhase::Storm)] + FTimespan::FromMinutes(1), Weather());
	TestTrue(TEXT("Sturm ab Sturmschwelle"), InStorm.WindMs >= Weather().StormWindMs && InStorm.Phase == EGenesisWeatherPhase::Storm);

	// Die Nacht der Naturgewalt: Sturm am Abend, Alarm noch in N01s Arbeitszeit (bis 17 Uhr).
	TestTrue(TEXT("Alarm vor 17 Uhr"), T.PhaseStart[int32(EGenesisWeatherPhase::Alert)].GetHour() < 17);
	TestTrue(TEXT("Sturm am Abend"), T.PhaseStart[int32(EGenesisWeatherPhase::Storm)].GetHour() >= 18);

	// Deterministisch: gleicher Seed = gleicher Verlauf, anderer Seed = andere Staerke.
	const FGenesisStormTimeline Again = Timeline(0);
	TestEqual(TEXT("Gleicher Seed, gleicher Spitzenwind"), Again.PeakWindMs, T.PeakWindMs);
	TestTrue(TEXT("Gleicher Seed, gleiche Sturmzeit"), Again.PhaseStart[3] == T.PhaseStart[3]);
	int32 BridgeSurvives = 0;
	int32 BridgeDamaged = 0;
	for (int64 Seed = 1; Seed <= 200; ++Seed)
	{
		(Timeline(Seed).RiverRiseM >= Village().BridgeDamageRiverM ? BridgeDamaged : BridgeSurvives)++;
	}
	AddInfo(FString::Printf(TEXT("200 Welten: Bruecke haelt %d-mal, nimmt %d-mal Schaden"), BridgeSurvives, BridgeDamaged));
	TestTrue(TEXT("Beide Verlaeufe moeglich (nicht vorbestimmt)"), BridgeSurvives > 0 && BridgeDamaged > 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisWorldStateKeysTest, "Genesis.Flussdorf.WorldState.KeysAndVersions",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisWorldStateKeysTest::RunTest(const FString&)
{
	using namespace GenesisFlussdorfTests;
	FGenesisSaveBundle B = MakeWorld(0);
	TestEqual(TEXT("Startwert aus Projekteinstellungen (Riss vorhanden)"), FGenesisWorldStateLib::GetValue(B, TEXT("VS01_BRIDGE_01.Damage")), 1);
	TestEqual(TEXT("Unbekannter Wert ist 0"), FGenesisWorldStateLib::GetValue(B, TEXT("VS01_BRIDGE_01.Closed")), 0);
	TestTrue(TEXT("Aenderung"), FGenesisWorldStateLib::SetValue(B, TEXT("VS01_BRIDGE_01.Closed"), 1, TEXT("EV_TEST")));
	TestFalse(TEXT("Gleicher Wert ist keine Aenderung"), FGenesisWorldStateLib::SetValue(B, TEXT("VS01_BRIDGE_01.Closed"), 1, TEXT("EV_TEST2")));
	const FGenesisWorldObjectState* Bridge = FGenesisWorldStateLib::FindObject(B, TEXT("VS01_BRIDGE_01"));
	TestTrue(TEXT("Version 1, Ereignis belegt"), Bridge && Bridge->Version == 1 && Bridge->LastEventId == FName(TEXT("EV_TEST")));
	TestEqual(TEXT("Startwerte bleiben erhalten"), FGenesisWorldStateLib::GetValue(B, TEXT("VS01_BRIDGE_01.Passable")), 1);

	FGenesisWorldStateLib::SetValue(B, TEXT("Know.CrackSeen"), 1);
	TestEqual(TEXT("Spielerwissen"), B.Life.Knowledge.FindRef(TEXT("CrackSeen")), 1);
	FGenesisWorldStateLib::SetValue(B, TEXT("WX.Phase"), 3);
	TestEqual(TEXT("Weltflag"), B.World.EventFlags.FindRef(TEXT("WX.Phase")), 3);

	// Weltobjekte bekommen keinen NPC-Zustand im Kausalgraphen.
	Record(B, Spec(TEXT("STORM_DAMAGE"), TEXT("WEATHER"), { TEXT("VS01_BRIDGE_01") }));
	TestNull(TEXT("Bruecke ist keine Figur"), FGenesisCausality::FindNpc(B, TEXT("VS01_BRIDGE_01")));
	TestNull(TEXT("Wetter ist keine Figur"), FGenesisCausality::FindNpc(B, TEXT("WEATHER")));

	// Schema 5: Objekte und Wissen ueberstehen Speichern/Laden.
	TArray<uint8> Bytes;
	FGenesisSaveStore::Encode(B, Bytes);
	FGenesisSaveBundle L;
	TestTrue(TEXT("Laden"), FGenesisSaveStore::Decode(Bytes, L) == EGenesisSaveResult::Ok);
	TestEqual(TEXT("Schema 5"), L.SchemaVersion, 5);
	TestEqual(TEXT("Brueckenzustand geladen"), FGenesisWorldStateLib::GetValue(L, TEXT("VS01_BRIDGE_01.Closed")), 1);
	TestEqual(TEXT("Version geladen"), FGenesisWorldStateLib::FindObject(L, TEXT("VS01_BRIDGE_01"))->Version, 1);
	TestEqual(TEXT("Wissen geladen"), FGenesisWorldStateLib::GetValue(L, TEXT("Know.CrackSeen")), 1);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisPassiveNightTest, "Genesis.Flussdorf.Rules.NightWithoutPlayer",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisPassiveNightTest::RunTest(const FString&)
{
	using namespace GenesisFlussdorfTests;
	const UGenesisFlussdorfSettings& S = Village();
	FGenesisSaveBundle B = MakeWorld(0);
	const FGenesisStormTimeline T = Timeline(0);
	const TArray<FName> Triggers = Run(B, T, DayTwo, 1, [](FGenesisSaveBundle&) {});
	AddInfo(TEXT("Ausloeser: ") + FString::JoinBy(Triggers, TEXT(", "), [](FName N) { return N.ToString(); }));

	// Wetter tritt auch ohne Spieler ein, in fester Reihenfolge, jeder Ausloeser genau einmal.
	const TArray<FName> Expected = { TEXT("WX_PRECURSOR"), TEXT("WX_ALERT"), TEXT("WX_PUBLIC_WARNING"), TEXT("WX_STORM"), TEXT("WX_RECEDED"), TEXT("WX_OVER"), TEXT("WX_SETTLED") };
	TestTrue(TEXT("Alle Wetter-Ausloeser in Reihenfolge, je einmal"), Triggers == Expected);

	// Ohne Spieler erreicht der Alarm N05 erst nach der Meldezeit.
	const FGenesisCausalEvent* Alert = FirstOfType(B, TEXT("WEATHER_ALERT"));
	const FGenesisCausalEvent* Warning = FirstOfType(B, TEXT("PUBLIC_WARNING"));
	if (TestNotNull(TEXT("Alarm"), Alert) && TestNotNull(TEXT("Warnung"), Warning))
	{
		const double Delay = (Warning->WorldTime - Alert->WorldTime).GetTotalMinutes();
		AddInfo(FString::Printf(TEXT("Alarm %s, Warnung %s (%.0f min)"), *Alert->WorldTime.ToString(TEXT("%H:%M")), *Warning->WorldTime.ToString(TEXT("%H:%M")), Delay));
		TestTrue(TEXT("Warnung erst nach Meldezeit"), FMath::Abs(Delay - S.AlertRelayMinutes) <= 1.0);
		TestTrue(TEXT("Warnung kommt von N05 und ist belegt"), Warning->ActorId == S.CommunityCoordinator && Warning->CauseEventIds.Contains(Alert->EventId));
	}

	// Niemand hat den Riss gemeldet: keine Sperrung, kein Pruefauftrag.
	TestEqual(TEXT("Bruecke nicht gesperrt"), Obj(B, S.Bridge, TEXT("Closed")), 0);
	TestNull(TEXT("Kein Pruefauftrag"), FirstOfType(B, TEXT("INSPECTION_REQUESTED")));

	// Schaeden nur aus Pegel und Wind.
	TestEqual(TEXT("Bruecke beschaedigt, wenn der Pegel die Schwelle erreicht"), Obj(B, S.Bridge, TEXT("Damage")), T.RiverRiseM >= S.BridgeDamageRiverM ? 2 : 1);
	TestEqual(TEXT("Uferweg gesperrt, wenn ueberflutet"), Obj(B, S.Trail, TEXT("Open")), T.RiverRiseM >= S.TrailFloodRiverM ? 0 : 1);
	TestEqual(TEXT("Ungesicherte Werkstatt: Lager beschaedigt, wenn der Wind die Schwelle erreicht"), Obj(B, S.Workshop, TEXT("StockDamaged")), T.PeakWindMs >= S.WorkshopDamageWindMs ? 1 : 0);
	TestEqual(TEXT("Station: Alarm aufgehoben"), Obj(B, S.Station, TEXT("Alert")), 0);
	TestEqual(TEXT("Kausalgraph widerspruchsfrei"), FGenesisCausality::ValidateGraph(B).Num(), 0);

	// Idempotent: denselben Zeitraum noch einmal anwenden bucht nichts doppelt.
	const int32 Events = B.World.CausalEvents.Num();
	TArray<FName> Again;
	auto Rec = [&B](const FGenesisEventSpec& Sp) { return Record(B, Sp); };
	FGenesisFlussdorfRules::AdvanceWeather(B, T, FDateTime(2026, 6, 15, 10, 0, 0), DayTwo, Rec, Again);
	FGenesisFlussdorfRules::EvaluateCoordinator(B, T, Rec, Again);
	TestEqual(TEXT("Keine doppelten Ereignisse"), B.World.CausalEvents.Num(), Events);
	TestEqual(TEXT("Keine doppelten Ausloeser"), Again.Num(), 0);

	// Zeitraffer in einem Schritt ergibt denselben Weltzustand wie minutenweise.
	FGenesisSaveBundle Skip = MakeWorld(0);
	Run(Skip, T, DayTwo, 60 * 28, [](FGenesisSaveBundle&) {});
	for (const TCHAR* Key : { TEXT("Damage"), TEXT("Passable"), TEXT("Closed") })
	{
		TestEqual(FString::Printf(TEXT("Zeitraffer: Bruecke %s"), Key), Obj(Skip, S.Bridge, Key), Obj(B, S.Bridge, Key));
	}
	TestEqual(TEXT("Zeitraffer: Uferweg"), Obj(Skip, S.Trail, TEXT("Open")), Obj(B, S.Trail, TEXT("Open")));
	TestEqual(TEXT("Zeitraffer: Werkstatt"), Obj(Skip, S.Workshop, TEXT("StockDamaged")), Obj(B, S.Workshop, TEXT("StockDamaged")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisEngagedNightTest, "Genesis.Flussdorf.Rules.NightWithReportsAndWarnings",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FGenesisEngagedNightTest::RunTest(const FString&)
{
	using namespace GenesisFlussdorfTests;
	const UGenesisFlussdorfSettings& S = Village();
	const FName Player = FGenesisCausality::PlayerSubjectId(0);
	FGenesisSaveBundle B = MakeWorld(0);
	const FGenesisStormTimeline T = Timeline(0);
	const FDateTime AlertTime = T.PhaseStart[int32(EGenesisWeatherPhase::Alert)];
	const FDateTime ActTime = AlertTime + FTimespan::FromMinutes(15);
	bool bActed = false;

	// Der Spieler liest die Station, meldet N05 Werte und Riss und warnt N01 und N04 - wie im Spiel per Gespraech.
	Run(B, T, DayTwo, 1, [&](FGenesisSaveBundle& W)
	{
		if (!bActed && W.World.WorldDateTime >= ActTime)
		{
			bActed = true;
			Record(W, Spec(TEXT("ALERT_REPORTED"), Player, { S.CommunityCoordinator }));
			Record(W, Spec(TEXT("BRIDGE_DAMAGE_REPORTED"), Player, { S.CommunityCoordinator, S.Bridge }));
			Record(W, Spec(TEXT("WARNING_RECEIVED"), Player, { S.WorkshopOwner }));
			Record(W, Spec(TEXT("WARNING_RECEIVED"), Player, { S.DeliveryDriver }));
			TestEqual(TEXT("N01 sichert die Werkstatt"), FGenesisFlussdorfRules::ReactionFor(W, S.WorkshopOwner, TEXT("Work"), EGenesisWeatherPhase::Alert), FName(TEXT("Secure")));
			TestEqual(TEXT("N04 setzt aus"), FGenesisFlussdorfRules::ReactionFor(W, S.DeliveryDriver, TEXT("Home"), EGenesisWeatherPhase::Alert), FName(TEXT("Home")));
			// Sichern dauert in der Welt (PIE-Test); hier das Ergebnis eintragen.
			const FName Secured = Record(W, Spec(TEXT("WORKSHOP_SECURED"), S.WorkshopOwner, { S.Workshop }));
			FGenesisWorldStateLib::SetObjectValue(W, S.Workshop, TEXT("Secured"), 1, Secured);
		}
	});

	const FGenesisCausalEvent* Warning = FirstOfType(B, TEXT("PUBLIC_WARNING"));
	const FGenesisCausalEvent* Closed = FirstOfType(B, TEXT("BRIDGE_CLOSED"));
	if (TestNotNull(TEXT("Warnung"), Warning) && TestNotNull(TEXT("Sperrung"), Closed))
	{
		AddInfo(FString::Printf(TEXT("Alarm %s, Meldung %s, Warnung %s, Sperrung %s"), *AlertTime.ToString(TEXT("%H:%M")), *ActTime.ToString(TEXT("%H:%M")),
			*Warning->WorldTime.ToString(TEXT("%H:%M")), *Closed->WorldTime.ToString(TEXT("%H:%M"))));
		TestTrue(TEXT("Warnung frueher als ohne Spieler"), Warning->WorldTime < AlertTime + FTimespan::FromMinutes(S.AlertRelayMinutes));
		TestTrue(TEXT("Sperrung vor dem Sturm"), Closed->WorldTime < T.PhaseStart[int32(EGenesisWeatherPhase::Storm)]);
		TestEqual(TEXT("Sperrung durch N05"), Closed->ActorId, S.CommunityCoordinator);
	}
	TestEqual(TEXT("Pruefauftrag gespeichert"), Obj(B, S.Bridge, TEXT("InspectionRequested")), 1);
	TestEqual(TEXT("Ohne Pruefperson bleibt die Bruecke zu"), Obj(B, S.Bridge, TEXT("Closed")), 1);
	TestEqual(TEXT("Gesicherte Werkstatt: kein Lagerschaden"), Obj(B, S.Workshop, TEXT("StockDamaged")), 0);
	// Der Pegel richtet sich nicht nach dem Spieler.
	TestEqual(TEXT("Brueckenschaden haengt nur am Pegel"), Obj(B, S.Bridge, TEXT("Damage")), T.RiverRiseM >= S.BridgeDamageRiverM ? 2 : 1);
	TestTrue(TEXT("N01 hat der Spieler gewarnt (Erinnerung)"), FGenesisFlussdorfRules::KnowsWarning(B, S.WorkshopOwner));
	TestTrue(TEXT("N05 vertraut dem Spieler mehr"), FGenesisCausality::GetAttitude(B, S.CommunityCoordinator, Player).Trust > 0.f);
	TestEqual(TEXT("Kausalgraph widerspruchsfrei"), FGenesisCausality::ValidateGraph(B).Num(), 0);

	// Im Sturm sucht jede Figur Schutz, auch ohne Warnung; nach dem Sturm gilt wieder der Tagesplan.
	FGenesisSaveBundle Fresh = MakeWorld(0);
	TestEqual(TEXT("Sturm: Schutz"), FGenesisFlussdorfRules::ReactionFor(Fresh, S.WorkshopOwner, TEXT("Work"), EGenesisWeatherPhase::Storm), FName(TEXT("Home")));
	TestEqual(TEXT("Ohne Warnung vor dem Sturm: Tagesplan"), FGenesisFlussdorfRules::ReactionFor(Fresh, S.WorkshopOwner, TEXT("Work"), EGenesisWeatherPhase::Alert), FName());
	TestEqual(TEXT("Nach dem Sturm: Tagesplan"), FGenesisFlussdorfRules::ReactionFor(B, S.WorkshopOwner, TEXT("Work"), EGenesisWeatherPhase::Over), FName());
	return true;
}

#endif
