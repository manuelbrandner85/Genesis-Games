#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "GenesisSwimGameMode.generated.h"

class ACameraActor;
class AGenesisSpermPawn;
class UGenesisMenuWidget;
class UInstancedStaticMeshComponent;
class UPointLightComponent;

/** Course of the C02-B swim (CR-001 E2/E4): no game over, no timer or ranking on screen. */
UENUM()
enum class EGenesisSwimPhase : uint8
{
    Free,           // 0-120 s: the player swims (auto swim: guided from the start)
    Guided,         // after 120 s: the course leads the cell gently to the oocyte
    Fusion,         // the player's cell reached the zona pellucida
    Objective,      // still not there: objective camera, another cell fuses - the life begins anyway
    Finished,
};

/**
 * C02-B graybox director: builds the oviduct (analytic tube, ring plates), the oocyte with zona and
 * cumulus cells and the other sperm cells, runs the time window and ends the swim with Own or
 * Other. Hands the result to the story start (UGenesisGameInstance::FinishSwim); started directly
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

    static constexpr float FreeSeconds = 120.f;       // E4: 60-120 s of own swimming
    static constexpr float GuideRampSeconds = 15.f;
    static constexpr float ObjectiveAfter = 165.f;    // still not arrived: another cell fuses
    static constexpr float FusionSeconds = 2.5f;
    static constexpr float ObjectiveSeconds = 5.f;
    static constexpr int32 OtherCells = 40;

    EGenesisSwimPhase GetPhase() const { return Phase; }
    float GetElapsed() const { return Elapsed; }
    FName GetResult() const { return Result; }
    bool IsFinished() const { return Phase == EGenesisSwimPhase::Finished; }
    float GetArrivalSeconds() const { return ArrivalSeconds; }
    /** Tests: ends the swim at once with the given result (Own/Other). */
    void ForceFinish(FName InResult);

private:
    void BuildCourse();
    void TickOthers(float DeltaTime);
    void Finish();
    AGenesisSpermPawn* GetSperm() const;

    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Wall;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Cumulus;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Others;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> OtherTails;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Oocyte;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Zona;
    UPROPERTY() TObjectPtr<UPointLightComponent> EggLight;
    UPROPERTY() TObjectPtr<ACameraActor> ObjectiveCamera;

    struct FOther { FVector P; FVector H; float S = 0.f; float Effort = 0.6f; float Seed = 0.f; };
    TArray<FOther> OtherState;
    EGenesisSwimPhase Phase = EGenesisSwimPhase::Free;
    float Elapsed = 0.f;
    float PhaseTime = 0.f;
    float ArrivalSeconds = -1.f;
    int32 FusingOther = INDEX_NONE;
    bool bPlaced = false;
    FName Result;
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
