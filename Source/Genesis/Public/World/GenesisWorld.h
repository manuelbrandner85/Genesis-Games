#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "GameFramework/Actor.h"
#include "Save/GenesisSaveTypes.h"
#include "GenesisWorld.generated.h"

class UGenesisDialogDefinition;
class UStaticMeshComponent;

/** Ein Weltobjekt mit Zustand (Bruecke, Werkstatt, Weg, Aushang, Messstation). */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisWorldObjectDef
{
	GENERATED_BODY()

	/** Feste ID, z. B. VS01_BRIDGE_01 (Quelle) oder R05_TRAIL. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	FName ObjectId;

	/** Region der Weltbibel (R01..R08). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	FName RegionId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	FText DisplayName;

	/** Startzustand, solange der Spielstand nichts anderes belegt. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	TMap<FName, int32> InitialValues;

	/** Gespraech beim Ansehen/Benutzen, wenn keine Quest etwas anderes vorsieht. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	TSoftObjectPtr<UGenesisDialogDefinition> DefaultDialog;
};

/** Projekteinstellungen > Genesis World. */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Genesis World"))
class GENESIS_API UGenesisWorldSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|World")
	TArray<FGenesisWorldObjectDef> Objects;

	/**
	 * Ausloeser, die nicht aus einem Quest-Gespraech kommen, sondern aus der Welt (Wetter, Objekt-Gespraeche).
	 * Der Sackgassen-Pruefer akzeptiert Questkanten mit diesen Ausloesern.
	 */
	UPROPERTY(Config, EditAnywhere, Category = "Genesis|World")
	TArray<FName> WorldTriggers;

	const FGenesisWorldObjectDef* FindObject(FName ObjectId) const;
};

/**
 * Lesen und Schreiben von Weltzustand ueber einen Schluessel:
 *  "Know.<Name>"         Wissen des Spielers in diesem Leben
 *  "<ObjectId>.<Key>"    Zustandswert eines Weltobjekts (z. B. VS01_BRIDGE_01.Closed)
 *  sonst                  World.EventFlags (z. B. WX.Phase)
 * Fehlende Werte sind 0.
 */
struct GENESIS_API FGenesisWorldStateLib
{
	static bool IsWorldObjectId(FName Id);

	static const FGenesisWorldObjectState* FindObject(const FGenesisSaveBundle& Bundle, FName ObjectId);

	static int32 GetObjectValue(const FGenesisSaveBundle& Bundle, FName ObjectId, FName Key);

	/** Setzt einen Objektwert. Nur eine echte Aenderung erhoeht die Version. Liefert true bei Aenderung. */
	static bool SetObjectValue(FGenesisSaveBundle& Bundle, FName ObjectId, FName Key, int32 Value, FName EventId);

	static int32 GetValue(const FGenesisSaveBundle& Bundle, FName Key);

	static bool SetValue(FGenesisSaveBundle& Bundle, FName Key, int32 Value, FName EventId = NAME_None);
};

/**
 * Sichtbarer Teil eines Weltobjekts. Mehrere Actors koennen dieselbe ObjectId haben (Bruecke, Sperren, Schaeden).
 * Mit ShowWhenKey erscheint der Actor nur bei passendem Zustand (z. B. Sperre bei Blocked = 1) und
 * blockiert dann auch die Navigation.
 */
UCLASS()
class GENESIS_API AGenesisWorldObject : public AActor
{
	GENERATED_BODY()

public:
	AGenesisWorldObject();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	FName ObjectId;

	/** Spieler kann es ansehen/benutzen (Taste E). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	bool bInteractable = false;

	/** Leer = immer da. Sonst nur, wenn Zustand ShowWhenKey == ShowWhenValue (bzw. >= bei bShowWhenAtLeast). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	FName ShowWhenKey;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	int32 ShowWhenValue = 1;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	bool bShowWhenAtLeast = false;

	/** Sichtbar = blockiert Bewegung und Navigation (Sperre, Truemmer). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	bool bBlockingWhenShown = false;

	/** Hoehe folgt einem Weltwert in cm (z. B. Wasserspiegel WX.RiverCm); leer = fest. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|World")
	FName HeightFollowsKey;

	UStaticMeshComponent* GetVisual() const { return Visual; }

	/** Zustand aus dem Spielstand uebernehmen (wird regelmaessig aufgerufen, auch nach dem Laden). */
	UFUNCTION(BlueprintCallable, Category = "Genesis|World")
	void ApplyState();

	UFUNCTION(BlueprintPure, Category = "Genesis|World")
	bool IsShown() const { return bShown; }

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

private:
	UPROPERTY(VisibleAnywhere, Category = "Genesis|World")
	TObjectPtr<UStaticMeshComponent> Visual;

	bool bShown = true;
	bool bStateApplied = false;
	float BaseZ = 0.f;
};
