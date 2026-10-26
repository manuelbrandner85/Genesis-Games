#pragma once
#include "CoreMinimal.h"

/**
 * Playable pregnancy (ScriptLock 1.3 C02-E -> C03 -> C04, design/SCHWANGERSCHAFT_KONZEPT.md, GD-2026-10-26-02):
 * ten stages from the first divisions to the birth, a week clock in days since fertilisation (the clinical
 * "SSW" counts from the last period, +14 days) and actions that exist only from the day the development
 * makes them possible. No thoughts, no voice, no score; every action has a visible consequence outside.
 */
enum class EGenesisPregAction : uint8
{
    Observe,        // always: look around (camera)
    TimeLapse,      // always: let the time run faster
    Magnify,        // always: the documentation lens / labels
    Twitch,         // first spontaneous movements (~day 38)
    Stretch,
    Grasp,
    Swallow,
    ThumbSuck,      // ~day 70
    Kick,
    Turn,           // while there is room (until ~day 224)
    ReactToVoice,   // hearing works (~day 154)
    TurnToLight,    // eyes open (~day 175)
    SleepWake,
    Count
};

struct GENESIS_API FGenesisPregStage
{
    const TCHAR* Id;            // S1..S10
    const TCHAR* Title;         // what happens (shown in the HUD)
    float StartDay;             // days since fertilisation
    float EndDay;
    float PlaySeconds;          // playtime of the stage (P1: all together ~2.5 h)
};

struct GENESIS_API FGenesisPregnancy
{
    static constexpr float BirthDay = 266.f;      // 38 weeks after fertilisation = SSW 40
    static constexpr float QuickeningDay = 126.f; // from here the mother feels kicks (SSW ~20)

    static const TArray<FGenesisPregStage>& Stages();
    /** First day on which an action is biologically possible (and last day for Turn). */
    static float FirstDay(EGenesisPregAction A);
    static float LastDay(EGenesisPregAction A);
    static const TCHAR* ActionName(EGenesisPregAction A);
    /** "SSW" counted clinically from the last period. */
    static int32 GestationalWeek(float Day) { return int32((Day + 14.f) / 7.f); }

    int32 Stage = 0;
    float Day = 0.f;
    float StageTime = 0.f;
    float TimeScale = 1.f;           // TimeLapse: x8 while held
    bool bBorn = false;
    bool bC03Due = false;            // late pregnancy reached: C03 "Ich höre dich" (once)
    bool bC03Done = false;
    int32 Shortened = 0;

    const FGenesisPregStage& Current() const { return Stages()[Stage]; }
    bool IsAllowed(EGenesisPregAction A) const;
    TArray<EGenesisPregAction> AllowedActions() const;
    /** Performs an action if the development allows it. OutWorld: the visible consequence outside
     *  (ledger action id), empty if nobody outside can notice it (e.g. a kick before day 126). */
    bool Perform(EGenesisPregAction A, FName& OutWorld) const;
    /** Advances the stage clock; the day runs linearly through the stage over its playtime. Returns true
     *  when a new stage began. */
    bool Tick(float DeltaSeconds);
    /** P2: jump to the start of the next stage (world time and development are carried forward). */
    bool ShortenStage();
    /** Set from a save (stage id or Born, day, whether C03 was already shown). */
    void Restore(FName StageId, float InDay, bool bInC03Done);
    FName StageId() const { return bBorn ? FName(TEXT("Born")) : FName(Current().Id); }

private:
    void EnterStage(int32 NewStage);
};
