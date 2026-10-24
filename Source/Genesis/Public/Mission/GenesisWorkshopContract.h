#pragma once
#include "CoreMinimal.h"

class UGenesisWorldStateSubsystem;

/** A choice the player can make in a conversation / at an object. Disabled choices carry a reason. */
struct GENESIS_API FGenesisChoice
{
    FName Action;
    FText Text;
    bool bEnabled = true;
    FText Reason;
};

/** What a person (or the object) answers. Speaker None = description of an observation. */
struct GENESIS_API FGenesisReply
{
    FName Speaker;
    FText Line;
};

/** Where each NPC is right now: region tag (R02, R03 ...) if standing there, None if at home /
 *  inside / still walking. Built from the real actors in the game, from the schedule in tests. */
using FGenesisPresence = TMap<FName, FName>;

/**
 * Kette A "Die Werkstatt" / S24-02 "Der Preis der Hilfe" (V24_MISSIONSBIBEL, working canon).
 *
 * All state lives in UGenesisWorldStateSubsystem (object states, items, ledger), so the chain is
 * saved/loaded as a whole and every step is an idempotent event. Terminal states: Completed,
 * CompletedByN01, Declined, Withdrawn - every reachable state leads to one of them (tested).
 *
 * From the source: N02 brings a real order and may reject a price or withdraw; diagnosis shows at
 * least two plausible, checkable causes; the part belongs to the market and is reserved on the
 * agreement; 60 GE example payment exactly once after acceptance by the customer; 18 GE part only
 * if in stock and affordable; reloading never pays twice. Everything else is a Startwert
 * (docs/design/G6_FLUSSDORF_WERKSTATT.md); all spoken lines are DRAFT_NEEDS_APPROVAL.
 */
struct GENESIS_API FGenesisWorkshopContract
{
    // Object / item IDs
    static const FName Contract;         // CT_GENERATOR_N02
    static const FName Generator;        // OBJ_GENERATOR_N02: Defect -> Repaired
    static const FName Tool;             // TOOL_PLUG_WRENCH: N01 | Player
    static const FName Part;             // ITEM_SPARK_PLUG
    static const FName Reservation;      // RES_ITEM_SPARK_PLUG: Player | None
    static const FName FactPlugWorn;     // diagnosis results (player knowledge)
    static const FName FactFilterOk;

    // Numbers: 60 GE and 18 GE from the source; the rest are Startwerte.
    static constexpr int32 RewardGE = 60;
    static constexpr int32 PartPriceGE = 18;
    static constexpr int32 HighPriceGE = 90;
    static constexpr int32 CustomerBudgetGE = 70;
    static constexpr int32 WithdrawAfterDay = 2;            // customer needs it back by end of day 2
    static constexpr int32 N01RepairMinutes = 60;

    /** Choices for talking to N01/N02/N03 or using the generator, given who is where. */
    static TArray<FGenesisChoice> Choices(const UGenesisWorldStateSubsystem& WS, FName Target, const FGenesisPresence& Presence);
    /** Performs one choice (ignored with a reply if it is not allowed right now). */
    static FGenesisReply Execute(UGenesisWorldStateSubsystem& WS, FName Target, FName Action, const FGenesisPresence& Presence);
    /** Time and arrival driven progress: customer inspection, N01 taking over, withdrawal. */
    static void Update(UGenesisWorldStateSubsystem& WS, const FGenesisPresence& Presence);
    /** Where the chain needs a NPC to be instead of the daily schedule (appointments). */
    static FName NpcOverrideAnchor(const UGenesisWorldStateSubsystem& WS, FName NpcID);
    static FString State(const UGenesisWorldStateSubsystem& WS);
    static bool IsTerminal(const FString& S);
    /** One-line hint for the HUD (what is open, never a forced goal). */
    static FText TaskText(const UGenesisWorldStateSubsystem& WS);
};
