#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Character/GenesisCharacterAppearance.h"
#include "GenesisCharacterRegistry.generated.h"

class USkeletalMesh;

USTRUCT(BlueprintType)
struct GENESIS_API FGenesisCharacterRegistryEntry
{
	GENERATED_BODY()

	/** Feste, nie wechselnde ID der Figur (Missionen, Dialoge, Saves verweisen nur hierauf). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Characters")
	FName CharacterAssetId;

	/** Anzeigename im Gespraech (Rolle, solange kein Name feststeht, z. B. "Werkstatt"). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Characters")
	FText DisplayName;

	/** Austauschbares Aussehen. Ein Modellwechsel aendert nur diesen Wert. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Characters")
	TSoftObjectPtr<UGenesisCharacterAppearance> Appearance;

	/** Gehoert zur Figur, nicht zum Modell: jedes kuenftige Modell muss diesen Vertrag erfuellen. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Characters")
	FGenesisProportionContract Contract;
};

/** Zentrale Zuordnung Figur-ID -> Aussehen + Vertrag (Projekteinstellungen > Genesis Characters). */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Genesis Characters"))
class GENESIS_API UGenesisCharacterRegistry : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|Characters")
	TArray<FGenesisCharacterRegistryEntry> Entries;

	static const FGenesisCharacterRegistryEntry* FindEntry(FName CharacterAssetId);

	/** Misst Hoehe und Ankerhoehe eines Meshes im Referenz-Pose. */
	static bool MeasureMesh(const USkeletalMesh* Mesh, FName AnchorBone, FGenesisMeasuredProportions& Out);

	/** Prueft ein Aussehen gegen einen Figurenvertrag. Leere Fehlerliste = darf eingesetzt werden. */
	static bool ValidateAppearance(const UGenesisCharacterAppearance* Appearance, const FGenesisProportionContract& Contract,
		TArray<FString>& OutErrors, FGenesisMeasuredProportions* OutMeasured = nullptr);
};

/** Blueprint- und Python-Zugang (z. B. fuer Import- und Pruefskripte). */
UCLASS()
class GENESIS_API UGenesisCharacterLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Genesis|Characters")
	static FGenesisMeasuredProportions MeasureSkeletalMesh(USkeletalMesh* Mesh, FName AnchorBone);

	/** Prueft ein Aussehen gegen den Vertrag der Figur CharacterAssetId. */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Characters")
	static TArray<FString> ValidateAppearanceForCharacter(UGenesisCharacterAppearance* Appearance, FName CharacterAssetId);
};
