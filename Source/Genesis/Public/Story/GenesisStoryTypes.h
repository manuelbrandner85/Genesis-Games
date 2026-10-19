#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Engine/DeveloperSettings.h"
#include "GenesisStoryTypes.generated.h"

/** Folge einer Antwort: ein Ereignis im Kausalgraphen und/oder ein Weltzustand (EventFlag). */
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

	/** Weltzustand setzen (World.EventFlags), leer = keiner. */
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

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Story")
	TArray<FGenesisQuestEdge> Edges;
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

	const FGenesisQuestStep* FindStep(FName StepId) const;
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

	/** Im Testlevel automatisch gestartet. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Story")
	TArray<FName> AutoStartQuestIds;

	/** Reichweite zum Ansprechen einer Figur, cm. */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Story")
	float InteractRangeCm = 250.f;

	UGenesisQuestDefinition* LoadQuest(FName QuestId) const;
};
