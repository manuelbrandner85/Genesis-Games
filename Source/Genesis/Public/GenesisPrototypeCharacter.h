#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GenesisPrototypeCharacter.generated.h"
class UCameraComponent;
class USpringArmComponent;
/** TECHNICAL PROXY ONLY. No canonical model, story or production-ready animations. */
UCLASS()
class GENESIS_API AGenesisPrototypeCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AGenesisPrototypeCharacter();
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;
protected:
    void MoveForward(float Value);
    void MoveRight(float Value);
    UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> SpringArm;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> FollowCamera;
};
