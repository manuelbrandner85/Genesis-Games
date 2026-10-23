#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Time/GenesisTimeTypes.h"
#include "GenesisWorldClockSubsystem.generated.h"

/** Was beim Vorruecken der Zeit passiert ist. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisTimeAdvanceResult
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Time")
	int32 DaysChanged = 0;

	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Time")
	bool bSeasonChanged = false;

	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Time")
	EGenesisSeason NewSeason = EGenesisSeason::Winter;

	/** Alle neu erreichten Lebensabschnitte in Reihenfolge (ein Zeitraffer kann mehrere ueberspringen). */
	UPROPERTY(BlueprintReadOnly, Category = "Genesis|Time")
	TArray<EGenesisLifeStage> StagesEntered;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FGenesisLifeStageChanged, EGenesisLifeStage, OldStage, EGenesisLifeStage, NewStage);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FGenesisSeasonChanged, EGenesisSeason, NewSeason);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FGenesisDayChanged, FDateTime, NewDate);

/**
 * Weltuhr des laufenden Spiels. Der Zustand selbst (Weltzeit, Leben) liegt im Spielstand
 * (UGenesisSaveSubsystem), damit Speichern immer den aktuellen Stand erfasst.
 */
UCLASS()
class GENESIS_API UGenesisWorldClockSubsystem : public UTickableWorldSubsystem
{
	GENERATED_BODY()

public:
	/** Reine Berechnung: Zeit vorruecken, Lebensabschnitt nachfuehren, Ereignisse sammeln. */
	static FGenesisTimeAdvanceResult AdvanceTime(FGenesisSaveBundle& Bundle, const FTimespan& Delta, const UGenesisTimeSettings& Settings);

	/** Zeitraffer (z. B. zwischen Lebensabschnitten). Setzt Weltzeit und Alter fort, ueberschreibt nichts. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Time")
	FGenesisTimeAdvanceResult SkipTime(float Days);

	UFUNCTION(BlueprintCallable, Category = "Genesis|Time")
	void SetClockRunning(bool bRunning) { bClockRunning = bRunning; }

	UFUNCTION(BlueprintPure, Category = "Genesis|Time")
	bool IsClockRunning() const { return bClockRunning; }

	/** Zusaetzlicher Zeitraffer-Faktor auf die eingestellte Uhrgeschwindigkeit (1 = normal), z. B. fuer Tests. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Time")
	void SetTimeScale(float Scale) { TimeScale = FMath::Max(Scale, 0.f); }

	UFUNCTION(BlueprintPure, Category = "Genesis|Time")
	float GetTimeScale() const { return TimeScale; }

	UFUNCTION(BlueprintPure, Category = "Genesis|Time")
	FDateTime GetWorldDateTime() const;

	UFUNCTION(BlueprintPure, Category = "Genesis|Time")
	float GetTimeOfDayHours() const;

	UFUNCTION(BlueprintPure, Category = "Genesis|Time")
	EGenesisSeason GetSeason() const;

	UFUNCTION(BlueprintPure, Category = "Genesis|Time")
	float GetPlayerAgeYears() const;

	UPROPERTY(BlueprintAssignable, Category = "Genesis|Time")
	FGenesisLifeStageChanged OnLifeStageChanged;

	UPROPERTY(BlueprintAssignable, Category = "Genesis|Time")
	FGenesisSeasonChanged OnSeasonChanged;

	UPROPERTY(BlueprintAssignable, Category = "Genesis|Time")
	FGenesisDayChanged OnDayChanged;

	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;

private:
	FGenesisTimeAdvanceResult AdvanceAndBroadcast(const FTimespan& Delta);
	FGenesisSaveBundle* GetBundle() const;

	bool bClockRunning = true;

	float TimeScale = 1.f;

	/** Noch nicht uebernommene Bruchteile einer Millisekunde. */
	int64 PendingTicks = 0;
};
