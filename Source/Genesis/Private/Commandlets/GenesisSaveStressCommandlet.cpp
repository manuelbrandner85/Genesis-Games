#include "GenesisSaveStressCommandlet.h"

#include "Genesis.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Save/GenesisSaveStore.h"

namespace
{
	const TCHAR* StressSlot = TEXT("Stress");

	void StampMarkers(FGenesisSaveBundle& Bundle, int64 Sequence)
	{
		// Jeder Teil traegt die Sequenz der Transaktion, in der er geschrieben wurde.
		Bundle.Soul.LivesLived = int32(Sequence);
		Bundle.World.DayOfYear = int32(Sequence % 365);
		Bundle.Life.AgeYears = float(Sequence);
	}

	bool MarkersConsistent(const FGenesisSaveBundle& Bundle)
	{
		return Bundle.Soul.LivesLived == int32(Bundle.Sequence)
			&& Bundle.World.DayOfYear == int32(Bundle.Sequence % 365)
			&& Bundle.Life.AgeYears == float(Bundle.Sequence);
	}
}

UGenesisSaveStressCommandlet::UGenesisSaveStressCommandlet()
{
	// Editor-Kontext bleibt an: Editor-Plugins wie StateTree setzen GEditor beim Laden voraus.
	LogToConsole = true;
}

int32 UGenesisSaveStressCommandlet::Main(const FString& Params)
{
	FString Mode;
	FString Dir;
	int32 Payload = 2000;
	int64 MaxSaves = MAX_int64;
	FParse::Value(*Params, TEXT("mode="), Mode);
	FParse::Value(*Params, TEXT("dir="), Dir);
	FParse::Value(*Params, TEXT("payload="), Payload);
	FParse::Value(*Params, TEXT("maxsaves="), MaxSaves);
	if (Dir.IsEmpty())
	{
		UE_LOG(LogGenesis, Error, TEXT("-dir= fehlt"));
		return 2;
	}

	FGenesisSaveStore Store(Dir);

	if (Mode == TEXT("write"))
	{
		FGenesisSaveBundle Bundle;
		if (Store.Load(StressSlot, Bundle) != EGenesisSaveResult::Ok)
		{
			Bundle = FGenesisSaveBundle();
			Bundle.Soul.SoulId = FGuid::NewGuid();
			for (int32 i = 0; i < Payload; ++i)
			{
				FGenesisMemoryRecord M;
				M.MemoryId = FName(*FString::Printf(TEXT("MEM_STRESS_%05d"), i));
				M.WorldYear = 2026 + i % 80;
				M.EmotionalWeight = float(i % 100) / 100.f;
				Bundle.Life.Memories.Add(M);
			}
		}

		bool bAnnounced = false;
		for (int64 n = 0; n < MaxSaves; ++n)
		{
			StampMarkers(Bundle, Bundle.Sequence + 1);
			const EGenesisSaveResult Result = Store.Save(StressSlot, Bundle);
			if (Result != EGenesisSaveResult::Ok)
			{
				UE_LOG(LogGenesis, Error, TEXT("Speichern fehlgeschlagen: %s"), *UEnum::GetValueAsString(Result));
				return 1;
			}
			if (!bAnnounced)
			{
				FFileHelper::SaveStringToFile(TEXT("running"), *(Store.GetDirectory() / TEXT("running.flag")));
				bAnnounced = true;
			}
		}
		return 0;
	}

	if (Mode == TEXT("verify"))
	{
		FGenesisSaveBundle Bundle;
		bool bBackup = false;
		const EGenesisSaveResult Result = Store.Load(StressSlot, Bundle, &bBackup);
		const bool bConsistent = Result == EGenesisSaveResult::Ok && MarkersConsistent(Bundle);
		const FString Line = FString::Printf(TEXT("result=%s seq=%lld backup=%d consistent=%d memories=%d"),
			*UEnum::GetValueAsString(Result), Bundle.Sequence, bBackup ? 1 : 0, bConsistent ? 1 : 0, Bundle.Life.Memories.Num());
		UE_LOG(LogGenesis, Display, TEXT("GENESIS_VERIFY %s"), *Line);
		FFileHelper::SaveStringToFile(Line, *(Store.GetDirectory() / TEXT("verify_result.txt")));
		return bConsistent ? 0 : 1;
	}

	UE_LOG(LogGenesis, Error, TEXT("-mode=write oder -mode=verify angeben"));
	return 2;
}
