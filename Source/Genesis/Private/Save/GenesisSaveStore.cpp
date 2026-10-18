#include "Save/GenesisSaveStore.h"

#include "Genesis.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformFileManager.h"
#include "JsonObjectConverter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"

#if PLATFORM_WINDOWS
#include "Windows/AllowWindowsPlatformTypes.h"
#include <windows.h>
#include "Windows/HideWindowsPlatformTypes.h"
#endif

namespace GenesisSave
{
	static const ANSICHAR* Magic = "GENESIS_SAVE";
	static const TCHAR* MainExt = TEXT(".gsav");
	static const TCHAR* TempExt = TEXT(".gsav.tmp");
	static const TCHAR* BackupExt = TEXT(".gsav.bak");

	static FString Sha1Hex(const uint8* Data, int32 Num)
	{
		uint8 Hash[FSHA1::DigestSize];
		FSHA1::HashBuffer(Data, Num, Hash);
		return BytesToHex(Hash, FSHA1::DigestSize);
	}
}

FGenesisSaveStore::FGenesisSaveStore(const FString& InDirectory)
	: Directory(FPaths::ConvertRelativePathToFull(InDirectory))
{
}

FString FGenesisSaveStore::DefaultDirectory()
{
	return FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir() / TEXT("SaveGames") / TEXT("Genesis"));
}

FString FGenesisSaveStore::GetMainPath(const FString& Slot) const { return Directory / (Slot + GenesisSave::MainExt); }
FString FGenesisSaveStore::GetTempFilePath(const FString& Slot) const { return Directory / (Slot + GenesisSave::TempExt); }
FString FGenesisSaveStore::GetBackupPath(const FString& Slot) const { return Directory / (Slot + GenesisSave::BackupExt); }

void FGenesisSaveStore::Encode(const FGenesisSaveBundle& Bundle, TArray<uint8>& OutBytes)
{
	FString Json;
	FJsonObjectConverter::UStructToJsonObjectString(Bundle, Json, 0, 0, 0, nullptr, false);

	const FTCHARToUTF8 Payload(*Json);
	const FString Header = FString::Printf(TEXT("%hs\n%d\n%lld\n%s\n"),
		GenesisSave::Magic, Bundle.SchemaVersion, Bundle.Sequence,
		*GenesisSave::Sha1Hex(reinterpret_cast<const uint8*>(Payload.Get()), Payload.Length()));
	const FTCHARToUTF8 HeaderUtf8(*Header);

	OutBytes.Reset(HeaderUtf8.Length() + Payload.Length());
	OutBytes.Append(reinterpret_cast<const uint8*>(HeaderUtf8.Get()), HeaderUtf8.Length());
	OutBytes.Append(reinterpret_cast<const uint8*>(Payload.Get()), Payload.Length());
}

EGenesisSaveResult FGenesisSaveStore::Decode(const TArray<uint8>& Bytes, FGenesisSaveBundle& OutBundle)
{
	// Vier Kopfzeilen finden.
	int32 LineEnds[4];
	int32 Found = 0;
	for (int32 i = 0; i < Bytes.Num() && Found < 4; ++i)
	{
		if (Bytes[i] == '\n')
		{
			LineEnds[Found++] = i;
		}
	}
	if (Found < 4)
	{
		return EGenesisSaveResult::Corrupt;
	}

	auto Line = [&Bytes, &LineEnds](int32 Index) -> FString
	{
		const int32 Start = Index == 0 ? 0 : LineEnds[Index - 1] + 1;
		const FUTF8ToTCHAR Conv(reinterpret_cast<const ANSICHAR*>(Bytes.GetData() + Start), LineEnds[Index] - Start);
		return FString(Conv.Length(), Conv.Get());
	};

	if (Line(0) != ANSI_TO_TCHAR(GenesisSave::Magic))
	{
		return EGenesisSaveResult::Corrupt;
	}

	const int32 Schema = FCString::Atoi(*Line(1));
	if (Schema <= 0 || Schema > FGenesisSaveBundle::CurrentSchemaVersion)
	{
		return EGenesisSaveResult::SchemaUnsupported;
	}
	const int64 HeaderSequence = FCString::Atoi64(*Line(2));

	const int32 PayloadStart = LineEnds[3] + 1;
	const int32 PayloadLen = Bytes.Num() - PayloadStart;
	if (PayloadLen <= 0 || GenesisSave::Sha1Hex(Bytes.GetData() + PayloadStart, PayloadLen) != Line(3))
	{
		return EGenesisSaveResult::Corrupt;
	}

	const FUTF8ToTCHAR PayloadConv(reinterpret_cast<const ANSICHAR*>(Bytes.GetData() + PayloadStart), PayloadLen);
	const FString Json(PayloadConv.Length(), PayloadConv.Get());

	FGenesisSaveBundle Parsed;
	if (!FJsonObjectConverter::JsonObjectStringToUStruct(Json, &Parsed, 0, 0)
		|| Parsed.Sequence != HeaderSequence
		|| Parsed.SchemaVersion != Schema)
	{
		return EGenesisSaveResult::Corrupt;
	}

	OutBundle = MoveTemp(Parsed);
	return EGenesisSaveResult::Ok;
}

EGenesisSaveResult FGenesisSaveStore::ReadFile(const FString& Path, FGenesisSaveBundle& OutBundle)
{
	if (!IFileManager::Get().FileExists(*Path))
	{
		return EGenesisSaveResult::NotFound;
	}
	TArray<uint8> Bytes;
	if (!FFileHelper::LoadFileToArray(Bytes, *Path))
	{
		return EGenesisSaveResult::IoError;
	}
	return Decode(Bytes, OutBundle);
}

bool FGenesisSaveStore::WriteDurable(const FString& Path, const TArray<uint8>& Bytes, int32 BytesToWrite) const
{
	IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
	TUniquePtr<IFileHandle> Handle(PlatformFile.OpenWrite(*Path, false, false));
	if (!Handle)
	{
		return false;
	}
	if (!Handle->Write(Bytes.GetData(), BytesToWrite))
	{
		return false;
	}
	// Bis auf das Speichermedium durchschreiben, nicht nur in den OS-Cache.
	return Handle->Flush(true);
}

bool FGenesisSaveStore::Commit(const FString& Slot) const
{
	const FString Main = GetMainPath(Slot);
	const FString Temp = GetTempFilePath(Slot);
	const FString Backup = GetBackupPath(Slot);
	IFileManager& FileManager = IFileManager::Get();

	if (!FileManager.FileExists(*Main))
	{
#if PLATFORM_WINDOWS
		return ::MoveFileExW(*Temp, *Main, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH) != 0;
#else
		return FileManager.Move(*Main, *Temp, true);
#endif
	}

	// Die Hauptdatei ist gueltig, solange der Austausch nicht abgeschlossen ist; die alte Sicherung darf weg.
	FileManager.Delete(*Backup, false, true, true);

#if PLATFORM_WINDOWS
	// ReplaceFileW: Hauptdatei -> Sicherung, Temp -> Hauptdatei, in einem Dateisystemvorgang.
	if (::ReplaceFileW(*Main, *Temp, *Backup, REPLACEFILE_IGNORE_MERGE_ERRORS, nullptr, nullptr))
	{
		return true;
	}
	UE_LOG(LogGenesis, Error, TEXT("ReplaceFileW fehlgeschlagen (%u) fuer %s"), ::GetLastError(), *Main);
	return false;
#else
	return FileManager.Copy(*Backup, *Main) == COPY_OK && FileManager.Move(*Main, *Temp, true);
#endif
}

EGenesisSaveResult FGenesisSaveStore::Save(const FString& Slot, FGenesisSaveBundle& InOutBundle) const
{
	if (!IFileManager::Get().MakeDirectory(*Directory, true))
	{
		return EGenesisSaveResult::IoError;
	}

	FGenesisSaveBundle ToWrite = InOutBundle;
	ToWrite.SchemaVersion = FGenesisSaveBundle::CurrentSchemaVersion;
	ToWrite.Sequence = InOutBundle.Sequence + 1;
	ToWrite.SavedAtUtc = FDateTime::UtcNow();

	TArray<uint8> Bytes;
	Encode(ToWrite, Bytes);

	const FString Temp = GetTempFilePath(Slot);
	const int32 BytesToWrite = Fault == EGenesisSaveFault::TruncatedTempWrite ? Bytes.Num() / 2 : Bytes.Num();
	if (!WriteDurable(Temp, Bytes, BytesToWrite))
	{
		return EGenesisSaveResult::IoError;
	}
	if (Fault == EGenesisSaveFault::TruncatedTempWrite || Fault == EGenesisSaveFault::AbortAfterTempWrite)
	{
		return EGenesisSaveResult::IoError;
	}

	FGenesisSaveBundle Verify;
	if (ReadFile(Temp, Verify) != EGenesisSaveResult::Ok || Verify.Sequence != ToWrite.Sequence)
	{
		return EGenesisSaveResult::VerifyFailed;
	}

	if (!Commit(Slot))
	{
		return EGenesisSaveResult::IoError;
	}

	InOutBundle.Sequence = ToWrite.Sequence;
	InOutBundle.SavedAtUtc = ToWrite.SavedAtUtc;
	InOutBundle.SchemaVersion = ToWrite.SchemaVersion;
	return EGenesisSaveResult::Ok;
}

EGenesisSaveResult FGenesisSaveStore::Load(const FString& Slot, FGenesisSaveBundle& OutBundle, bool* bOutUsedBackup) const
{
	if (bOutUsedBackup)
	{
		*bOutUsedBackup = false;
	}

	const EGenesisSaveResult MainResult = ReadFile(GetMainPath(Slot), OutBundle);
	if (MainResult == EGenesisSaveResult::Ok)
	{
		return MainResult;
	}

	const EGenesisSaveResult BackupResult = ReadFile(GetBackupPath(Slot), OutBundle);
	if (BackupResult == EGenesisSaveResult::Ok)
	{
		UE_LOG(LogGenesis, Warning, TEXT("Spielstand '%s': Hauptdatei unbrauchbar, Sicherung geladen."), *Slot);
		if (bOutUsedBackup)
		{
			*bOutUsedBackup = true;
		}
		return BackupResult;
	}

	return MainResult == EGenesisSaveResult::NotFound ? BackupResult : MainResult;
}
