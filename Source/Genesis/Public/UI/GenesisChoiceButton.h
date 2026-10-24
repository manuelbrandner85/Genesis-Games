#pragma once
#include "CoreMinimal.h"
#include "Components/Button.h"
#include "GenesisChoiceButton.generated.h"

DECLARE_DELEGATE_OneParam(FGenesisChoiceClicked, int32);

/** Button for one dialog choice; reports its index when clicked. */
UCLASS()
class GENESIS_API UGenesisChoiceButton : public UButton
{
    GENERATED_BODY()
public:
    void Setup(int32 InIndex);
    FGenesisChoiceClicked OnChoice;
private:
    UFUNCTION() void HandleClicked();
    UFUNCTION() void HandleHovered();
    int32 Index = 0;
};
