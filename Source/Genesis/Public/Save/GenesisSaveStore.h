#pragma once

#include "CoreMinimal.h"
#include "Save/GenesisSaveTypes.h"

/** Nur fuer Tests: simuliert einen Absturz an einer bestimmten Stelle des Speicherns. */
enum class EGenesisSaveFault : uint8
{
	None,
	/** Temp-Datei vollstaendig geschrieben, Prozess "stirbt" vor dem Austausch. */
	AbortAfterTempWrite,
	/** Prozess "stirbt" mitten im Schreiben der Temp-Datei. */
	TruncatedTempWrite
};

/**
 * Transaktionaler Speicher fuer FGenesisSaveBundle.
 *
 * Dateiformat (<Slot>.gsav):
 *   GENESIS_SAVE\n<Schema>\n<Sequence>\n<SHA1 der Nutzdaten>\n<JSON-Nutzdaten>
 *
 * Ablauf beim Speichern:
 *   1. Nutzdaten in <Slot>.gsav.tmp schreiben und auf Platte flushen
 *   2. Temp-Datei zuruecklesen und Pruefsumme verifizieren
 *   3. Atomarer Austausch: alte <Slot>.gsav wird zu <Slot>.gsav.bak, Temp wird zu <Slot>.gsav
 * Beim Laden wird zuerst die Hauptdatei, bei Defekt die Sicherung verwendet; .tmp wird nie geladen.
 */
class GENESIS_API FGenesisSaveStore
{
public:
	explicit FGenesisSaveStore(const FString& InDirectory);

	/** Speichert das Bundle. Bei Erfolg wird InOutBundle.Sequence/SavedAtUtc auf den geschriebenen Stand gesetzt. */
	EGenesisSaveResult Save(const FString& Slot, FGenesisSaveBundle& InOutBundle) const;

	/** Laedt den letzten vollstaendig geschriebenen Stand. */
	EGenesisSaveResult Load(const FString& Slot, FGenesisSaveBundle& OutBundle, bool* bOutUsedBackup = nullptr) const;

	FString GetMainPath(const FString& Slot) const;
	FString GetTempFilePath(const FString& Slot) const;
	FString GetBackupPath(const FString& Slot) const;
	const FString& GetDirectory() const { return Directory; }

	void SetFaultForTesting(EGenesisSaveFault InFault) { Fault = InFault; }

	static void Encode(const FGenesisSaveBundle& Bundle, TArray<uint8>& OutBytes);
	/** Schreibt beliebige JSON-Nutzdaten mit Kopf und Pruefsumme (z. B. fuer Migrationstests alter Schemata). */
	static void EncodeRaw(int32 SchemaVersion, int64 Sequence, const FString& Json, TArray<uint8>& OutBytes);
	static EGenesisSaveResult Decode(const TArray<uint8>& Bytes, FGenesisSaveBundle& OutBundle);
	static EGenesisSaveResult ReadFile(const FString& Path, FGenesisSaveBundle& OutBundle);

	/** Standardordner: Saved/SaveGames/Genesis */
	static FString DefaultDirectory();

private:
	bool WriteDurable(const FString& Path, const TArray<uint8>& Bytes, int32 BytesToWrite) const;
	bool Commit(const FString& Slot) const;

	FString Directory;
	EGenesisSaveFault Fault = EGenesisSaveFault::None;
};
