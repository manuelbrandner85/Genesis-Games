#include "UI/GenesisMenuGameMode.h"
#include "UI/GenesisMenuWidget.h"
#include "GenesisGameInstance.h"
#include "Camera/CameraActor.h"
#include "EngineUtils.h"

AGenesisMenuGameMode::AGenesisMenuGameMode()
{
    DefaultPawnClass = nullptr;
    PlayerControllerClass = AGenesisMenuPlayerController::StaticClass();
}

void AGenesisMenuPlayerController::BeginPlay()
{
    Super::BeginPlay();
    if (!IsLocalController()) {
        return;
    }
    for (TActorIterator<ACameraActor> It(GetWorld()); It; ++It) {
        if (It->ActorHasTag(TEXT("MenuCamera"))) {
            MenuCamera = *It;
            CameraStart = MenuCamera->GetActorTransform();
            SetViewTarget(MenuCamera);
            break;
        }
    }
    Menu = CreateWidget<UGenesisMenuWidget>(this, UGenesisMenuWidget::StaticClass());
    if (!Menu) {
        return;
    }
    Menu->AddToViewport();
    const UGenesisGameInstance* GI = Cast<UGenesisGameInstance>(GetGameInstance());
    Menu->StartMainMenu(GI && GI->bBootSequenceShown);
    FInputModeUIOnly Mode;
    Mode.SetWidgetToFocus(Menu->TakeWidget());
    SetInputMode(Mode);
    SetShowMouseCursor(true);
}

void AGenesisMenuPlayerController::PlayerTick(float DeltaTime)
{
    Super::PlayerTick(DeltaTime);
    if (!MenuCamera) {
        return;
    }
    // Slow handheld-like drift: a few centimetres and under a degree, periods of 40-90 s.
    Time += DeltaTime;
    const FVector Offset(FMath::Sin(Time * 0.11f) * 18.f, FMath::Sin(Time * 0.07f + 1.3f) * 26.f, FMath::Sin(Time * 0.15f) * 4.f);
    const FRotator Turn(FMath::Sin(Time * 0.09f) * 0.6f, FMath::Sin(Time * 0.071f + 0.4f) * 1.4f, 0.f);
    MenuCamera->SetActorLocationAndRotation(CameraStart.GetLocation() + Offset, (CameraStart.Rotator() + Turn).Quaternion());
}
