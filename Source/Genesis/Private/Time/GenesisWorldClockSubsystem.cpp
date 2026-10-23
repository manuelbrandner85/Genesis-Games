#include "Time/GenesisWorldClockSubsystem.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Save/GenesisSaveSubsystem.h"

FGenesisTimeAdvanceResult UGenesisWorldClockSubsystem::AdvanceTime(FGenesisSaveBundle& Bundle, const FTimespan& Delta, const UGenesisTimeSettings& Settings)
{
	FGenesisTimeAdvanceResult Result;
	if (Delta <= FTimespan::Zero())
	{
		return Result;
	}

	const FDateTime Before = Bundle.World.WorldDateTime;
	const FDateTime After = Before + Delta;
	Bundle.World.WorldDateTime = After;

	Result.DaysChanged = int32((After.GetDate() - Before.GetDate()).GetTotalDays() + 0.5);
	Result.NewSeason = FGenesisLifeCycle::GetSeason(After);
	Result.bSeasonChanged = Result.NewSeason != FGenesisLifeCycle::GetSeason(Before) || Delta.GetTotalDays() >= 365.0;

	const EGenesisLifeStage OldStage = Bundle.Life.Stage;
	const EGenesisLifeStage NewStage = FGenesisLifeCycle::ComputeStage(Bundle.Life, After, Settings);
	if (NewStage != OldStage)
	{
		// Die Abschnitte sind zeitlich geordnet; ein Zeitraffer kann mehrere davon durchlaufen.
		for (uint8 Stage = uint8(OldStage) + 1; Stage <= uint8(NewStage); ++Stage)
		{
			Result.StagesEntered.Add(EGenesisLifeStage(Stage));
		}
		Bundle.Life.Stage = NewStage;
	}
	return Result;
}

bool UGenesisWorldClockSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
	const UWorld* World = Cast<UWorld>(Outer);
	return World && (World->WorldType == EWorldType::Game || World->WorldType == EWorldType::PIE);
}

FGenesisSaveBundle* UGenesisWorldClockSubsystem::GetBundle() const
{
	const UGameInstance* GameInstance = GetWorld() ? GetWorld()->GetGameInstance() : nullptr;
	UGenesisSaveSubsystem* Save = GameInstance ? GameInstance->GetSubsystem<UGenesisSaveSubsystem>() : nullptr;
	return Save ? &Save->GetMutable() : nullptr;
}

FGenesisTimeAdvanceResult UGenesisWorldClockSubsystem::AdvanceAndBroadcast(const FTimespan& Delta)
{
	FGenesisSaveBundle* Bundle = GetBundle();
	if (!Bundle)
	{
		return FGenesisTimeAdvanceResult();
	}

	// Nur ganze Millisekunden in die Weltzeit uebernehmen (Speichergenauigkeit); der Rest wird weitergetragen,
	// damit ueber lange Spielzeit keine Zeit verloren geht.
	const int64 TicksPerMs = ETimespan::TicksPerMillisecond;
	const int64 TotalTicks = Delta.GetTicks() + PendingTicks;
	const int64 WholeTicks = TotalTicks / TicksPerMs * TicksPerMs;
	PendingTicks = TotalTicks - WholeTicks;

	const EGenesisLifeStage OldStage = Bundle->Life.Stage;
	const FGenesisTimeAdvanceResult Result = AdvanceTime(*Bundle, FTimespan(WholeTicks), *GetDefault<UGenesisTimeSettings>());

	if (Result.DaysChanged > 0)
	{
		OnDayChanged.Broadcast(Bundle->World.WorldDateTime);
	}
	if (Result.bSeasonChanged)
	{
		OnSeasonChanged.Broadcast(Result.NewSeason);
	}
	EGenesisLifeStage Previous = OldStage;
	for (const EGenesisLifeStage Stage : Result.StagesEntered)
	{
		OnLifeStageChanged.Broadcast(Previous, Stage);
		Previous = Stage;
	}
	return Result;
}

void UGenesisWorldClockSubsystem::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	const UWorld* World = GetWorld();
	if (!bClockRunning || !World || World->IsPaused())
	{
		return;
	}
	const double GameSeconds = double(DeltaTime) * GetDefault<UGenesisTimeSettings>()->GameSecondsPerRealSecond * TimeScale;
	AdvanceAndBroadcast(FTimespan::FromSeconds(GameSeconds));
}

FGenesisTimeAdvanceResult UGenesisWorldClockSubsystem::SkipTime(float Days)
{
	return AdvanceAndBroadcast(FTimespan::FromDays(Days));
}

FDateTime UGenesisWorldClockSubsystem::GetWorldDateTime() const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	return Bundle ? Bundle->World.WorldDateTime : FDateTime();
}

float UGenesisWorldClockSubsystem::GetTimeOfDayHours() const
{
	return float(GetWorldDateTime().GetTimeOfDay().GetTotalHours());
}

EGenesisSeason UGenesisWorldClockSubsystem::GetSeason() const
{
	return FGenesisLifeCycle::GetSeason(GetWorldDateTime());
}

float UGenesisWorldClockSubsystem::GetPlayerAgeYears() const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	return Bundle ? float(FGenesisLifeCycle::GetAgeYears(Bundle->Life, Bundle->World.WorldDateTime)) : 0.f;
}

TStatId UGenesisWorldClockSubsystem::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(UGenesisWorldClockSubsystem, STATGROUP_Tickables);
}
