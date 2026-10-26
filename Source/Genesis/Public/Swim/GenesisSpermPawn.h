#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "Swim/GenesisSpermRoute.h"
#include "GenesisSpermPawn.generated.h"

class UCameraComponent;
class UPointLightComponent;
class USpringArmComponent;
class UStaticMeshComponent;

/**
 * C02-B graybox: the player's sperm cell (1 uu = 1 um, see FGenesisOviduct).
 * Movement as at this scale in reality: no coasting (Reynolds number ~1e-2, the cell stops when
 * the flagellum stops), only a short response time; the flagellum beat pushes along the heading,
 * the fluid flow carries the cell, and the cell turns against the flow on its own (rheotaxis).
 * The player steers the heading and can beat harder (hyperactivated motility); never a race UI.
 */
UCLASS()
class GENESIS_API AGenesisSpermPawn : public APawn
{
    GENERATED_BODY()
public:
    AGenesisSpermPawn();
    virtual void Tick(float DeltaTime) override;

    static constexpr float SwimSpeed = 80.f;          // um/s at full beat (hyperactivated)
    static constexpr float BaseEffort = 0.7f;         // 56 um/s progressive without extra effort
    static constexpr float TurnYawDeg = 75.f;         // deg/s at full stick
    static constexpr float TurnPitchDeg = 60.f;
    static constexpr float RheotaxisRate = 0.35f;     // rad/s towards upstream
    static constexpr float ResponseSeconds = 0.08f;

    /** Input of this frame: steer (x yaw, y pitch, -1..1) and a stronger beat. */
    void SetSwimInput(const FVector2D& Steer, bool bBurst) { SteerInput = Steer; bBurstInput = bBurst; }
    /** 0..1: how strongly the course guides the cell to the oocyte (auto swim = 1, E2/E4). */
    void SetGuidance(float Amount) { Guidance = FMath::Clamp(Amount, 0.f, 1.f); }
    void SetFrozen(bool bInFrozen) { bFrozen = bInFrozen; }
    bool IsFrozen() const { return bFrozen; }
    void PlaceAtStart();
    /** CR-002: the section the cell swims in now (W1-W5); the pawn keeps a copy. */
    void SetCourse(const FGenesisCourse& InCourse) { Course = InCourse; }
    const FGenesisCourse& GetCourse() const { return Course; }
    /** Medium of the moment: < 1 in the coagulum, acidic zones or mucus (set by the director per frame). */
    void SetMediumFactor(float F) { MediumFactor = F; }
    /** Hyperactivated motility after capacitation (W4 onwards). */
    void SetSpeedFactor(float F) { SpeedFactor = F; }
    float GetSpeedFactor() const { return SpeedFactor; }
    /** Where the guidance leads at the end of the section (default: the course end; W3: the correct tube). */
    void SetFinalGoal(const FVector& Goal) { FinalGoal = Goal; bHasFinalGoal = true; }
    /** Place the cell at a course position (section start, or taking over another cell - F4). */
    void PlaceAt(float S, const FVector& Offset = FVector::ZeroVector);

    float GetCourseS() const { return CourseS; }
    FVector GetHeading() const { return Heading; }
    FVector GetSwimVelocity() const { return Velocity; }
    float GetGuidance() const { return Guidance; }
    int32 GetWallContacts() const { return WallContacts; }

private:
    void AnimateFlagellum(float DeltaTime);

    UPROPERTY() TObjectPtr<USceneComponent> Body;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Head;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Midpiece;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Tail;
    UPROPERTY() TObjectPtr<USpringArmComponent> Arm;
    UPROPERTY() TObjectPtr<UCameraComponent> Camera;
    UPROPERTY() TObjectPtr<UPointLightComponent> Lamp;

    FGenesisCourse Course;
    float MediumFactor = 1.f;
    float SpeedFactor = 1.f;
    FVector FinalGoal = FVector::ZeroVector;
    bool bHasFinalGoal = false;
    FVector Heading = FVector::ForwardVector;
    FVector Velocity = FVector::ZeroVector;
    FVector2D SteerInput = FVector2D::ZeroVector;
    bool bBurstInput = false;
    bool bFrozen = false;
    float Guidance = 0.f;
    float CourseS = 0.f;
    float BeatPhase = 0.f;
    int32 WallContacts = 0;
};
