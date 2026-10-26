#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "Swim/GenesisSpermRoute.h"
#include "GenesisSwimGameMode.generated.h"

class ACameraActor;
class AGenesisSpermPawn;
class UGenesisMenuWidget;
class UInstancedStaticMeshComponent;
class UPointLightComponent;
class UTextBlock;

/** Course of the C02-B route (ScriptLock 1.3): no game over, no timer or ranking on screen. */
UENUM()
enum class EGenesisSwimPhase : uint8
{
    Free,           // the player swims (auto swim: guided from the start)
    Guided,         // after the section's free time the course leads gently to its end
    Resting,        // W4: bound to the epithelium, capacitation (a labelled time jump)
    Transition,     // between two sections: caption, then the next section is built
    Fusion,         // W5: the player's cell reached the zona pellucida
    Objective,      // W5: still not there: objective camera, another cell fuses - the life begins anyway
    Finished,
};

/** Factual captions over the swim (section names, time jumps); no score, no timer. */
UCLASS()
class GENESIS_API UGenesisSwimHud : public UUserWidget
{
    GENERATED_BODY()
public:
    void ShowCaption(const FString& Text, float Seconds);
    const FString& GetCaption() const { return Caption; }

protected:
    virtual void NativeOnInitialized() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
    UTextBlock* Label = nullptr;
    FString Caption;
    float Left = 0.f;
    float Total = 1.f;
};

/**
 * C02-B graybox director (CR-002): runs the route W1 vagina -> W2 cervix -> W3 uterus -> W4 isthmus ->
 * W5 ampulla one section after the other. Builds each section (analytic course, wall plates, crypts,
 * tubal exits, the oocyte with cumulus in W5) and the other sperm cells (fewer in every section), applies
 * the section mechanics (coagulum and acidic zones, mucus, contraction waves, binding + capacitation,
 * hyperactivation), guides gently after each section's free time and never ends in a game over: a
 * cell that gets stuck or takes the wrong tube hands control to another cell (F4); in W5 another cell
 * may fuse. Hands the result to the story start (UGenesisGameInstance::FinishSwim); started directly
 * (editor, tests) it only records the result.
 */
UCLASS()
class GENESIS_API AGenesisSwimDirector : public AActor
{
    GENERATED_BODY()
public:
    AGenesisSwimDirector();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    static constexpr float FreeSeconds = 120.f;       // W5 (E4 kept for the last section)
    static constexpr float GuideRampSeconds = 15.f;
    static constexpr float ObjectiveAfter = 165.f;    // W5: still not arrived: another cell fuses
    static constexpr float FusionSeconds = 2.5f;
    static constexpr float ObjectiveSeconds = 5.f;
    static constexpr float TransitionSeconds = 2.5f;
    static constexpr float NoProgressSeconds = 25.f;  // W1-W4: no headway for this long -> another cell takes over
    static constexpr int32 OtherCells = 40;
    /** Editor/tests without a story start: the section the route begins with. */
    static EGenesisRouteSection StandaloneStartSection;

    EGenesisSwimPhase GetPhase() const { return Phase; }
    EGenesisRouteSection GetSection() const { return Section; }
    float GetElapsed() const { return Elapsed; }
    float GetSectionElapsed() const { return SectionElapsed; }
    FName GetResult() const { return Result; }
    bool IsFinished() const { return Phase == EGenesisSwimPhase::Finished; }
    float GetArrivalSeconds() const { return ArrivalSeconds; }
    int32 GetSwitches() const { return Switches; }
    int32 GetSectionsDone() const { return SectionsDone; }
    bool WasShortened() const { return bShortened; }
    bool HasRested() const { return bRested; }
    TArray<float> GetSectionSeconds() const { return SectionSeconds; }
    const FString& GetLastSwitchReason() const { return LastSwitchReason; }

    /** F3: after the first complete route W1-W4 may be shortened to a short film; W5 stays playable. */
    bool CanShorten() const;
    bool Shorten();
    /** Tests: ends the swim at once with the given result (Own/Other). */
    void ForceFinish(FName InResult);
    /** Tests: puts the cell deep into the first crypt (W2) / into the wrong tube (W3). */
    bool DebugEnterPocket();
    bool DebugWrongExit();

private:
    void BuildSection();
    void ClearSection();
    void StartSection(EGenesisRouteSection NewSection);
    void EndSection();
    void SwitchCell(const FString& Why, float NewS, const FVector& Offset);
    void TickOthers(float DeltaTime);
    void TickMechanics(float DeltaTime);
    void Finish();
    void Caption(const FString& Text, float Seconds);
    AGenesisSpermPawn* GetSperm() const;

    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Wall;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Cumulus;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Others;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> OtherTails;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Particles;   // coagulum strands, acidic zones, mucus
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Oocyte;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Zona;
    UPROPERTY() TObjectPtr<UPointLightComponent> EggLight;
    UPROPERTY() TObjectPtr<ACameraActor> ObjectiveCamera;
    UPROPERTY() TObjectPtr<UGenesisSwimHud> Hud;

    struct FOther { FVector P; FVector H; float S = 0.f; float Effort = 0.6f; float Seed = 0.f; };
    TArray<FOther> OtherState;
    TArray<FVector> AcidZones;
    FGenesisCourse Course;
    EGenesisRouteSection Section = EGenesisRouteSection::Vagina;
    EGenesisRouteSection NextSection = EGenesisRouteSection::Vagina;
    EGenesisSwimPhase Phase = EGenesisSwimPhase::Free;
    float Elapsed = 0.f;
    float SectionElapsed = 0.f;
    float PhaseTime = 0.f;
    float ArrivalSeconds = -1.f;
    float StuckTime = 0.f;
    float ProgressS = 0.f;
    float ProgressTime = 0.f;
    int32 FusingOther = INDEX_NONE;
    int32 Switches = 0;
    int32 SectionsDone = 0;
    bool bPlaced = false;
    bool bRested = false;
    bool bShortened = false;
    bool bStarted = false;
    FName Result;
    FString LastSwitchReason;
    TArray<float> SectionSeconds;
};

/** C02-B controls: left stick / WASD / arrows steer, A / Space / RT / Shift beat harder,
 *  Esc / P / Menu pause. Gamepad stick dead zone against drift. */
UCLASS()
class GENESIS_API AGenesisSwimPlayerController : public APlayerController
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void SetupInputComponent() override;
    virtual void PlayerTick(float DeltaTime) override;

    static constexpr float StickDeadZone = 0.25f;
    void TogglePauseMenu();
    bool IsPauseMenuOpen() const { return PauseMenu != nullptr; }
    UGenesisMenuWidget* GetPauseMenu() const { return PauseMenu; }
    /** The steer/burst values read from the keys this frame (for tests). */
    FVector2D GetLastSteer() const { return LastSteer; }
    bool GetLastBurst() const { return bLastBurst; }

private:
    void ClosePauseMenu();
    UPROPERTY() TObjectPtr<UGenesisMenuWidget> PauseMenu;
    FVector2D LastSteer = FVector2D::ZeroVector;
    bool bLastBurst = false;
};

UCLASS()
class GENESIS_API AGenesisSwimGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AGenesisSwimGameMode();
    virtual void StartPlay() override;
};
