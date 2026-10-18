#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "GenesisSaveStressCommandlet.generated.h"

/**
 * Absturztest fuer den Spielstand.
 *   -run=GenesisSaveStress -mode=write  -dir=<Ordner> [-payload=N] [-maxsaves=N]
 *       speichert endlos; ein externes Skript beendet den Prozess hart.
 *   -run=GenesisSaveStress -mode=verify -dir=<Ordner>
 *       laedt den Stand und prueft, dass Soul, World und Life aus derselben Transaktion stammen.
 *       Ergebnis zusaetzlich in <Ordner>/verify_result.txt.
 */
UCLASS()
class UGenesisSaveStressCommandlet : public UCommandlet
{
	GENERATED_BODY()

public:
	UGenesisSaveStressCommandlet();
	virtual int32 Main(const FString& Params) override;
};
