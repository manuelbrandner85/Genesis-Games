#pragma once
#include "CoreMinimal.h"
#include "World/GenesisWorldTypes.h"

/**
 * Transactional save file for FGenesisWorldState.
 * Write: JSON envelope {schema, sha1, state} -> <file>.tmp -> read back and verify -> old file
 * becomes <file>.bak -> .tmp replaces <file>. Load: <file>, if missing/corrupt then <file>.bak.
 * A crash at any point leaves either the old or the new complete state, never a half one.
 */
struct GENESIS_API FGenesisSaveStore
{
    static bool Save(const FString& Path, const FGenesisWorldState& State, FString& OutError);
    static bool Load(const FString& Path, FGenesisWorldState& OutState, FString& OutError, bool* bOutUsedBackup = nullptr);
    static FString SlotPath(const FString& Slot);
    /** Automation only: redirects all slots into a test folder so tests never touch player saves. */
    static FString SlotDirectoryOverride;

    /** Older schemas are upgraded on load. Schema 1 -> 2 derives soul/life/world ids from the
     *  payload hash, so loading the same old file always yields the same identity. Schema 2 -> 3
     *  marks the story start as passed (those lives began before CR-001): StoryStartStage Done,
     *  ConceptionMode Migrated, soul seed 0 before life start 1. Schema 3 -> 4: route = 1 section (W5 only),
     *  pregnancy Born (those lives were saved after the birth). */
    static void Migrate(FGenesisWorldState& State, const FString& PayloadSha1);

private:
    static bool ReadVerified(const FString& Path, FGenesisWorldState& OutState, FString& OutError);
};
