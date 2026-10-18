#include "Npc/GenesisNpcTypes.h"

FName UGenesisNpcSettings::GetActivity(FName NpcId, float HourOfDay) const
{
	const FGenesisNpcSchedule* Schedule = Schedules.FindByPredicate([NpcId](const FGenesisNpcSchedule& S) { return S.NpcId == NpcId; });
	if (Schedule)
	{
		for (const FGenesisScheduleEntry& Entry : Schedule->Entries)
		{
			const bool bWraps = Entry.EndHour < Entry.StartHour;
			const bool bInside = bWraps
				? (HourOfDay >= Entry.StartHour || HourOfDay < Entry.EndHour)
				: (HourOfDay >= Entry.StartHour && HourOfDay < Entry.EndHour);
			if (bInside)
			{
				return Entry.Activity;
			}
		}
	}
	return DefaultActivity;
}

FGameplayTag UGenesisNpcSettings::ActivityTag(FName Activity)
{
	return FGameplayTag::RequestGameplayTag(FName(*(TEXT("Genesis.Activity.") + Activity.ToString())), false);
}
