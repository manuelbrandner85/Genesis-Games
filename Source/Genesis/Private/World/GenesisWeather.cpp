#include "World/GenesisWeather.h"

#include "Math/RandomStream.h"

namespace
{
	/** Weicher Anstieg 0..1 (Smoothstep). */
	float Smooth(float X)
	{
		X = FMath::Clamp(X, 0.f, 1.f);
		return X * X * (3.f - 2.f * X);
	}

	/** Anstieg ueber Ramp, Plateau, Abfall ueber Decay; Zeit in Stunden ab Beginn des Anstiegs. */
	float Envelope(float Hours, float Ramp, float Plateau, float Decay)
	{
		if (Hours <= 0.f)
		{
			return 0.f;
		}
		if (Hours < Ramp)
		{
			return Smooth(Hours / FMath::Max(Ramp, 0.01f));
		}
		if (Hours < Ramp + Plateau)
		{
			return 1.f;
		}
		return 1.f - Smooth((Hours - Ramp - Plateau) / FMath::Max(Decay, 0.01f));
	}

	float HoursSince(const FDateTime& Start, const FDateTime& Time)
	{
		return float((Time - Start).GetTotalHours());
	}
}

EGenesisWeatherPhase FGenesisStormTimeline::GetPhase(const FDateTime& Time) const
{
	EGenesisWeatherPhase Result = EGenesisWeatherPhase::Calm;
	for (int32 i = 1; i < PhaseStart.Num(); ++i)
	{
		if (Time >= PhaseStart[i])
		{
			Result = EGenesisWeatherPhase(i);
		}
	}
	return Result;
}

FGenesisStormTimeline FGenesisWeather::BuildTimeline(const FGenesisStormScenario& Scenario, int64 WorldSeed, const UGenesisWeatherSettings& Settings)
{
	FGenesisStormTimeline Timeline;
	Timeline.StormId = Scenario.StormId;
	Timeline.Scenario = Scenario;

	// Streuung aus Seed und Sturm-ID: dieselbe Welt bekommt immer denselben Sturm.
	FRandomStream Random(int32(uint32(WorldSeed) ^ uint32(WorldSeed >> 32) ^ GetTypeHash(Scenario.StormId)));
	Timeline.PeakWindMs = Scenario.PeakWindMs * (1.f + Random.FRandRange(-Scenario.WindJitter, Scenario.WindJitter));
	Timeline.RiverRiseM = Scenario.RiverRiseM * (1.f + Random.FRandRange(-Scenario.RiverJitter, Scenario.RiverJitter));
	const float ShiftMinutes = Random.FRandRange(-Scenario.TimeJitterMinutes, Scenario.TimeJitterMinutes);
	Timeline.Start = Scenario.PrecursorStart + FTimespan::FromMinutes(FMath::RoundToInt(ShiftMinutes));

	// Phasenzeiten minutengenau aus den Messwerten selbst: eine Warnung hat einen gemessenen Ausloeser.
	Timeline.PhaseStart.Init(FDateTime::MinValue(), int32(EGenesisWeatherPhase::Settled) + 1);
	Timeline.PhaseStart[int32(EGenesisWeatherPhase::Precursor)] = Timeline.Start;
	const float TotalHours = Scenario.WindLagHours + Scenario.WindRampHours + Scenario.PeakHours + Scenario.DecayHours + 1.f;
	const float PeakEnd = Scenario.WindLagHours + Scenario.WindRampHours + Scenario.PeakHours;
	int32 Reached = int32(EGenesisWeatherPhase::Precursor);
	for (int32 Minute = 1; Minute <= int32(TotalHours * 60.f) && Reached < int32(EGenesisWeatherPhase::Over); ++Minute)
	{
		const FDateTime Time = Timeline.Start + FTimespan::FromMinutes(Minute);
		const FGenesisWeatherReading R = SampleRaw(Timeline, Time, Settings);
		const float Hours = Minute / 60.f;
		auto Enter = [&Timeline, &Reached, Time](EGenesisWeatherPhase Phase)
		{
			Timeline.PhaseStart[int32(Phase)] = Time;
			Reached = int32(Phase);
		};
		if (Reached == int32(EGenesisWeatherPhase::Precursor) && -R.PressureTendency3h >= Settings.AlertPressureFall3hHPa)
		{
			Enter(EGenesisWeatherPhase::Alert);
		}
		else if (Reached == int32(EGenesisWeatherPhase::Alert) && R.WindMs >= Settings.StormWindMs)
		{
			Enter(EGenesisWeatherPhase::Storm);
		}
		else if (Reached == int32(EGenesisWeatherPhase::Storm) && Hours > PeakEnd && R.WindMs < Settings.StormWindMs)
		{
			Enter(EGenesisWeatherPhase::Receding);
		}
		else if (Reached == int32(EGenesisWeatherPhase::Receding) && R.WindMs < Settings.OverWindMs)
		{
			Enter(EGenesisWeatherPhase::Over);
		}
	}
	// Ein schwacher Seed erreicht die Sturmschwelle vielleicht nie: dann bleibt es bei der Warnlage.
	for (int32 i = int32(EGenesisWeatherPhase::Precursor) + 1; i <= int32(EGenesisWeatherPhase::Over); ++i)
	{
		if (Timeline.PhaseStart[i] == FDateTime::MinValue())
		{
			Timeline.PhaseStart[i] = FDateTime::MaxValue();
		}
	}
	const FDateTime Over = Timeline.PhaseStart[int32(EGenesisWeatherPhase::Over)];
	Timeline.PhaseStart[int32(EGenesisWeatherPhase::Settled)] = Over == FDateTime::MaxValue()
		? Timeline.Start + FTimespan::FromHours(TotalHours + Settings.SettledAfterHours)
		: Over + FTimespan::FromHours(Settings.SettledAfterHours);
	return Timeline;
}

FGenesisWeatherReading FGenesisWeather::SampleRaw(const FGenesisStormTimeline& Timeline, const FDateTime& Time, const UGenesisWeatherSettings& Settings)
{
	const FGenesisStormScenario& S = Timeline.Scenario;
	const float Hours = HoursSince(Timeline.Start, Time);
	const float WindHours = Hours - S.WindLagHours;
	// Druck: faellt mit den Vorzeichen, erholt sich mit dem Abklingen.
	auto Pressure = [&](float H)
	{
		const float Fall = Envelope(H, S.PressureFallHours, S.WindLagHours + S.WindRampHours + S.PeakHours - S.PressureFallHours, S.DecayHours * 2.f);
		return Settings.NormalPressureHPa - S.PressureDropHPa * Fall;
	};

	FGenesisWeatherReading R;
	R.PressureHPa = Pressure(Hours);
	R.PressureTendency3h = R.PressureHPa - Pressure(Hours - 3.f);
	const float Wind = Envelope(WindHours, S.WindRampHours, S.PeakHours, S.DecayHours);
	R.WindMs = S.BaseWindMs + (Timeline.PeakWindMs - S.BaseWindMs) * Wind;
	R.RainMmH = S.PeakRainMmH * Envelope(WindHours + 0.5f, S.WindRampHours, S.PeakHours, S.DecayHours);
	R.RiverM = Timeline.RiverRiseM * Envelope(WindHours - S.RiverLagHours, S.WindRampHours, S.PeakHours, S.RiverDecayHours);
	return R;
}

FGenesisWeatherReading FGenesisWeather::Sample(const FGenesisStormTimeline& Timeline, const FDateTime& Time, const UGenesisWeatherSettings& Settings)
{
	FGenesisWeatherReading R = SampleRaw(Timeline, Time, Settings);
	R.Phase = Timeline.GetPhase(Time);
	return R;
}

float FGenesisWeather::MaxRiverBetween(const FGenesisStormTimeline& Timeline, const FDateTime& From, const FDateTime& To, const UGenesisWeatherSettings& Settings)
{
	float Max = SampleRaw(Timeline, To, Settings).RiverM;
	for (FDateTime T = From; T < To; T += FTimespan::FromMinutes(5))
	{
		Max = FMath::Max(Max, SampleRaw(Timeline, T, Settings).RiverM);
	}
	return Max;
}

float FGenesisWeather::MaxWindBetween(const FGenesisStormTimeline& Timeline, const FDateTime& From, const FDateTime& To, const UGenesisWeatherSettings& Settings)
{
	float Max = SampleRaw(Timeline, To, Settings).WindMs;
	for (FDateTime T = From; T < To; T += FTimespan::FromMinutes(5))
	{
		Max = FMath::Max(Max, SampleRaw(Timeline, T, Settings).WindMs);
	}
	return Max;
}

FName FGenesisWeather::PhaseName(EGenesisWeatherPhase Phase)
{
	switch (Phase)
	{
	case EGenesisWeatherPhase::Precursor: return TEXT("Precursor");
	case EGenesisWeatherPhase::Alert: return TEXT("Alert");
	case EGenesisWeatherPhase::Storm: return TEXT("Storm");
	case EGenesisWeatherPhase::Receding: return TEXT("Receding");
	case EGenesisWeatherPhase::Over: return TEXT("Over");
	case EGenesisWeatherPhase::Settled: return TEXT("Settled");
	default: return TEXT("Calm");
	}
}
