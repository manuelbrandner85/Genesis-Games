#include "UI/GenesisHudWidget.h"
#include "UI/GenesisChoiceButton.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/World.h"

namespace
{
    const FLinearColor Dim(0.55f, 0.55f, 0.55f, 1.f);
    const FLinearColor Gold(1.f, 0.85f, 0.45f, 1.f);

    void Place(UCanvasPanelSlot* S, const FAnchors& Anchor, const FVector2D& Alignment, const FVector2D& Pos)
    {
        S->SetAnchors(Anchor);
        S->SetAlignment(Alignment);
        S->SetPosition(Pos);
        S->SetAutoSize(true);
    }
}

UTextBlock* UGenesisHudWidget::MakeText(const FString& Name, int32 Size, const FLinearColor& Color)
{
    UTextBlock* T = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), *Name);
    FSlateFontInfo Font = T->GetFont();
    Font.Size = Size;
    T->SetFont(Font);
    T->SetColorAndOpacity(FSlateColor(Color));
    T->SetShadowOffset(FVector2D(1.f, 1.f));
    T->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.8f));
    BaseSizes.Emplace(T, Size);
    return T;
}

void UGenesisHudWidget::SetTextScale(float Scale)
{
    for (const TPair<UTextBlock*, int32>& P : BaseSizes) {
        FSlateFontInfo Font = P.Key->GetFont();
        Font.Size = FMath::RoundToInt(P.Value * FMath::Clamp(Scale, 1.f, 1.5f));
        P.Key->SetFont(Font);
    }
}

void UGenesisHudWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Root"));
    WidgetTree->RootWidget = Root;

    UVerticalBox* TopLeft = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("TopLeft"));
    Clock = MakeText(TEXT("Clock"), 20);
    Money = MakeText(TEXT("Money"), 16, Gold);
    TopLeft->AddChildToVerticalBox(Clock);
    TopLeft->AddChildToVerticalBox(Money);
    Place(Root->AddChildToCanvas(TopLeft), FAnchors(0.f, 0.f), FVector2D(0.f, 0.f), FVector2D(32.f, 24.f));

    Task = MakeText(TEXT("Task"), 15);
    Place(Root->AddChildToCanvas(Task), FAnchors(1.f, 0.f), FVector2D(1.f, 0.f), FVector2D(-32.f, 24.f));

    Note = MakeText(TEXT("Note"), 16, Gold);
    Place(Root->AddChildToCanvas(Note), FAnchors(0.5f, 0.f), FVector2D(0.5f, 0.f), FVector2D(0.f, 70.f));

    Prompt = MakeText(TEXT("Prompt"), 18);
    Place(Root->AddChildToCanvas(Prompt), FAnchors(0.5f, 1.f), FVector2D(0.5f, 1.f), FVector2D(0.f, -90.f));

    DialogPanel = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("Dialog"));
    DialogPanel->SetBrushColor(FLinearColor(0.f, 0.f, 0.f, 0.62f));
    DialogPanel->SetPadding(FMargin(28.f, 18.f));
    UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("DialogColumn"));
    Speaker = MakeText(TEXT("Speaker"), 15, Gold);
    Line = MakeText(TEXT("Line"), 18);
    Line->SetAutoWrapText(true);
    Line->SetWrapTextAt(900.f);
    ChoiceBox = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("Choices"));
    Column->AddChildToVerticalBox(Speaker);
    Column->AddChildToVerticalBox(Line)->SetPadding(FMargin(0.f, 4.f, 0.f, 12.f));
    Column->AddChildToVerticalBox(ChoiceBox);
    DialogPanel->SetContent(Column);
    Place(Root->AddChildToCanvas(DialogPanel), FAnchors(0.5f, 1.f), FVector2D(0.5f, 1.f), FVector2D(0.f, -40.f));
    DialogPanel->SetVisibility(ESlateVisibility::Collapsed);
}

void UGenesisHudWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    if (const UGenesisWorldStateSubsystem* WS = GetWorld() ? GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>() : nullptr) {
        Clock->SetText(FText::FromString(WS->GetClockText()));
        Money->SetText(FText::FromString(FString::Printf(TEXT("%d GE"), WS->GetState().PlayerMoneyGE)));
        Task->SetText(FGenesisWorkshopContract::TaskText(*WS));
    }
    if (NoteTime > 0.f) {
        NoteTime -= InDeltaTime;
        if (NoteTime <= 0.f) {
            Note->SetText(FText::GetEmpty());
        }
    }
}

void UGenesisHudWidget::SetPrompt(const FText& InPrompt)
{
    Prompt->SetText(InPrompt);
}

void UGenesisHudWidget::ShowNote(const FText& InNote, float Seconds)
{
    Note->SetText(InNote);
    NoteTime = Seconds;
}

void UGenesisHudWidget::ShowDialog(const FText& InSpeaker, const FText& InLine, const TArray<FGenesisChoice>& Choices, int32 Highlight)
{
    Speaker->SetText(InSpeaker);
    Line->SetText(InLine);
    ChoiceBox->ClearChildren();
    Buttons.Reset();
    for (int32 I = 0; I <= Choices.Num(); ++I) {
        const bool bEnd = I == Choices.Num();
        const bool bEnabled = bEnd || Choices[I].bEnabled;
        FString Label = FString::Printf(TEXT("%d   %s"), I + 1, bEnd ? TEXT("Gespräch beenden") : *Choices[I].Text.ToString());
        if (!bEnabled && !Choices[I].Reason.IsEmpty()) {
            Label += FString::Printf(TEXT("   (%s)"), *Choices[I].Reason.ToString());
        }
        UGenesisChoiceButton* B = WidgetTree->ConstructWidget<UGenesisChoiceButton>(UGenesisChoiceButton::StaticClass());
        B->Setup(I);
        B->OnChoice.BindLambda([this](int32 Index) { OnChoiceClicked.ExecuteIfBound(Index); });
        B->SetBackgroundColor(I == Highlight ? FLinearColor(0.35f, 0.3f, 0.15f, 0.9f) : FLinearColor(0.f, 0.f, 0.f, 0.f));
        B->SetIsEnabled(bEnabled);
        UTextBlock* T = MakeText(FString::Printf(TEXT("ChoiceText%d"), I), 17, bEnabled ? FLinearColor::White : Dim);
        T->SetText(FText::FromString(Label));
        B->AddChild(T);
        ChoiceBox->AddChildToVerticalBox(B)->SetPadding(FMargin(0.f, 2.f));
        Buttons.Add(B);
    }
    DialogPanel->SetVisibility(ESlateVisibility::Visible);
    Prompt->SetText(FText::GetEmpty());
}

void UGenesisHudWidget::HideDialog()
{
    DialogPanel->SetVisibility(ESlateVisibility::Collapsed);
}
