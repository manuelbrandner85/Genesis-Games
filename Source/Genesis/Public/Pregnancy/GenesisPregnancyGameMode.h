#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Cinematic/GenesisSceneTypes.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Pregnancy/GenesisPregnancy.h"
#include "GenesisPregnancyGameMode.generated.h"

class UCameraComponent;
class UGenesisMenuWidget;
class UInstancedStaticMeshComponent;
class UPointLightComponent;
class USpringArmComponent;
class UTextBlock;

/** Stage, week, real size, the actions the development allows now and the visible consequence outside. */
UCLASS()
class GENESIS_API UGenesisPregnancyHud : public UUserWidget
{
    GENERATED_BODY()
public:
    void Refresh(const FString& Header, const FString& Facts, const TArray<FString>& Actions, int32 Selected, const FString& Outside);
    void ShowCaption(const FString& Text, float Seconds);
    const FString& GetCaption() const { return Caption; }

protected:
    virtual void NativeOnInitialized() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
    UTextBlock* HeaderText = nullptr;
    UTextBlock* FactsText = nullptr;
    UTextBlock* ActionsText = nullptr;
    UTextBlock* OutsideText = nullptr;
    UTextBlock* CaptionText = nullptr;
    FString Caption;
    float CaptionLeft = 0.f;
};

/** Orbit camera around the developing child (objective visualisation, not a point of view). */
UCLASS()
class GENESIS_API AGenesisPregnancyViewPawn : public APawn
{
    GENERATED_BODY()
public:
    AGenesisPregnancyViewPawn();
    void Orbit(const FVector2D& Delta);
    void Zoom(float Delta);
    UPROPERTY() TObjectPtr<USpringArmComponent> Arm;
    UPROPERTY() TObjectPtr<UCameraComponent> Camera;
    /** Visualisation light at the camera (ScriptLock: the inside view is a "Visualisierungsoptik"). */
    UPROPERTY() TObjectPtr<UPointLightComponent> ViewLight;
};

/**
 * Graybox of the playable pregnancy (GD-2026-10-26-02/-03): runs FGenesisPregnancy, builds the developing
 * child per stage at a fixed visual size with its real size labelled (S1 cells -> S2 blastocyst ->
 * S3 embryonic disc with the first heartbeat -> fetus with limbs, cord and placenta), the uterine wall
 * and the light that really comes through the belly. Actions animate the child and write their
 * consequence outside into the world ledger. C03 in late pregnancy and C04 at the birth run as scene
 * contracts (technical placeholders); after the birth the life is saved and continues in the world.
 */
UCLASS()
class GENESIS_API AGenesisPregnancyDirector : public AActor
{
    GENERATED_BODY()
public:
    AGenesisPregnancyDirector();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** Real size of the child (embryo/fetus crown-rump length, earlier the cell cluster) in mm. */
    static float RealSizeMm(float Day);

    FGenesisPregnancy& GetPregnancy() { return Preg; }
    const FGenesisPregnancy& GetPregnancyConst() const { return Preg; }
    bool PerformAction(EGenesisPregAction A);
    bool ShortenStage();
    void SetTimeLapse(bool bOn) { Preg.TimeScale = bOn ? 8.f : 1.f; }
    /** Writes the pregnancy into the world state and saves it in the active slot. */
    bool SaveNow(FString* OutError = nullptr);
    void SelectAction(int32 Delta);
    EGenesisPregAction GetSelectedAction() const;
    int32 GetOutsideEvents() const { return OutsideEvents; }
    const FString& GetLastOutside() const { return LastOutside; }
    bool IsInScene() const { return SceneLeft > 0.f; }
    bool HasHandedOverAfterBirth() const { return bHandedOver; }
    /** Tests: stop at the birth instead of travelling to the world map. */
    static bool bStayAfterBirthForTests;

private:
    void StartLife();
    void BuildStage();
    void UpdateVisual(float DeltaTime);
    void RefreshHud();
    void PlayScene(FName SceneID, float Seconds);
    void FinishScene();
    void SyncWorldState();

    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Wall;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Cells;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Body;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Cord;
    UPROPERTY() TObjectPtr<UPointLightComponent> BellyLight;
    UPROPERTY() TObjectPtr<UGenesisPregnancyHud> Hud;

    FGenesisPregnancy Preg;
    FGenesisSceneContract Scene;
    int32 BuiltStage = -1;
    int32 Selected = 0;
    int32 OutsideEvents = 0;
    float SceneLeft = 0.f;
    float AnimTime = 0.f;
    float ActionAnim = 0.f;
    EGenesisPregAction AnimAction = EGenesisPregAction::Observe;
    float TurnAngle = 0.f;
    float TurnTarget = 0.f;
    bool bAsleep = false;
    bool bStarted = false;
    bool bHandedOver = false;
    int64 ConceptionMinute = 0;
    FString LastOutside;
    FString OutsideLine;
};

/** Controls: left stick / WASD orbit, triggers / mouse wheel zoom, d-pad / Q E choose an action,
 *  A / Space / Enter do it, RB / T hold time lapse, Esc / P / Menu pause. */
UCLASS()
class GENESIS_API AGenesisPregnancyPlayerController : public APlayerController
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void SetupInputComponent() override;
    virtual void PlayerTick(float DeltaTime) override;
    void TogglePauseMenu();
    bool IsPauseMenuOpen() const { return PauseMenu != nullptr; }
    UGenesisMenuWidget* GetPauseMenu() const { return PauseMenu; }
    AGenesisPregnancyDirector* GetDirector() const;

private:
    void ClosePauseMenu();
    void ActionPrev();
    void ActionNext();
    void DoAction();
    UPROPERTY() TObjectPtr<UGenesisMenuWidget> PauseMenu;
};

UCLASS()
class GENESIS_API AGenesisPregnancyGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AGenesisPregnancyGameMode();
    virtual void StartPlay() override;
};
