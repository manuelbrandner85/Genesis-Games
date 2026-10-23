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

private:
    static bool ReadVerified(const FString& Path, FGenesisWorldState& OutState, FString& OutError);
};
