#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Story/GenesisStoryTypes.h"
#include "Save/GenesisSaveTypes.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "GenesisStory.generated.h"

struct FGenesisEventSpec;
class UGenesisCausalitySettings;

/** Questgraph und Dialoge als reine Funktionen auf dem Spielstand. */
struct GENESIS_API FGenesisStory
{
	static FGenesisQuestState* FindQuestState(FGenesisSaveBundle& Bundle, FName QuestId);
	static const FGenesisQuestState* FindQuestState(const FGenesisSaveBundle& Bundle, FName QuestId);

	/** Startet eine Quest (nicht doppelt). */
	static bool StartQuest(FGenesisSaveBundle& Bundle, const UGenesisQuestDefinition& Quest);

	static const FGenesisQuestStep* GetCurrentStep(const FGenesisSaveBundle& Bundle, const UGenesisQuestDefinition& Quest);

	/** Sind alle Bedingungen im Spielstand erfuellt? */
	static bool ConditionsMet(const FGenesisSaveBundle& Bundle, const TArray<FGenesisStateCondition>& Conditions);

	/** Ausloeser anwenden: passende Kante des aktuellen Schritts nehmen (Weltbedingung beachtet). Liefert true bei Fortschritt. */
	static bool FireTrigger(FGenesisSaveBundle& Bundle, const UGenesisQuestDefinition& Quest, FName Trigger);

	/** Antworten, die der Spieler jetzt waehlen kann (Vertrauen der Figur beachtet). */
	static TArray<const FGenesisDialogChoice*> GetAvailableChoices(const FGenesisSaveBundle& Bundle, const FGenesisDialogNode& Node, FName SpeakerId);

	/**
	 * Antwort anwenden: Weltzustand setzen, Ereignisse eintragen (ueber RecordEvent, damit die Welt Zeugen ergaenzen kann),
	 * Questausloeser liefern. Liefert den naechsten Knoten (NAME_None = Gespraechsende).
	 */
	static FName ApplyChoice(FGenesisSaveBundle& Bundle, const FGenesisDialogChoice& Choice, FName SpeakerId,
		TFunctionRef<FName(const FGenesisEventSpec&)> RecordEvent, FName& OutQuestTrigger);

	/** Sackgassen- und Logikpruefung einer Quest samt ihrer Dialoge. Leere Liste = in Ordnung. */
	static TArray<FString> ValidateQuest(const UGenesisQuestDefinition& Quest);

	static TArray<FString> ValidateDialog(const UGenesisDialogDefinition& Dialog, TSet<FName>* OutTriggers = nullptr);
};

/** Laufende Quests und das aktuelle Gespraech im Spiel. */
UCLASS()
class GENESIS_API UGenesisStorySubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Genesis|Story")
	bool StartQuest(FName QuestId);

	/**
	 * Ein Ausloeser aus der Welt (Wetter, Objekt-Gespraech): startet Quests mit diesem StartTrigger und
	 * bringt laufende Quests weiter, deren aktueller Schritt darauf wartet.
	 */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Story")
	void FireWorldTrigger(FName Trigger);

	/** Spieler spricht eine Figur an: startet das Gespraech des aktuellen Questschritts, falls es eines gibt. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Story")
	bool InteractWith(FName NpcId);

	UFUNCTION(BlueprintPure, Category = "Genesis|Story")
	bool IsInDialog() const { return ActiveDialog != nullptr; }

	UFUNCTION(BlueprintPure, Category = "Genesis|Story")
	FName GetDialogSpeaker() const;

	/** Anzeigename des Sprechers (Rolle oder Objekt), sonst die ID. */
	UFUNCTION(BlueprintPure, Category = "Genesis|Story")
	FText GetDialogSpeakerName() const;

	UFUNCTION(BlueprintPure, Category = "Genesis|Story")
	FText GetDialogText() const;

	UFUNCTION(BlueprintPure, Category = "Genesis|Story")
	TArray<FText> GetDialogChoiceTexts() const;

	/** Antwort waehlen (0-basiert, bezogen auf die verfuegbaren Antworten). */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Story")
	bool Choose(int32 Index);

	/** Aktuelles Ziel der ersten laufenden Quest (fuer das HUD). */
	UFUNCTION(BlueprintPure, Category = "Genesis|Story")
	FText GetActiveObjective() const;

private:
	FGenesisSaveBundle* GetBundle() const;
	TArray<const FGenesisDialogChoice*> AvailableChoices() const;

	UPROPERTY(Transient)
	TObjectPtr<UGenesisDialogDefinition> ActiveDialog;

	UPROPERTY(Transient)
	TObjectPtr<UGenesisQuestDefinition> ActiveDialogQuest;

	FName ActiveNodeId;
	FName ActiveSpeakerId;
};

/** Platzhalter-HUD: Gespraech mit nummerierten Antworten und aktuelles Ziel. Keine Werte (kein Karma, kein Vertrauen). */
UCLASS()
class GENESIS_API AGenesisHUD : public AHUD
{
	GENERATED_BODY()

public:
	virtual void DrawHUD() override;
};

/** Blueprint- und Python-Zugang zur Story-Pruefung (z. B. direkt nach dem Bauen einer Quest). */
UCLASS()
class GENESIS_API UGenesisStoryLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Genesis|Story")
	static TArray<FString> ValidateQuest(UGenesisQuestDefinition* Quest);
};
