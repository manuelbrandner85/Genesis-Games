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

    /** Keyboard/mouse + gamepad layout: WASD/left stick move, mouse/right stick look, Space/A jump. */
    static FGenesisPrototypeInput Create(UObject* Outer);
    /** Gamepad look speed in degrees per second at full stick deflection. */
    static constexpr float GamepadLookRateDegPerSec = 150.f;
};

/** TECHNICAL PROXY ONLY. No canonical model, story or production-ready animations. */
UCLASS()
class GENESIS_API AGenesisPrototypeCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AGenesisPrototypeCharacter();
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;
    virtual void NotifyControllerChanged() override;
    const FGenesisPrototypeInput& GetPrototypeInput() const { return InputSetup; }
protected:
    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
    void EnsureInputSetup();
    UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> SpringArm;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> FollowCamera;
    UPROPERTY(Transient) FGenesisPrototypeInput InputSetup;
};
