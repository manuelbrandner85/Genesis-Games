#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "GameplayTagContainer.h"
#include "SmartObjectDefinition.h"
#include "GenesisNpcTypes.generated.h"

/** Ein Abschnitt im Tagesplan. Ende < Start bedeutet ueber Mitternacht (z. B. 22 bis 6 Uhr). */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisScheduleEntry
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	float StartHour = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	float EndHour = 0.f;

	/** Sleep, Work, Market, Leisure (Gameplay-Tag Genesis.Activity.<Name>). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	FName Activity;
};

USTRUCT(BlueprintType)
struct GENESIS_API FGenesisNpcSchedule
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	FName NpcId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	TArray<FGenesisScheduleEntry> Entries;
};

/** Projekteinstellungen > Genesis NPC: Tagesplaene und Wahrnehmung. */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Genesis NPC"))
class GENESIS_API UGenesisNpcSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|NPC")
	TArray<FGenesisNpcSchedule> Schedules;

	/** Was eine Figur tut, wenn ihr Plan zu dieser Stunde nichts vorsieht. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|NPC")
	FName DefaultActivity = TEXT("Leisure");

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|NPC")
	TSoftObjectPtr<class UStateTree> DailyLifeStateTree;

	/** Sichtweite bei Tageslicht (EV >= 10) und in dunkler Nacht (EV <= -3), cm; dazwischen linear. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Perception")
	float SightRangeDayCm = 4000.f;

	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Perception")
	float SightRangeNightCm = 800.f;

	/** Halber Blickwinkel in Grad (Mensch: ca. 100-110 Grad zur Seite). */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Perception")
	float HalfFieldOfViewDeg = 105.f;

	FName GetActivity(FName NpcId, float HourOfDay) const;

	static FGameplayTag ActivityTag(FName Activity);
};

/** Verhaltensdefinition eines GENESIS-Aktivitaetsplatzes (noetig, damit ein Slot als "belegt" gilt). */
UCLASS(EditInlineNew)
class GENESIS_API UGenesisActivityBehaviorDefinition : public USmartObjectBehaviorDefinition
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|NPC")
	FName Activity;
};
