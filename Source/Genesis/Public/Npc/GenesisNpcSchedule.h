#pragma once
#include "CoreMinimal.h"

/** One block of a NPC's day: where the person is between StartMinute and EndMinute. */
struct GENESIS_API FGenesisScheduleEntry
{
    int32 StartMinute = 0;      // minute of day, inclusive
    int32 EndMinute = 0;        // minute of day, exclusive
    FName Anchor;               // TargetPoint tag in the level, e.g. N01_Work
    FName Region;               // R01..R08, for checks and UI
    bool bIndoorsPrivate = false; // at home: inside the closed house, not visible
};

/**
 * Daily routines of the Flussdorf NPCs.
 * Source: V24_NPC_UND_EREIGNISSIMULATION (working canon, candidate) - base, private place and
 * routine per role. Where the source says "vormittags" or "Termine variieren", the exact minutes
 * are Startwerte (docs/design/G6_FLUSSDORF_WERKSTATT.md).
 */
struct GENESIS_API FGenesisNpcSchedules
{
    static const TArray<FGenesisScheduleEntry>& Get(FName NpcID);
    /** Entry active at the given minute of day (falls back to the last one, i.e. home). */
    static const FGenesisScheduleEntry* Find(FName NpcID, int32 MinuteOfDay);
};
