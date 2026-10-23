#include "Npc/GenesisNpcSchedule.h"

namespace
{
    constexpr int32 H(int32 Hour, int32 Minute = 0) { return Hour * 60 + Minute; }
    const TArray<FGenesisScheduleEntry> Empty;

    const TMap<FName, TArray<FGenesisScheduleEntry>>& Table()
    {
        static const TMap<FName, TArray<FGenesisScheduleEntry>> T = {
            // N01 WorkshopOwner: base R03, private R07; source: 09:00-17:00 work, then private.
            { TEXT("N01"), {
                { H(0), H(9), TEXT("N01_Home"), TEXT("R07"), true },
                { H(9), H(17), TEXT("N01_Work"), TEXT("R03"), false },
                { H(17), H(24), TEXT("N01_Home"), TEXT("R07"), true } } },
            // N02 RepairCustomer: base R02, private R07; source: errands in the morning,
            // appointments only by agreement. Startwert: 08:30-12:00 at the market.
            { TEXT("N02"), {
                { H(0), H(8, 30), TEXT("N02_Home"), TEXT("R07"), true },
                { H(8, 30), H(12), TEXT("N02_Errands"), TEXT("R02"), false },
                { H(12), H(24), TEXT("N02_Home"), TEXT("R07"), true } } },
            // N03 MarketOwner: base R02, private R07; source: 08:00-18:00 while the shop is open.
            { TEXT("N03"), {
                { H(0), H(8), TEXT("N03_Home"), TEXT("R07"), true },
                { H(8), H(18), TEXT("N03_Work"), TEXT("R02"), false },
                { H(18), H(24), TEXT("N03_Home"), TEXT("R07"), true } } },
        };
        return T;
    }
}

const TArray<FGenesisScheduleEntry>& FGenesisNpcSchedules::Get(FName NpcID)
{
    const TArray<FGenesisScheduleEntry>* E = Table().Find(NpcID);
    return E ? *E : Empty;
}

const FGenesisScheduleEntry* FGenesisNpcSchedules::Find(FName NpcID, int32 MinuteOfDay)
{
    const TArray<FGenesisScheduleEntry>& Entries = Get(NpcID);
    for (const FGenesisScheduleEntry& E : Entries) {
        if (MinuteOfDay >= E.StartMinute && MinuteOfDay < E.EndMinute) {
            return &E;
        }
    }
    return Entries.Num() ? &Entries.Last() : nullptr;
}
