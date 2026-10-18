#include "Time/GenesisTimeTypes.h"

double FGenesisLifeCycle::GetAgeYears(const FGenesisLifeState& Life, const FDateTime& Now)
{
	if (!Life.bBorn)
	{
		return 0.0;
	}
	return FMath::Max(0.0, (Now - Life.BirthDateTime).GetTotalDays() / DaysPerYear);
}

double FGenesisLifeCycle::GetDaysSinceConception(const FGenesisLifeState& Life, const FDateTime& Now)
{
	return FMath::Max(0.0, (Now - Life.ConceptionDateTime).GetTotalDays());
}

EGenesisLifeStage FGenesisLifeCycle::ComputeStage(const FGenesisLifeState& Life, const FDateTime& Now, const UGenesisTimeSettings& Settings)
{
	if (Life.Stage == EGenesisLifeStage::Echo)
	{
		return EGenesisLifeStage::Echo;
	}

	if (!Life.bBorn)
	{
		const double Days = GetDaysSinceConception(Life, Now);
		if (Days < Settings.EmbryoStartDay)
		{
			return EGenesisLifeStage::Conception;
		}
		if (Days < Settings.FetusStartDay)
		{
			return EGenesisLifeStage::Embryo;
		}
		if (Days < Settings.BirthStartDay)
		{
			return EGenesisLifeStage::Fetus;
		}
		return EGenesisLifeStage::Birth;
	}

	const double Age = GetAgeYears(Life, Now);
	if (Age < Settings.ChildStartYears)
	{
		return EGenesisLifeStage::Infant;
	}
	if (Age < Settings.AdolescentStartYears)
	{
		return EGenesisLifeStage::Child;
	}
	if (Age < Settings.AdultStartYears)
	{
		return EGenesisLifeStage::Adolescent;
	}
	if (Age < Settings.ElderStartYears)
	{
		return EGenesisLifeStage::Adult;
	}
	return EGenesisLifeStage::Elder;
}

void FGenesisLifeCycle::CompleteBirth(FGenesisLifeState& Life, const FDateTime& Now)
{
	Life.bBorn = true;
	Life.BirthDateTime = Now;
	Life.Stage = EGenesisLifeStage::Infant;
}

EGenesisSeason FGenesisLifeCycle::GetSeason(const FDateTime& Date)
{
	switch (Date.GetMonth())
	{
	case 3: case 4: case 5:
		return EGenesisSeason::Spring;
	case 6: case 7: case 8:
		return EGenesisSeason::Summer;
	case 9: case 10: case 11:
		return EGenesisSeason::Autumn;
	default:
		return EGenesisSeason::Winter;
	}
}

FDateTime FGenesisLifeCycle::ToSavePrecision(const FDateTime& Value)
{
	const int64 TicksPerMs = ETimespan::TicksPerMillisecond;
	return FDateTime((Value.GetTicks() + TicksPerMs / 2) / TicksPerMs * TicksPerMs);
}
