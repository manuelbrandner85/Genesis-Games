#include "UI/GenesisChoiceButton.h"

void UGenesisChoiceButton::Setup(int32 InIndex)
{
    Index = InIndex;
    OnClicked.AddUniqueDynamic(this, &UGenesisChoiceButton::HandleClicked);
    OnHovered.AddUniqueDynamic(this, &UGenesisChoiceButton::HandleHovered);
}

void UGenesisChoiceButton::HandleHovered()
{
    SetFocus();          // mouse and controller share one visible focus
}

void UGenesisChoiceButton::HandleClicked()
{
    OnChoice.ExecuteIfBound(Index);
}
