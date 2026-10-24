#include "UI/GenesisChoiceButton.h"

void UGenesisChoiceButton::Setup(int32 InIndex)
{
    Index = InIndex;
    OnClicked.AddUniqueDynamic(this, &UGenesisChoiceButton::HandleClicked);
}

void UGenesisChoiceButton::HandleClicked()
{
    OnChoice.ExecuteIfBound(Index);
}
