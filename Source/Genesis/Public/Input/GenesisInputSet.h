#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "GenesisInputSet.generated.h"

class UInputAction;
class UInputMappingContext;

/**
 * Standardsteuerung fuer Maus/Tastatur und Controller, vollstaendig im Code definiert.
 * Spaeter koennen Spieler-Belegungen ueber Enhanced-Input-Benutzereinstellungen ueberschrieben werden.
 */
UCLASS()
class GENESIS_API UGenesisInputSet : public UObject
{
	GENERATED_BODY()

public:
	static UGenesisInputSet* CreateDefault(UObject* Outer);

	UPROPERTY()
	TObjectPtr<UInputMappingContext> Context;

	UPROPERTY()
	TObjectPtr<UInputAction> Move;

	UPROPERTY()
	TObjectPtr<UInputAction> Look;

	UPROPERTY()
	TObjectPtr<UInputAction> Jump;

	/** Gedrueckt halten: laufen statt gehen (Tastatur). */
	UPROPERTY()
	TObjectPtr<UInputAction> RunHold;

	/** Umschalten zwischen Gehen und Laufen (Controller-Stickklick). */
	UPROPERTY()
	TObjectPtr<UInputAction> RunToggle;

	/** Figur ansprechen. */
	UPROPERTY()
	TObjectPtr<UInputAction> Interact;

	/** Antwort 1-4 im Gespraech. */
	UPROPERTY()
	TArray<TObjectPtr<UInputAction>> Choices;

	/** Controller: Drehgeschwindigkeit der Kamera in Grad pro Sekunde bei vollem Ausschlag. */
	static constexpr float GamepadLookDegreesPerSecond = 160.f;

	/** Maus: Faktor auf die Engine-Mausempfindlichkeit. */
	static constexpr float MouseLookScale = 2.5f;
};
