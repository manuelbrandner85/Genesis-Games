#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Mission/GenesisWorkshopContract.h"
#include "GenesisHudWidget.generated.h"

class UTextBlock;
class UVerticalBox;
class UBorder;
class UGenesisChoiceButton;

/**
 * Game HUD and dialog panel, built in C++ (no widget asset).
 * Top left: clock and money. Top right: open task (a hint, never a forced goal).
 * Bottom centre: interaction prompt or the dialog (speaker, line, numbered choices; disabled
 * choices are greyed out with their reason). Short notes (saved/loaded) fade after a few seconds.
 */
UCLASS()
class GENESIS_API UGenesisHudWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    void SetPrompt(const FText& Prompt);
    void ShowDialog(const FText& Speaker, const FText& Line, const TArray<FGenesisChoice>& Choices, int32 Highlight);
    void HideDialog();
    void ShowNote(const FText& Note, float Seconds = 4.f);

    /** Index of the clicked choice (Choices.Num() = "end conversation"). */
    DECLARE_DELEGATE_OneParam(FOnChoiceClicked, int32);
    FOnChoiceClicked OnChoiceClicked;

protected:
    virtual void NativeOnInitialized() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
    UTextBlock* MakeText(const FString& Name, int32 Size, const FLinearColor& Color = FLinearColor::White);
    UTextBlock* Clock = nullptr;
    UTextBlock* Money = nullptr;
    UTextBlock* Task = nullptr;
    UTextBlock* Prompt = nullptr;
    UTextBlock* Note = nullptr;
    UBorder* DialogPanel = nullptr;
    UTextBlock* Speaker = nullptr;
    UTextBlock* Line = nullptr;
    UVerticalBox* ChoiceBox = nullptr;
    UPROPERTY() TArray<TObjectPtr<UGenesisChoiceButton>> Buttons;
    float NoteTime = 0.f;
};
