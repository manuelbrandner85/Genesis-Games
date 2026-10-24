#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GenesisPrototypeCharacter.generated.h"
class UCameraComponent;
class USpringArmComponent;
class UInputAction;
class UInputMappingContext;
struct FInputActionValue;

/** Enhanced Input objects of the tech proxy, built in code (no .uasset needed for the smoke test). */
USTRUCT()
struct GENESIS_API FGenesisPrototypeInput
{
    GENERATED_BODY()
    UPROPERTY(Transient) TObjectPtr<UInputMappingContext> Context;
    UPROPERTY(Transient) TObjectPtr<UInputAction> Move;
    UPROPERTY(Transient) TObjectPtr<UInputAction> Look;
    UPROPERTY(Transient) TObjectPtr<UInputAction> Jump;
    UPROPERTY(Transient) TObjectPtr<UInputAction> Sprint;
    UPROPERTY(Transient) TObjectPtr<UInputAction> SprintToggle;
    UPROPERTY(Transient) TObjectPtr<UInputAction> Interact;      // E / gamepad X: talk, use, end conversation
    UPROPERTY(Transient) TObjectPtr<UInputAction> Confirm;       // Enter / gamepad A in a conversation
    UPROPERTY(Transient) TObjectPtr<UInputAction> ChoiceUp;      // arrow / d-pad up
    UPROPERTY(Transient) TObjectPtr<UInputAction> ChoiceDown;    // arrow / d-pad down
    UPROPERTY(Transient) TArray<TObjectPtr<UInputAction>> Choices; // keys 1-6
    UPROPERTY(Transient) TObjectPtr<UInputAction> SaveGame;      // F5
    UPROPERTY(Transient) TObjectPtr<UInputAction> LoadGame;      // F9

    /** Keyboard/mouse + gamepad layout: WASD/left stick move, mouse/right stick look, Space/A jump,
     *  Shift held / left stick click (toggle) sprint, E / X interact, 1-6 or d-pad + A choose, F5/F9 save/load. */
    static FGenesisPrototypeInput Create(UObject* Outer);
    /** Gamepad look speed in degrees per second at full stick deflection. */
    static constexpr float GamepadLookRateDegPerSec = 150.f;
    /** Right stick dead zone. 0.3 instead of the usual 0.2-0.25: worn sticks rest at up to ~28 %
     *  (measured on the dev PC's controller) and would otherwise turn the camera on their own. */
    static constexpr float LookDeadZone = 0.3f;
};

/** TECHNICAL PROXY ONLY. No canonical model, story or production-ready animations.
 *  Movement values follow real people: walking 1.75 m/s, running 4.5 m/s, jump ~45 cm. */
UCLASS(Config=Game)
class GENESIS_API AGenesisPrototypeCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    static constexpr float WalkSpeed = 175.f;       // cm/s, brisk walk (6.3 km/h)
    static constexpr float SprintSpeed = 450.f;     // cm/s, run (16.2 km/h)
    static constexpr float JumpHeight = 45.f;       // cm, standing jump of an adult
    static constexpr float PitchMin = -70.f;        // look down limit (deg)
    static constexpr float PitchMax = 55.f;         // look up limit (deg)

    AGenesisPrototypeCharacter();
    virtual void PostInitializeComponents() override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;
    virtual void NotifyControllerChanged() override;
    const FGenesisPrototypeInput& GetPrototypeInput() const { return InputSetup; }
    void SetSprinting(bool bNewSprinting);
    bool IsSprinting() const { return bSprinting; }
    USpringArmComponent* GetSpringArm() const { return SpringArm; }
protected:
    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
    void StartSprint() { SetSprinting(true); }
    void StopSprint() { SetSprinting(false); }
    void ToggleSprint() { SetSprinting(!bSprinting); }
    void DoJump();
    void DoStopJumping();
    void OnInteract();
    void OnConfirm();
    void OnChoiceUp();
    void OnChoiceDown();
    void OnChoice(int32 Index);
    void OnSave();
    void OnLoad();
    class AGenesisPlayerController* GenesisPC() const;
    void EnsureInputSetup();
    UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> SpringArm;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> FollowCamera;
    UPROPERTY(Transient) FGenesisPrototypeInput InputSetup;
    /** Visual proxy, set in DefaultGame.ini so it can be swapped without code changes. */
    UPROPERTY(Config) TSoftObjectPtr<class USkeletalMesh> ProxyMesh;
    UPROPERTY(Config) TSoftClassPtr<class UAnimInstance> ProxyAnimClass;
    bool bSprinting = false;
};
