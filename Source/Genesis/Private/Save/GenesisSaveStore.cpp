#include "Save/GenesisSaveStore.h"
#include "HAL/FileManager.h"
#include "JsonObjectConverter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
    FString Sha1Hex(const FString& Text)
    {
        const FTCHARToUTF8 Utf8(*Text);
        FSHAHash Hash;
        FSHA1::HashBuffer(Utf8.Get(), Utf8.Length(), Hash.Hash);
        return Hash.ToString();
    }
}

FString FGenesisSaveStore::SlotPath(const FString& Slot)
{
    return FPaths::ProjectSavedDir() / TEXT("SaveGames") / (Slot + TEXT(".genesis.json"));
}

bool FGenesisSaveStore::Save(const FString& Path, const FGenesisWorldState& State, FString& OutError)
{
    FString Payload;
    if (!FJsonObjectConverter::UStructToJsonObjectString(State, Payload, 0, 0, 0, nullptr, false)) {
        OutError = TEXT("serialise failed");
        return false;
    }
    const FString Envelope = FString::Printf(TEXT("{\"schema\":%d,\"sha1\":\"%s\",\"state\":%s}"),
        State.SchemaVersion, *Sha1Hex(Payload), *Payload);
    const FString Tmp = Path + TEXT(".tmp");
    const FString Bak = Path + TEXT(".bak");
    IFileManager& FM = IFileManager::Get();
    FM.MakeDirectory(*FPaths::GetPath(Path), true);
    if (!FFileHelper::SaveStringToFile(Envelope, *Tmp, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM)) {
        OutError = TEXT("write temp failed");
        return false;
    }
    FGenesisWorldState Check;
    if (!ReadVerified(Tmp, Check, OutError)) {
        OutError = TEXT("temp verify failed: ") + OutError;
        FM.Delete(*Tmp);
        return false;
    }
    if (FM.FileExists(*Path)) {
        // Only a verified main file may become the backup; a damaged one must never overwrite a
        // good backup. It is kept aside as .corrupt for diagnosis.
        FGenesisWorldState Current;
        FString CurrentError;
        const bool bMainValid = ReadVerified(Path, Current, CurrentError);
        if (!FM.Move(bMainValid ? *Bak : *(Path + TEXT(".corrupt")), *Path, true, true)) {
            OutError = TEXT("backup move failed");
            return false;
        }
    }
    if (!FM.Move(*Path, *Tmp, true, true)) {
        OutError = TEXT("final move failed");
        return false;
    }
    return true;
}

bool FGenesisSaveStore::ReadVerified(const FString& Path, FGenesisWorldState& OutState, FString& OutError)
{
    FString Text;
    if (!FFileHelper::LoadFileToString(Text, *Path)) {
        OutError = TEXT("missing");
        return false;
    }
    TSharedPtr<FJsonObject> Root;
    if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text), Root) || !Root.IsValid()) {
        OutError = TEXT("not json");
        return false;
    }
    const int32 Schema = Root->GetIntegerField(TEXT("schema"));
    if (Schema > FGenesisWorldState::CurrentSchema) {
        OutError = FString::Printf(TEXT("schema %d is newer than this build (%d)"), Schema, FGenesisWorldState::CurrentSchema);
        return false;
    }
    // Re-extract the exact payload text the hash was computed over.
    const int32 Start = Text.Find(TEXT("\"state\":"));
    if (Start == INDEX_NONE || !Text.EndsWith(TEXT("}"))) {
        OutError = TEXT("no state");
        return false;
    }
    const FString Payload = Text.Mid(Start + 8, Text.Len() - Start - 9);
    if (Sha1Hex(Payload) != Root->GetStringField(TEXT("sha1"))) {
        OutError = TEXT("checksum mismatch");
        return false;
    }
    FGenesisWorldState Loaded;
    if (!FJsonObjectConverter::JsonObjectStringToUStruct(Payload, &Loaded, 0, 0)) {
        OutError = TEXT("state does not match schema");
        return false;
    }
    OutState = MoveTemp(Loaded);
    return true;
}

bool FGenesisSaveStore::Load(const FString& Path, FGenesisWorldState& OutState, FString& OutError, bool* bOutUsedBackup)
{
    if (bOutUsedBackup) {
        *bOutUsedBackup = false;
    }
    FString MainError;
    if (ReadVerified(Path, OutState, MainError)) {
        return true;
    }
    FString BakError;
    if (ReadVerified(Path + TEXT(".bak"), OutState, BakError)) {
        if (bOutUsedBackup) {
            *bOutUsedBackup = true;
        }
        UE_LOG(LogTemp, Warning, TEXT("Genesis save: main file unusable (%s), loaded backup"), *MainError);
        return true;
    }
    OutError = FString::Printf(TEXT("main: %s, backup: %s"), *MainError, *BakError);
    return false;
}
