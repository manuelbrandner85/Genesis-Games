#pragma once
#include "CoreMinimal.h"

/**
 * Menu route graph of docs/v4_2/MENU_FLOW.json (runtime copy: Content/Genesis/Data/menu_flow.json).
 * The menu widgets only move along edges of this graph, so every screen is reachable, none is a dead
 * end and no button claims a route that does not exist.
 */
struct GENESIS_API FGenesisMenuFlow
{
    struct FNode
    {
        FString Mode;                   // system, cinematic, presentation, ui, gameplay
        TArray<FName> Edges;
        TArray<FString> Actions;
    };

    FName Initial;
    FName Current;
    TMap<FName, FNode> Nodes;

    static FString DefaultPath();
    bool LoadFromFile(const FString& Path, FString& OutError);

    /** Structural problems: unknown edge targets, nodes not reachable from Initial, nodes from which
     *  EXIT cannot be reached, nodes without way out (except EXIT). Empty = sound graph. */
    TArray<FString> Validate() const;

    bool CanGo(FName To) const;
    bool Go(FName To);
    void Reset() { Current = Initial; }
};
