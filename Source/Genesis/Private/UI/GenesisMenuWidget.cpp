#include "UI/GenesisMenuWidget.h"
#include "UI/GenesisChoiceButton.h"
#include "UI/GenesisUserSettings.h"
#include "Cinematic/GenesisCinematicSubsystem.h"
#include "Cinematic/GenesisLightStrike.h"
#include "GenesisGameInstance.h"
#include "Player/GenesisPlayerController.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/ButtonSlot.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/ScrollBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Kismet/KismetSystemLibrary.h"

namespace
{
    const FLinearColor Accent(0.93f, 0.78f, 0.45f, 1.f);
    const FLinearColor MenuDim(0.55f, 0.55f, 0.55f, 1.f);
    const FLinearColor Ink(0.06f, 0.05f, 0.04f, 1.f);

    struct FBootPage { const TCHAR* Title; const TCHAR* Body; float Seconds; };
    const FBootPage BootPages[] = {
        { TEXT("Technischer Vorabstand"), TEXT("GENESIS ist in Entwicklung. Grafik, Ton und Inhalte sind unfertig."), 3.f },
        { TEXT("Erstellt mit Unreal Engine"), TEXT(""), 3.f },
        { TEXT("Gesundheitshinweis"),
          TEXT("Bei einem sehr kleinen Teil der Menschen können Lichtblitze, Muster oder schnelle Bildwechsel epileptische Anfälle auslösen – auch ohne bekannte Vorgeschichte.\n"
               "Treten Schwindel, Seh- oder Muskelstörungen auf, unterbrich das Spiel sofort und wende dich an eine Ärztin oder einen Arzt.\n"
               "Blitze und Kamerawackeln lassen sich unter „Barrierefreiheit“ verringern."), 6.f },
        { TEXT("Lautstärke"), TEXT("Sprache, Musik und Effekte lassen sich unter „Einstellungen“ jederzeit getrennt regeln."), 3.5f },
    };

    void PlaceInCanvas(UCanvasPanelSlot* S, const FAnchors& Anchor, const FVector2D& Alignment, const FVector2D& Pos, const FVector2D* Size = nullptr)
    {
        S->SetAnchors(Anchor);
        S->SetAlignment(Alignment);
        S->SetPosition(Pos);
        if (Size) {
            S->SetSize(*Size);
        }
        else {
            S->SetAutoSize(true);
        }
    }

    FName NodeOf(EGenesisMenuScreen S)
    {
        switch (S) {
        case EGenesisMenuScreen::Boot:           return TEXT("BOOT");
        case EGenesisMenuScreen::Title:          return TEXT("TITLE_CARD");
        case EGenesisMenuScreen::Main:           return TEXT("MAIN_MENU");
        case EGenesisMenuScreen::NewGame:
        case EGenesisMenuScreen::NewGameConfirm: return TEXT("NEW_GAME");
        case EGenesisMenuScreen::Load:           return TEXT("LOAD_GAME");
        case EGenesisMenuScreen::Settings:       return TEXT("SETTINGS");
        case EGenesisMenuScreen::Accessibility:  return TEXT("ACCESSIBILITY");
        case EGenesisMenuScreen::Credits:        return TEXT("CREDITS");
        case EGenesisMenuScreen::QuitConfirm:    return TEXT("QUIT");
        case EGenesisMenuScreen::Pause:
        case EGenesisMenuScreen::MainMenuConfirm: return TEXT("PAUSE_MENU");
        case EGenesisMenuScreen::StoryStart:     return TEXT("STORY_START");
        case EGenesisMenuScreen::ChapterCard:    return TEXT("CHAPTER_CARD");
        default:                                 return NAME_None;
        }
    }

    FString OnOff(bool b) { return b ? TEXT("An") : TEXT("Aus"); }
}

int32 UGenesisMenuWidget::Scaled(int32 Size) const
{
    const UGenesisUserSettings* U = UGenesisUserSettings::Get();
    return FMath::RoundToInt(Size * (U ? FMath::Clamp(U->TextScale, 1.f, 1.5f) : 1.f));
}

UTextBlock* UGenesisMenuWidget::MakeText(const FString& Name, int32 Size, const FLinearColor& Color)
{
    UTextBlock* T = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), Name.IsEmpty() ? NAME_None : FName(*Name));
    FSlateFontInfo Font = T->GetFont();
    Font.Size = Size;
    T->SetFont(Font);
    T->SetColorAndOpacity(FSlateColor(Color));
    T->SetShadowOffset(FVector2D(1.f, 1.f));
    T->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.7f));
    return T;
}

void UGenesisMenuWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    SetIsFocusable(true);
    FString Error;
    if (!Flow.LoadFromFile(FGenesisMenuFlow::DefaultPath(), Error)) {
        UE_LOG(LogTemp, Error, TEXT("Genesis menu: menu flow not loaded: %s"), *Error);
    }

    Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Root"));
    WidgetTree->RootWidget = Root;

    Shade = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("Shade"));
    Shade->SetBrushColor(FLinearColor(0.f, 0.f, 0.f, 1.f));
    UCanvasPanelSlot* ShadeSlot = Root->AddChildToCanvas(Shade);
    ShadeSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
    ShadeSlot->SetOffsets(FMargin(0.f));

    Center = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("Center"));
    BigTitle = MakeText(TEXT("BigTitle"), 64);
    BigSub = MakeText(TEXT("BigSub"), 18, FLinearColor(0.85f, 0.85f, 0.85f, 1.f));
    BigSub->SetAutoWrapText(true);
    BigSub->SetWrapTextAt(900.f);
    BigTitle->SetJustification(ETextJustify::Center);
    BigSub->SetJustification(ETextJustify::Center);
    Center->AddChildToVerticalBox(BigTitle)->SetHorizontalAlignment(HAlign_Center);
    Center->AddChildToVerticalBox(BigSub)->SetPadding(FMargin(0.f, 18.f, 0.f, 0.f));
    Press = MakeText(TEXT("Press"), 17, FLinearColor(0.85f, 0.85f, 0.85f, 1.f));
    Press->SetJustification(ETextJustify::Center);
    Center->AddChildToVerticalBox(Press)->SetPadding(FMargin(0.f, 64.f, 0.f, 0.f));
    PlaceInCanvas(Root->AddChildToCanvas(Center), FAnchors(0.5f, 0.5f), FVector2D(0.5f, 0.5f), FVector2D(0.f, 0.f));

    // C01 light strike: a round point of light, then the full-screen white (FGenesisLightStrike).
    FSlateBrush Round;
    Round.DrawAs = ESlateBrushDrawType::RoundedBox;
    Round.OutlineSettings.RoundingType = ESlateBrushRoundingType::HalfHeightRadius;
    LightPoint = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("LightPoint"));
    LightPoint->SetBrush(Round);
    LightPoint->SetBrushColor(FGenesisLightStrike::Color());
    LightPoint->SetVisibility(ESlateVisibility::Collapsed);
    const FVector2D NoSize(0.f, 0.f);
    PlaceInCanvas(Root->AddChildToCanvas(LightPoint), FAnchors(0.5f, 0.5f), FVector2D(0.5f, 0.5f), FVector2D(0.f, 0.f), &NoSize);
    Flash = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("Flash"));
    Flash->SetBrushColor(FGenesisLightStrike::Color());
    Flash->SetVisibility(ESlateVisibility::Collapsed);
    UCanvasPanelSlot* FlashSlot = Root->AddChildToCanvas(Flash);
    FlashSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
    FlashSlot->SetOffsets(FMargin(0.f));

    // Left column: dark glass panel with header, info line and the focusable entries.
    Panel = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("Panel"));
    Panel->SetBrushColor(FLinearColor(0.01f, 0.01f, 0.012f, 0.72f));
    Panel->SetPadding(FMargin(64.f, 72.f, 48.f, 48.f));
    UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("Column"));
    Header = MakeText(TEXT("Header"), 40, Accent);
    Info = MakeText(TEXT("Info"), 16, FLinearColor(0.82f, 0.82f, 0.82f, 1.f));
    Info->SetAutoWrapText(true);
    Info->SetWrapTextAt(560.f);
    Scroll = WidgetTree->ConstructWidget<UScrollBox>(UScrollBox::StaticClass(), TEXT("Scroll"));
    ButtonBox = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("Buttons"));
    Scroll->AddChild(ButtonBox);
    Column->AddChildToVerticalBox(Header);
    Column->AddChildToVerticalBox(Info)->SetPadding(FMargin(0.f, 10.f, 0.f, 26.f));
    UVerticalBoxSlot* ScrollSlot = Column->AddChildToVerticalBox(Scroll);
    ScrollSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
    Footer = MakeText(TEXT("Footer"), 13, MenuDim);
    Footer->SetAutoWrapText(true);
    Footer->SetWrapTextAt(560.f);
    Column->AddChildToVerticalBox(Footer)->SetPadding(FMargin(0.f, 18.f, 0.f, 0.f));
    Panel->SetContent(Column);
    UCanvasPanelSlot* PanelSlot = Root->AddChildToCanvas(Panel);
    PanelSlot->SetAnchors(FAnchors(0.f, 0.f, 0.f, 1.f));
    PanelSlot->SetOffsets(FMargin(0.f, 0.f, 680.f, 0.f));
}

void UGenesisMenuWidget::StartMainMenu(bool bSkipBoot)
{
    bInGame = false;
    ReturnScreen = EGenesisMenuScreen::Main;
    Flow.Reset();
    if (bSkipBoot) {
        Flow.Current = TEXT("TITLE_CARD");       // back from the game: boot and title were seen in this session
        ShowScreen(EGenesisMenuScreen::Main);
    }
    else {
        BootPage = 0;
        Screen = EGenesisMenuScreen::Boot;
        Rebuild();
    }
}

void UGenesisMenuWidget::StartPauseMenu(bool bStoryStart)
{
    bInGame = true;
    bStoryPause = bStoryStart;
    ReturnScreen = EGenesisMenuScreen::Pause;
    Flow.Current = bStoryStart ? TEXT("STORY_SWIM") : TEXT("IN_GAME");
    ShowScreen(EGenesisMenuScreen::Pause);
}

UGenesisGameInstance* UGenesisMenuWidget::GetGenesisGI() const
{
    return Cast<UGenesisGameInstance>(GetGameInstance());
}

void UGenesisMenuWidget::ResumeStoryStart()
{
    bInGame = false;
    ReturnScreen = EGenesisMenuScreen::Main;
    Flow.Reset();
    Flow.Current = TEXT("STORY_SWIM");          // back from the swim map
    ShowScreen(EGenesisMenuScreen::StoryStart);
}

float UGenesisMenuWidget::StoryPartSeconds() const
{
    const UGenesisGameInstance* GI = GetGenesisGI();
    const UGenesisUserSettings* U = UGenesisUserSettings::Get();
    switch (GI ? GI->StoryStart.Step : EGenesisStoryStep::NotStarted) {
    case EGenesisStoryStep::C00:     return 6.f;        // placeholder until the C00 master exists
    case EGenesisStoryStep::C01:     return FGenesisLightStrike::Duration(!U || U->bReduceFlashes);
    case EGenesisStoryStep::C02Film: return 4.f;
    case EGenesisStoryStep::C02End:  return 5.f;
    default:                         return 0.f;
    }
}

float UGenesisMenuWidget::GetFlashLevel() const
{
    const UGenesisGameInstance* GI = GetGenesisGI();
    if (Screen != EGenesisMenuScreen::StoryStart || !GI || GI->StoryStart.Step != EGenesisStoryStep::C01) {
        return 0.f;
    }
    const UGenesisUserSettings* U = UGenesisUserSettings::Get();
    return FGenesisLightStrike::WhiteLevel(ScreenTime, !U || U->bReduceFlashes);
}

void UGenesisMenuWidget::FinishStoryPart(bool bSkipped)
{
    UGenesisGameInstance* GI = GetGenesisGI();
    UGenesisCinematicSubsystem* Cine = GI ? GI->GetSubsystem<UGenesisCinematicSubsystem>() : nullptr;
    if (!Cine || !GI->StoryStart.FinishFilm(*Cine, bSkipped)) {
        return;
    }
    ConfirmSkipUntil = -1.f;
    switch (GI->StoryStart.Step) {
    case EGenesisStoryStep::C02Swim:
        if (!bSwimRequested && Flow.Go(TEXT("STORY_SWIM"))) {
            bSwimRequested = true;
            GI->EnterSwim();
        }
        break;
    case EGenesisStoryStep::Title:
        ShowScreen(GI->bStoryStartForNewLife ? EGenesisMenuScreen::ChapterCard : EGenesisMenuScreen::Title);
        break;
    default:
        ScreenTime = 0.f;
        Rebuild();
        break;
    }
}

void UGenesisMenuWidget::StoryKey()
{
    const UGenesisGameInstance* GI = GetGenesisGI();
    if (Screen != EGenesisMenuScreen::StoryStart || !GI || !GI->StoryStart.CanSkip()) {
        return;
    }
    if (GI->StoryStart.NeedsSkipConfirmation() && !IsSkipConfirmPending()) {
        ConfirmSkipUntil = ScreenTime + 3.f;     // C00: a single accidental press never skips the prologue
        Rebuild();
        return;
    }
    FinishStoryPart(true);
}

void UGenesisMenuWidget::StoryStartTick()
{
    const UGenesisGameInstance* GI = GetGenesisGI();
    if (!GI || !GI->StoryStart.IsFilmPart()) {
        return;
    }
    const float Level = GetFlashLevel();
    const bool bC01 = GI->StoryStart.Step == EGenesisStoryStep::C01;
    Flash->SetVisibility(bC01 && Level > 0.f ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
    Flash->SetRenderOpacity(Level);
    const bool bPoint = bC01 && ScreenTime < FGenesisLightStrike::PointSeconds + 0.3f;
    LightPoint->SetVisibility(bPoint ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
    if (bPoint) {
        const float Size = FMath::Max(2.f, FGenesisLightStrike::PointSize(ScreenTime) * 1080.f);
        if (UCanvasPanelSlot* S = Cast<UCanvasPanelSlot>(LightPoint->Slot)) {
            S->SetSize(FVector2D(Size, Size));
        }
    }
    if (ConfirmSkipUntil > 0.f && ScreenTime > ConfirmSkipUntil) {
        ConfirmSkipUntil = -1.f;
        Rebuild();
    }
    if (ScreenTime > StoryPartSeconds()) {
        FinishStoryPart(false);
    }
}

void UGenesisMenuWidget::ChooseNewGameSlot(const FString& SaveSlotName)
{
    UGenesisGameInstance* GI = GetGenesisGI();
    if (!GI) {
        return;
    }
    PendingSlot = SaveSlotName;
    if (GI->HasCompletedStoryLife()) {
        ShowScreen(EGenesisMenuScreen::ChapterCard);       // the life of this session's story start
    }
    else if (Flow.CanGo(TEXT("STORY_START")) && GI->BeginStoryStart(true, SaveSlotName)) {
        ShowScreen(EGenesisMenuScreen::StoryStart);        // every life begins with C00-C02
    }
}

bool UGenesisMenuWidget::ShowScreen(EGenesisMenuScreen NewScreen)
{
    const FName Node = NodeOf(NewScreen);
    if (Node != Flow.Current && !Flow.Go(Node)) {
        LastFlowError = FString::Printf(TEXT("no menu route %s -> %s"), *Flow.Current.ToString(), *Node.ToString());
        UE_LOG(LogTemp, Error, TEXT("Genesis menu: %s"), *LastFlowError);
        return false;
    }
    if (NewScreen != Screen) {
        InfoText.Reset();
        LastFocused = 0;
    }
    Screen = NewScreen;
    ScreenTime = 0.f;
    Rebuild();
    return true;
}

void UGenesisMenuWidget::AdvanceIntro()
{
    if (Screen == EGenesisMenuScreen::Boot) {
        if (++BootPage < UE_ARRAY_COUNT(BootPages)) {
            ScreenTime = 0.f;
            Rebuild();
            return;
        }
        // CR-001 (ScriptLock 1.2): the first start - no valid save yet - begins with the story
        // start C00 -> C01 -> C02 (swim), the title follows after C02 (E1). A returning player goes
        // to the title card; a new life from the menu plays the story start there.
        UGenesisGameInstance* GI = GetGenesisGI();
        if (GI) {
            GI->bBootSequenceShown = true;
        }
        if (GI && UGenesisGameInstance::MostRecentSlot().IsEmpty() && GI->BeginStoryStart(false)) {
            ShowScreen(EGenesisMenuScreen::StoryStart);
            return;
        }
        ShowScreen(EGenesisMenuScreen::Title);
    }
    else if (Screen == EGenesisMenuScreen::Title) {
        if (UGenesisGameInstance* GI = GetGenesisGI()) {
            GI->StoryStart.Complete();
        }
        ShowScreen(EGenesisMenuScreen::Main);
    }
    else if (Screen == EGenesisMenuScreen::ChapterCard && ScreenTime > 0.5f) {
        UGenesisGameInstance* GI = GetGenesisGI();
        if (GI && Flow.Go(TEXT("IN_GAME"))) {
            GI->StoryStart.Complete();
            GI->StartNewGame(PendingSlot.IsEmpty() ? GI->StoryStartSlot : PendingSlot);
        }
    }
    else if (Screen == EGenesisMenuScreen::StoryStart) {
        StoryKey();
    }
}

void UGenesisMenuWidget::Back()
{
    switch (Screen) {
    case EGenesisMenuScreen::Boot:
    case EGenesisMenuScreen::Title:
    case EGenesisMenuScreen::ChapterCard:
    case EGenesisMenuScreen::StoryStart:     AdvanceIntro(); break;
    case EGenesisMenuScreen::Main:           ShowScreen(EGenesisMenuScreen::QuitConfirm); break;
    case EGenesisMenuScreen::NewGameConfirm: Screen = EGenesisMenuScreen::NewGame; LastFocused = 0; Rebuild(); break;
    case EGenesisMenuScreen::QuitConfirm:    ShowScreen(EGenesisMenuScreen::Main); break;
    case EGenesisMenuScreen::Pause:          Resume(); break;
    case EGenesisMenuScreen::MainMenuConfirm: Screen = EGenesisMenuScreen::Pause; LastFocused = 0; Rebuild(); break;
    case EGenesisMenuScreen::Settings:
    case EGenesisMenuScreen::Accessibility:
        if (UGenesisUserSettings* U = UGenesisUserSettings::Get()) {
            U->SaveSettings();
        }
        ShowScreen(ReturnScreen);
        break;
    default:                                 ShowScreen(ReturnScreen); break;
    }
}

void UGenesisMenuWidget::Resume()
{
    if (Flow.Go(bStoryPause ? TEXT("STORY_SWIM") : TEXT("IN_GAME"))) {
        OnResume.ExecuteIfBound();
    }
}

FString UGenesisMenuWidget::SlotLabel(const FString& SaveSlotName, bool bForNewGame) const
{
    const FGenesisSlotInfo I = UGenesisGameInstance::DescribeSlot(SaveSlotName);
    const FString Name = FString::Printf(TEXT("Spielstand %s"), *SaveSlotName.RightChop(4));
    if (!I.bExists) {
        return Name + TEXT(" – leer");
    }
    if (!I.bValid) {
        return Name + TEXT(" – beschädigt") + (bForNewGame ? TEXT(" (wird überschrieben)") : TEXT(""));
    }
    return FString::Printf(TEXT("%s – Tag %d, %02d:%02d · %d GE · %s%s"), *Name, I.Day, I.Hour, I.Minute, I.MoneyGE,
        *I.SavedAt.ToString(TEXT("%d.%m.%Y %H:%M")), I.bFromBackup ? TEXT(" (Sicherung)") : TEXT(""));
}

void UGenesisMenuWidget::AddButton(const FString& Label, TFunction<void()> Activate, bool bEnabled)
{
    FEntry E;
    E.Label = [Label]() { return Label; };
    E.Activate = MoveTemp(Activate);
    E.bEnabled = bEnabled;
    Entries.Add(MoveTemp(E));
}

void UGenesisMenuWidget::AddCycle(const FString& Label, TFunction<int32()> Get, TFunction<void(int32)> Set, const TArray<FString>& Names)
{
    FEntry E;
    E.Label = [Label, Get, Names]() {
        const int32 V = Get();
        return FString::Printf(TEXT("%s:  ‹ %s ›"), *Label, Names.IsValidIndex(V) ? *Names[V] : TEXT("Benutzerdefiniert"));
    };
    E.Adjust = [Get, Set, Count = Names.Num()](int32 Dir) { Set(FMath::Clamp(FMath::Max(Get(), 0) + Dir, 0, Count - 1)); };
    E.Activate = [Get, Set, Count = Names.Num()]() { Set((FMath::Max(Get(), 0) + 1) % Count); };
    Entries.Add(MoveTemp(E));
}

void UGenesisMenuWidget::AddPercent(const FString& Label, float* Value, float Min, float Max, float Step)
{
    FEntry E;
    E.Label = [Label, Value]() { return FString::Printf(TEXT("%s:  ‹ %d %% ›"), *Label, FMath::RoundToInt(*Value * 100.f)); };
    E.Adjust = [this, Value, Min, Max, Step](int32 Dir) {
        *Value = FMath::Clamp(FMath::RoundToFloat((*Value + Dir * Step) / Step) * Step, Min, Max);
        SettingsChanged(false);
    };
    E.Activate = [this, Value, Min, Max, Step]() {
        *Value = *Value + Step > Max + KINDA_SMALL_NUMBER ? Min : FMath::RoundToFloat((*Value + Step) / Step) * Step;
        SettingsChanged(false);
    };
    Entries.Add(MoveTemp(E));
}

void UGenesisMenuWidget::AddToggle(const FString& Label, bool* Value)
{
    FEntry E;
    E.Label = [Label, Value]() { return FString::Printf(TEXT("%s:  ‹ %s ›"), *Label, *OnOff(*Value)); };
    E.Adjust = [this, Value](int32) { *Value = !*Value; SettingsChanged(false); };
    E.Activate = [this, Value]() { *Value = !*Value; SettingsChanged(false); };
    Entries.Add(MoveTemp(E));
}

void UGenesisMenuWidget::SettingsChanged(bool bEngineSettings)
{
    UGenesisUserSettings* U = UGenesisUserSettings::Get();
    if (!U) {
        return;
    }
    if (bEngineSettings) {
        U->ApplySettings(false);
    }
    U->ApplyGenesisOptions(this);
}

void UGenesisMenuWidget::BuildEntries()
{
    Entries.Reset();
    UGenesisGameInstance* GI = Cast<UGenesisGameInstance>(GetGameInstance());
    UGenesisUserSettings* U = UGenesisUserSettings::Get();
    FString Title;
    FString Hint;

    switch (Screen) {
    case EGenesisMenuScreen::Main: {
        Title = TEXT("GENESIS");
        const FString Recent = UGenesisGameInstance::MostRecentSlot();     // check_save_integrity
        if (!Recent.IsEmpty()) {
            AddButton(TEXT("Fortsetzen"), [this, GI, Recent]() {
                if (!Flow.Go(TEXT("CONTINUE"))) {
                    return;
                }
                if (UGenesisGameInstance::DescribeSlot(Recent).bValid && GI && Flow.Go(TEXT("IN_GAME"))) {
                    GI->LoadSlotAndPlay(Recent);
                }
                else {
                    Flow.Go(TEXT("MAIN_MENU"));
                    InfoText = TEXT("Der Spielstand ist nicht mehr lesbar.");
                    Rebuild();
                }
            });
        }
        AddButton(TEXT("Neues Leben"), [this]() { ShowScreen(EGenesisMenuScreen::NewGame); });
        AddButton(TEXT("Laden"), [this]() { ShowScreen(EGenesisMenuScreen::Load); });
        AddButton(TEXT("Einstellungen"), [this]() { ShowScreen(EGenesisMenuScreen::Settings); });
        AddButton(TEXT("Barrierefreiheit"), [this]() { ShowScreen(EGenesisMenuScreen::Accessibility); });
        AddButton(TEXT("Mitwirkende"), [this]() { ShowScreen(EGenesisMenuScreen::Credits); });
        AddButton(TEXT("Beenden"), [this]() { ShowScreen(EGenesisMenuScreen::QuitConfirm); });
        break;
    }
    case EGenesisMenuScreen::NewGame:
        Title = TEXT("Neues Leben");
        Hint = TEXT("Wähle einen Speicherplatz. Ein belegter Platz wird erst nach Bestätigung überschrieben.");
        for (const FString& SaveSlotName : UGenesisGameInstance::PlayerSlots()) {
            AddButton(SlotLabel(SaveSlotName, true), [this, GI, SaveSlotName]() {
                PendingSlot = SaveSlotName;
                if (UGenesisGameInstance::DescribeSlot(SaveSlotName).bExists) {
                    Screen = EGenesisMenuScreen::NewGameConfirm;
                    LastFocused = 1;                  // default: "No"
                    Rebuild();
                }
                else {
                    ChooseNewGameSlot(SaveSlotName);
                }
            });
        }
        AddButton(TEXT("Zurück"), [this]() { Back(); });
        break;
    case EGenesisMenuScreen::NewGameConfirm:
        Title = TEXT("Überschreiben?");
        Hint = FString::Printf(TEXT("%s ist belegt. Ein neues Leben ersetzt diesen Spielstand endgültig."), *SlotLabel(PendingSlot, false));
        AddButton(TEXT("Ja, neues Leben beginnen"), [this]() { ChooseNewGameSlot(PendingSlot); });
        AddButton(TEXT("Nein"), [this]() { Back(); });
        break;
    case EGenesisMenuScreen::Load:
        Title = TEXT("Laden");
        for (const FString& SaveSlotName : UGenesisGameInstance::PlayerSlots()) {
            const FGenesisSlotInfo I = UGenesisGameInstance::DescribeSlot(SaveSlotName);
            AddButton(SlotLabel(SaveSlotName, false), [this, GI, SaveSlotName]() {
                if (GI && UGenesisGameInstance::DescribeSlot(SaveSlotName).bValid && Flow.Go(TEXT("IN_GAME"))) {
                    GI->LoadSlotAndPlay(SaveSlotName);
                }
            }, I.bValid);
        }
        AddButton(TEXT("Zurück"), [this]() { Back(); });
        break;
    case EGenesisMenuScreen::Settings:
        Title = TEXT("Einstellungen");
        Hint = TEXT("←/→ ändert den Wert. Sprache-, Musik- und Effektlautstärke werden gespeichert und wirken, sobald Vertonung und Musik eingebaut sind.");
        if (U) {
            AddCycle(TEXT("Grafikprofil"), [U]() { return U->GetOverallScalabilityLevel(); },
                [this, U](int32 V) { U->SetOverallScalabilityLevel(V); SettingsChanged(true); },
                { TEXT("Niedrig"), TEXT("Mittel"), TEXT("Hoch"), TEXT("Episch"), TEXT("Kino") });
            AddCycle(TEXT("Anzeige"), [U]() { return int32(U->GetFullscreenMode()); },
                [this, U](int32 V) { U->SetFullscreenMode(EWindowMode::ConvertIntToWindowMode(V)); SettingsChanged(true); },
                { TEXT("Vollbild"), TEXT("Randloses Fenster"), TEXT("Fenster") });
            AddCycle(TEXT("VSync"), [U]() { return U->IsVSyncEnabled() ? 1 : 0; },
                [this, U](int32 V) { U->SetVSyncEnabled(V == 1); SettingsChanged(true); }, { TEXT("Aus"), TEXT("An") });
            AddCycle(TEXT("Bildraten-Grenze"), [U]() { const float L = U->GetFrameRateLimit(); return L <= 0.f ? 3 : L <= 30.f ? 0 : L <= 60.f ? 1 : 2; },
                [this, U](int32 V) { const float Limits[] = { 30.f, 60.f, 120.f, 0.f }; U->SetFrameRateLimit(Limits[V]); SettingsChanged(true); },
                { TEXT("30"), TEXT("60"), TEXT("120"), TEXT("Unbegrenzt") });
            AddPercent(TEXT("Gesamtlautstärke"), &U->MasterVolume, 0.f, 1.f, 0.1f);
            AddPercent(TEXT("Sprache"), &U->SpeechVolume, 0.f, 1.f, 0.1f);
            AddPercent(TEXT("Musik"), &U->MusicVolume, 0.f, 1.f, 0.1f);
            AddPercent(TEXT("Effekte"), &U->EffectsVolume, 0.f, 1.f, 0.1f);
            AddPercent(TEXT("Kamera-Empfindlichkeit"), &U->CameraSensitivity, 0.3f, 2.f, 0.1f);
            AddToggle(TEXT("Kamera Y umkehren"), &U->bInvertCameraY);
            AddToggle(TEXT("Bewegungsunschärfe"), &U->bMotionBlur);
            AddButton(TEXT("Standardwerte"), [this, U]() { U->SetToDefaults(); SettingsChanged(true); Rebuild(); });
        }
        AddButton(TEXT("Zurück"), [this]() { Back(); });
        break;
    case EGenesisMenuScreen::Accessibility:
        Title = TEXT("Barrierefreiheit");
        Hint = TEXT("Textgröße wirkt sofort in Menü und Anzeige. „Lichtblitze verringern“ ist von Anfang an eingeschaltet: Der Lichtschlag zu Beginn wird dann zu einem weichen Aufblenden. „Automatisch schwimmen“ übernimmt in der Schwimmphase die Richtung. Untertitel, Lesetempo und Wackel-Reduktion werden gespeichert und von den Zwischensequenzen genutzt, sobald diese eingebaut sind. Es gibt keine Pflicht-Reaktionstests und keine versteckten Zeitlimits bei Entscheidungen.");
        if (U) {
            AddToggle(TEXT("Untertitel"), &U->bSubtitles);
            AddToggle(TEXT("Sprechername in Untertiteln"), &U->bSubtitleSpeakerNames);
            AddCycle(TEXT("Textgröße"), [U]() { return U->TextScale >= 1.49f ? 2 : U->TextScale >= 1.24f ? 1 : 0; },
                [this, U](int32 V) { const float S[] = { 1.f, 1.25f, 1.5f }; U->TextScale = S[V]; SettingsChanged(false); Rebuild(); },
                { TEXT("100 %"), TEXT("125 %"), TEXT("150 %") });
            AddCycle(TEXT("Lesetempo"), [U]() { return U->ReadingSpeed; }, [this, U](int32 V) { U->ReadingSpeed = V; SettingsChanged(false); },
                { TEXT("Langsam"), TEXT("Normal"), TEXT("Schnell") });
            AddToggle(TEXT("Lichtblitze verringern"), &U->bReduceFlashes);
            AddToggle(TEXT("Kamerawackeln verringern"), &U->bReduceCameraShake);
            AddToggle(TEXT("Automatisch schwimmen"), &U->bAutoSwim);
        }
        AddButton(TEXT("Zurück"), [this]() { Back(); });
        break;
    case EGenesisMenuScreen::Credits:
        Title = TEXT("Mitwirkende");
        Hint = TEXT("GENESIS – technischer Vorabstand (V4.2, CM2)\n\n"
                    "Engine: Unreal® Engine 5.8, Epic Games – Unreal Engine EULA\n"
                    "Platzhalter-Figur: Epic Mannequin (Unreal-Engine-Beispielinhalt) – technischer Platzhalter, nicht final\n"
                    "Schrift: Roboto – Apache License 2.0\n"
                    "Texturen (CC0, Poly Haven): brown_planks_03, damaged_plaster, distressed_painted_planks, garage_floor, painted_brick, painted_concrete_02; HDRI empty_workshop, hausdorf_meadow (nur Vorschau-Renderings)\n"
                    "Modelle: eigene Blender-Modelle (Blender 5.2 als Werkzeug)\n\n"
                    "Noch keine Vertonung, keine Musik und keine Zwischensequenzen im Spiel.");
        AddButton(TEXT("Zurück"), [this]() { Back(); });
        break;
    case EGenesisMenuScreen::QuitConfirm:
        Title = TEXT("Spiel beenden?");
        AddButton(TEXT("Ja, beenden"), [this]() {
            if (Flow.Go(TEXT("EXIT"))) {
                UKismetSystemLibrary::QuitGame(this, GetOwningPlayer(), EQuitPreference::Quit, false);
            }
        });
        AddButton(TEXT("Nein"), [this]() { Back(); });
        LastFocused = FMath::Max(LastFocused, 1);
        break;
    case EGenesisMenuScreen::Pause: {
        Title = TEXT("Pause");
        AddButton(TEXT("Fortsetzen"), [this]() { Resume(); });
        if (bStoryPause) {
            // C02-B swim: no slot yet, so no saving or loading; the swim cannot be skipped.
            Hint = TEXT("Die Schwimmphase lässt sich nicht überspringen. Unter „Barrierefreiheit“ kann „Automatisch schwimmen“ die Richtung übernehmen.");
            AddButton(TEXT("Einstellungen"), [this]() { ShowScreen(EGenesisMenuScreen::Settings); });
            AddButton(TEXT("Barrierefreiheit"), [this]() { ShowScreen(EGenesisMenuScreen::Accessibility); });
            AddButton(TEXT("Hauptmenü"), [this]() { Screen = EGenesisMenuScreen::MainMenuConfirm; LastFocused = 1; Rebuild(); });
            break;
        }
        AddButton(TEXT("Speichern"), [this, GI]() {
            AGenesisPlayerController* PC = Cast<AGenesisPlayerController>(GetOwningPlayer());
            FString Err;
            const bool bOk = PC && PC->SaveGame(&Err);
            InfoText = bOk ? FString::Printf(TEXT("Gespeichert in %s."), *SlotLabel(GI ? GI->ActiveSlot : FString(), false)) : TEXT("Speichern fehlgeschlagen: ") + Err;
            Rebuild();
        }, GI && GI->ActiveSlot != TEXT("Dev"));
        AddButton(TEXT("Laden"), [this]() { ShowScreen(EGenesisMenuScreen::Load); });
        AddButton(TEXT("Einstellungen"), [this]() { ShowScreen(EGenesisMenuScreen::Settings); });
        AddButton(TEXT("Barrierefreiheit"), [this]() { ShowScreen(EGenesisMenuScreen::Accessibility); });
        AddButton(TEXT("Hauptmenü"), [this]() { Screen = EGenesisMenuScreen::MainMenuConfirm; LastFocused = 1; Rebuild(); });
        if (GI && GI->ActiveSlot == TEXT("Dev")) {
            Hint = TEXT("Direkt im Editor gestartet: Speichern im Menü nur bei Start über das Hauptmenü (F5 speichert in den Entwickler-Platz).");
        }
        break;
    }
    case EGenesisMenuScreen::MainMenuConfirm:
        Title = TEXT("Zum Hauptmenü?");
        Hint = bStoryPause ? TEXT("Der Beginn dieses Lebens wird abgebrochen.") : TEXT("Nicht gespeicherter Fortschritt geht verloren.");
        AddButton(TEXT("Ja, zum Hauptmenü"), [this, GI]() {
            if (GI && Flow.Go(TEXT("MAIN_MENU"))) {
                if (bStoryPause) {
                    GI->AbortStoryStart();
                }
                else {
                    GI->ReturnToMainMenu();
                }
            }
        });
        AddButton(TEXT("Nein"), [this]() { Back(); });
        break;
    default:
        break;
    }
    Header->SetText(FText::FromString(Title));
    Info->SetText(FText::FromString(InfoText.IsEmpty() ? Hint : InfoText + (Hint.IsEmpty() ? TEXT("") : TEXT("\n\n") + Hint)));
}

void UGenesisMenuWidget::Rebuild()
{
    const bool bStory = Screen == EGenesisMenuScreen::StoryStart || Screen == EGenesisMenuScreen::ChapterCard;
    const bool bIntro = Screen == EGenesisMenuScreen::Boot || Screen == EGenesisMenuScreen::Title || bStory;
    Center->SetVisibility(bIntro ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
    Panel->SetVisibility(bIntro ? ESlateVisibility::Collapsed : ESlateVisibility::Visible);
    Shade->SetBrushColor(FLinearColor(0.f, 0.f, 0.f, Screen == EGenesisMenuScreen::Boot || bStory ? 1.f : Screen == EGenesisMenuScreen::Title ? 0.35f : bInGame ? 0.45f : 0.f));
    if (Screen != EGenesisMenuScreen::StoryStart) {
        Flash->SetVisibility(ESlateVisibility::Collapsed);
        LightPoint->SetVisibility(ESlateVisibility::Collapsed);
    }

    ButtonBox->ClearChildren();
    Buttons.Reset();
    ButtonTexts.Reset();
    Entries.Reset();
    if (bIntro) {
        if (Screen == EGenesisMenuScreen::Boot) {
            const FBootPage& P = BootPages[FMath::Min(BootPage, int32(UE_ARRAY_COUNT(BootPages)) - 1)];
            BigTitle->SetText(FText::FromString(P.Title));
            BigSub->SetText(FText::FromString(P.Body));
            FSlateFontInfo F = BigTitle->GetFont();
            F.Size = Scaled(BootPage == 0 ? 72 : 34);
            BigTitle->SetFont(F);
        }
        else if (Screen == EGenesisMenuScreen::StoryStart) {
            // Placeholders until the C00/C02 masters are produced (IDs only, no script text). C01 is
            // the real light strike and shows no text.
            const UGenesisGameInstance* GI = GetGenesisGI();
            const EGenesisStoryStep Step = GI ? GI->StoryStart.Step : EGenesisStoryStep::NotStarted;
            const bool bC01 = Step == EGenesisStoryStep::C01;
            BigTitle->SetText(FText::FromString(bC01 ? TEXT("") : Step == EGenesisStoryStep::C00 ? TEXT("C00") : Step == EGenesisStoryStep::C02Film ? TEXT("C02-A") : TEXT("C02-C bis F")));
            BigSub->SetText(FText::FromString(bC01 ? TEXT("") : TEXT("Technischer Platzhalter – der Film ist noch nicht produziert.")));
            Press->SetText(FText::FromString(IsSkipConfirmPending() ? TEXT("Erneut drücken, um den Prolog zu überspringen")
                : Step == EGenesisStoryStep::C00 ? TEXT("Taste zweimal drücken: überspringen") : TEXT("")));
            FSlateFontInfo F = BigTitle->GetFont();
            F.Size = Scaled(34);
            F.LetterSpacing = 200;
            BigTitle->SetFont(F);
        }
        else if (Screen == EGenesisMenuScreen::ChapterCard) {
            BigTitle->SetText(FText::FromString(TEXT("KAPITEL I")));
            BigSub->SetText(FText::FromString(TEXT("DER ANFANG")));
            Press->SetText(FText::FromString(TEXT("Beliebige Taste drücken")));
            FSlateFontInfo F = BigTitle->GetFont();
            F.Size = Scaled(64);
            F.LetterSpacing = 300;
            BigTitle->SetFont(F);
        }
        else {
            // ScriptLock C01 SHOT 01-D: title, line, short silence, then "press any key" (no second title card)
            BigTitle->SetText(FText::FromString(TEXT("GENESIS")));
            BigSub->SetText(FText::FromString(TEXT("DER KREISLAUF DES LEBENS\n\nJede Entscheidung hinterlässt ein Echo.")));
            Press->SetText(FText::FromString(TEXT("Beliebige Taste drücken")));
            FSlateFontInfo F = BigTitle->GetFont();
            F.Size = Scaled(110);
            F.LetterSpacing = 400;
            BigTitle->SetFont(F);
        }
        FSlateFontInfo S = BigSub->GetFont();
        const bool bCard = Screen == EGenesisMenuScreen::Title || Screen == EGenesisMenuScreen::ChapterCard;
        S.Size = Scaled(bCard ? 22 : 18);
        S.LetterSpacing = bCard ? 120 : 0;
        BigSub->SetFont(S);
        FSlateFontInfo PF = Press->GetFont();
        PF.Size = Scaled(17);
        Press->SetFont(PF);
        Press->SetVisibility(bCard || Screen == EGenesisMenuScreen::StoryStart ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
        if (Screen == EGenesisMenuScreen::StoryStart) {
            Press->SetRenderOpacity(1.f);
        }
        SetFocus();
        return;
    }

    BuildEntries();
    // The column grows with the accessibility text size, so long setting rows never get cut off.
    const float Grow = Scaled(100) / 100.f;
    if (UCanvasPanelSlot* PanelSlot = Cast<UCanvasPanelSlot>(Panel->Slot)) {
        PanelSlot->SetOffsets(FMargin(0.f, 0.f, 680.f * Grow + 60.f * (Grow - 1.f), 0.f));
    }
    Info->SetWrapTextAt(560.f * Grow);
    Footer->SetWrapTextAt(560.f * Grow);
    FSlateFontInfo HF = Header->GetFont();
    HF.Size = Scaled(40);
    Header->SetFont(HF);
    FSlateFontInfo IF = Info->GetFont();
    IF.Size = Scaled(16);
    Info->SetFont(IF);
    FSlateFontInfo FF = Footer->GetFont();
    FF.Size = Scaled(13);
    Footer->SetFont(FF);
    Footer->SetText(FText::FromString(TEXT("Enter / A auswählen   ·   Esc / B zurück   ·   ← → Wert ändern\nGENESIS · technischer Stand V4.2 – kein finales Spiel")));

    FSlateBrush Brush;
    Brush.DrawAs = ESlateBrushDrawType::RoundedBox;
    Brush.OutlineSettings.RoundingType = ESlateBrushRoundingType::FixedRadius;
    Brush.OutlineSettings.CornerRadii = FVector4(3.f, 3.f, 3.f, 3.f);
    Brush.TintColor = FSlateColor(FLinearColor::White);
    FButtonStyle Style;
    Style.SetNormal(Brush).SetHovered(Brush).SetPressed(Brush).SetDisabled(Brush);
    Style.SetNormalPadding(FMargin(16.f, 9.f)).SetPressedPadding(FMargin(16.f, 10.f, 16.f, 8.f));

    for (int32 I = 0; I < Entries.Num(); ++I) {
        UGenesisChoiceButton* B = WidgetTree->ConstructWidget<UGenesisChoiceButton>(UGenesisChoiceButton::StaticClass());
        B->SetStyle(Style);
        B->Setup(I);
        B->OnChoice.BindUObject(this, &UGenesisMenuWidget::HandleChoice);
        B->SetIsEnabled(Entries[I].bEnabled);
        UTextBlock* T = MakeText(FString(), Scaled(22));      // unnamed: a rebuilt screen must never reuse the name of a live widget
        T->SetShadowOffset(FVector2D::ZeroVector);
        T->SetText(FText::FromString(Entries[I].Label()));
        if (UButtonSlot* BS = Cast<UButtonSlot>(B->AddChild(T))) {
            BS->SetHorizontalAlignment(HAlign_Left);
        }
        ButtonBox->AddChildToVerticalBox(B)->SetPadding(FMargin(0.f, 3.f));
        Buttons.Add(B);
        ButtonTexts.Add(T);
    }
    FocusEntry(FMath::Clamp(LastFocused, 0, Entries.Num() - 1));
}

void UGenesisMenuWidget::FocusEntry(int32 Index)
{
    for (int32 Step = 0; Step < Entries.Num(); ++Step) {
        const int32 I = (Index + Step) % Entries.Num();
        if (Entries[I].bEnabled && Buttons.IsValidIndex(I)) {
            LastFocused = I;
            Buttons[I]->SetFocus();
            return;
        }
    }
    SetFocus();
}

int32 UGenesisMenuWidget::GetFocusedEntry() const
{
    for (int32 I = 0; I < Buttons.Num(); ++I) {
        if (Buttons[I]->HasKeyboardFocus() || Buttons[I]->HasUserFocus(GetOwningPlayer())) {
            return I;
        }
    }
    return INDEX_NONE;
}

void UGenesisMenuWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    ScreenTime += InDeltaTime;
    if (PendingChoice != INDEX_NONE) {
        const int32 Index = PendingChoice;
        PendingChoice = INDEX_NONE;
        ActivateEntry(Index);
    }
    if (Screen == EGenesisMenuScreen::Boot && BootPage < int32(UE_ARRAY_COUNT(BootPages)) && ScreenTime > BootPages[BootPage].Seconds) {
        AdvanceIntro();
    }
    if (Screen == EGenesisMenuScreen::StoryStart) {
        StoryStartTick();
    }
    if (Screen == EGenesisMenuScreen::Title || Screen == EGenesisMenuScreen::ChapterCard) {
        const float T = ScreenTime - 2.f;          // "Kurze Stille", then the prompt fades in and breathes
        Press->SetRenderOpacity(T <= 0.f ? 0.f : FMath::Min(T, 1.f) * (0.6f + 0.4f * FMath::Cos(T * 2.f)));
    }
    const int32 Focused = GetFocusedEntry();
    if (Focused != INDEX_NONE) {
        LastFocused = Focused;
    }
    else if (Buttons.Num() > 0 && IsVisible() && !HasAnyUserFocus()) {
        FocusEntry(LastFocused);              // focus lost (e.g. click on empty space): keep it visible
    }
    // Visible focus: filled accent bar on the focused entry, readable text on every state.
    for (int32 I = 0; I < Buttons.Num(); ++I) {
        const bool bFocus = I == Focused;
        const bool bEnabled = Entries.IsValidIndex(I) && Entries[I].bEnabled;
        Buttons[I]->SetBackgroundColor(bFocus ? Accent : FLinearColor(1.f, 1.f, 1.f, 0.f));
        ButtonTexts[I]->SetColorAndOpacity(FSlateColor(bFocus ? Ink : bEnabled ? FLinearColor::White : MenuDim));
        if (Entries.IsValidIndex(I)) {
            ButtonTexts[I]->SetText(FText::FromString(Entries[I].Label()));
        }
    }
}

void UGenesisMenuWidget::HandleChoice(int32 Index)
{
    PendingChoice = Index;            // run after Slate's click handling: the action may rebuild the screen
}

bool UGenesisMenuWidget::ActivateEntry(int32 Index)
{
    if (!Entries.IsValidIndex(Index) || !Entries[Index].bEnabled || !Entries[Index].Activate) {
        return false;
    }
    LastFocused = Index;
    const TFunction<void()> Action = Entries[Index].Activate;
    Action();
    return true;
}

bool UGenesisMenuWidget::AdjustEntry(int32 Index, int32 Direction)
{
    if (!Entries.IsValidIndex(Index) || !Entries[Index].Adjust) {
        return false;
    }
    const TFunction<void(int32)> Adjust = Entries[Index].Adjust;
    Adjust(Direction);
    return true;
}

TArray<FString> UGenesisMenuWidget::GetEntryLabels() const
{
    TArray<FString> Labels;
    for (const FEntry& E : Entries) {
        Labels.Add(E.Label());
    }
    return Labels;
}

int32 UGenesisMenuWidget::FindEntry(const FString& Label) const
{
    for (int32 I = 0; I < Entries.Num(); ++I) {
        if (Entries[I].Label().StartsWith(Label)) {
            return I;
        }
    }
    return INDEX_NONE;
}

FReply UGenesisMenuWidget::NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent)
{
    const FKey Key = InKeyEvent.GetKey();
    if (Screen == EGenesisMenuScreen::Boot || Screen == EGenesisMenuScreen::Title || Screen == EGenesisMenuScreen::StoryStart
        || Screen == EGenesisMenuScreen::ChapterCard) {
        AdvanceIntro();
        return FReply::Handled();
    }
    if (Key == EKeys::Escape || Key == EKeys::Gamepad_FaceButton_Right || Key == EKeys::BackSpace
        || (Screen == EGenesisMenuScreen::Pause && (Key == EKeys::Gamepad_Special_Right || Key == EKeys::P))) {
        Back();
        return FReply::Handled();
    }
    return Super::NativeOnKeyDown(InGeometry, InKeyEvent);
}

FReply UGenesisMenuWidget::NativeOnPreviewKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent)
{
    // Left/right change a setting. Taken in the preview (tunnel) phase: Slate turns unhandled
    // arrow keys into focus navigation before the bubbling key event reaches this widget.
    const FKey Key = InKeyEvent.GetKey();
    const bool bLeft = Key == EKeys::Left || Key == EKeys::Gamepad_DPad_Left || Key == EKeys::Gamepad_LeftStick_Left || Key == EKeys::A;
    const bool bRight = Key == EKeys::Right || Key == EKeys::Gamepad_DPad_Right || Key == EKeys::Gamepad_LeftStick_Right || Key == EKeys::D;
    if ((bLeft || bRight) && AdjustEntry(GetFocusedEntry(), bRight ? 1 : -1)) {
        return FReply::Handled();
    }
    return Super::NativeOnPreviewKeyDown(InGeometry, InKeyEvent);
}

FReply UGenesisMenuWidget::NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
    if (Screen == EGenesisMenuScreen::Boot || Screen == EGenesisMenuScreen::Title || Screen == EGenesisMenuScreen::StoryStart
        || Screen == EGenesisMenuScreen::ChapterCard) {
        AdvanceIntro();
        return FReply::Handled();
    }
    return Super::NativeOnMouseButtonDown(InGeometry, InMouseEvent);
}
