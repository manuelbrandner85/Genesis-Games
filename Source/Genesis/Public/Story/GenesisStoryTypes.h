#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Engine/DeveloperSettings.h"
#include "GenesisStoryTypes.generated.h"

/**
 * Bedingung auf Weltzustand: Wert von Key liegt in [Min, Max]. Key wie bei FGenesisWorldStateLib:
 * "Know.<Name>" (Spielerwissen), "<ObjectId>.<Wert>" (Weltobjekt) oder ein EventFlag (z. B. WX.Phase). Fehlt = 0.
 */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisStateCondition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName Key;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	int32 Min = 1;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	int32 Max = MAX_int32;
};

/** Folge einer Antwort: ein Ereignis im Kausalgraphen und/oder ein Zustandswert (EventFlag, Weltobjekt oder Spielerwissen). */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisConsequence
{
	GENERATED_BODY()

	/** Ereignistyp (Genesis Causality), leer = kein Ereignis. Handelnder ist der Spieler. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName EventType;

	/** Die angesprochene Figur ist Betroffene. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	bool bTargetSpeaker = true;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FName> ExtraTargets;

	/** Zustand setzen (Schluessel wie FGenesisStateCondition: EventFlag, "<ObjectId>.<Wert>" oder "Know.<Name>"), leer = keiner. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName FlagName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	int32 FlagValue = 1;
};

USTRUCT(BlueprintType)
struct GENESIS_API FGenesisDialogChoice
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName ChoiceId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FText Text;

	/** Naechster Knoten; leer = Gespraech endet. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName NextNodeId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FGenesisConsequence> Consequences;

	/** Ausloeser fuer den Questgraphen, leer = keiner. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName QuestTrigger;

	/** Nur waehlbar, wenn die angesprochene Figur dem Spieler mindestens so sehr vertraut. Unter -1 = immer. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	float RequiredTrust = -2.f;

	/** Nur waehlbar, wenn alle Bedingungen erfuellt sind (z. B. Know.CrackSeen). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FGenesisStateCondition> Conditions;

	bool IsUnconditional() const { return RequiredTrust < -1.f && Conditions.Num() == 0; }
};

USTRUCT(BlueprintType)
struct GENESIS_API FGenesisDialogNode
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName NodeId;

	/** Sprecher (Figuren-ID); leer = die angesprochene Figur. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName SpeakerId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FText Text;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FGenesisDialogChoice> Choices;
};

/** Ein Gespraech als Graph aus Knoten und Antworten. Entscheidungen werden erst beim Waehlen wirksam (atomar). */
UCLASS(BlueprintType)
class GENESIS_API UGenesisDialogDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName DialogId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName StartNodeId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FGenesisDialogNode> Nodes;

	/** Inhalt ist Platzhalter (nicht aus der Spielbibel). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	bool bPlaceholderContent = false;

	/** Herkunft: Quellen und Status des Wortlauts (z. B. "Arbeitstext, nicht Kanon"). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FString SourceNote;

	const FGenesisDialogNode* FindNode(FName NodeId) const;
};

/** Kante im Questgraphen: Ausloeser (+ optionale Weltbedingung) fuehrt zu Schritt oder Ausgang. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisQuestEdge
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName Trigger;

	/** Folgeschritt; leer = Quest endet mit OutcomeId. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName NextStepId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName OutcomeId;

	/** Nur wenn World.EventFlags[RequiredFlag] == RequiredFlagValue (leer = immer). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName RequiredFlag;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	int32 RequiredFlagValue = 1;

	/** Zusaetzliche Bedingungen (alle muessen gelten). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FGenesisStateCondition> Conditions;

	bool IsUnconditional() const { return RequiredFlag.IsNone() && Conditions.Num() == 0; }
};

/** Weiterer Ansprechpartner eines Questschritts: Figur oder Weltobjekt und das Gespraech, das dann startet. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisStepContact
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName TargetId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TSoftObjectPtr<UGenesisDialogDefinition> Dialog;
};

USTRUCT(BlueprintType)
struct GENESIS_API FGenesisQuestStep
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName StepId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FText Objective;

	/** Ansprechpartner (Figuren-ID) und das Gespraech, das dann startet. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName TalkToNpcId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TSoftObjectPtr<UGenesisDialogDefinition> Dialog;

	/** Weitere Ansprechpartner in diesem Schritt (der Spieler waehlt, mit wem er spricht - oder mit niemandem). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FGenesisStepContact> Contacts;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FGenesisQuestEdge> Edges;

	/** Alle Ansprechpartner (TalkToNpcId/Dialog zuerst). */
	TArray<FGenesisStepContact> GetAllContacts() const;
};

UCLASS(BlueprintType)
class GENESIS_API UGenesisQuestDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/** Feste ID, z. B. Missionsanker L08 (dann aus den Originalquellen) oder TEST_Q01 (Platzhalter). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName QuestId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FText Title;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName StartStepId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FGenesisQuestStep> Steps;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	bool bPlaceholderContent = false;

	/** Quest bietet sich an, sobald dieser Welt-Ausloeser eintritt (z. B. WX_PRECURSOR); leer = nur per StartQuest. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName StartTrigger;

	/** Herkunft: Quellen und Status (z. B. "V21 L08 + V24 Kette B/C; Wortlaut Arbeitstext"). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FString SourceNote;

	const FGenesisQuestStep* FindStep(FName StepId) const;
};

/** Quest, die in einem bestimmten Level beim Spielstart beginnt (Testlevel). */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisQuestAutoStart
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FName QuestId;

	/** Kurzname des Levels, z. B. L_GenesisTest. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	FString MapName;
};

/** Projekteinstellungen > Genesis Story. */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Genesis Story"))
class GENESIS_API UGenesisStorySettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	/** Alle Quests des Spiels (werden automatisch auf Sackgassen geprueft). */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Story")
	TArray<TSoftObjectPtr<UGenesisQuestDefinition>> Quests;

	/** Beim Spielstart im jeweiligen Level automatisch gestartet. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Story")
	TArray<FGenesisQuestAutoStart> AutoStartQuests;

	/** Reichweite zum Ansprechen einer Figur, cm. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Story")
	float InteractRangeCm = 250.f;

	UGenesisQuestDefinition* LoadQuest(FName QuestId) const;
};
