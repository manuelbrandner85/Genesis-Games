#include "GenesisPrototypeCharacter.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/PlayerController.h"
#include "Engine/LocalPlayer.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"

namespace
{
    UInputAction* MakeAction(UObject* Outer, const TCHAR* Name, EInputActionValueType Type)
    {
        UInputAction* Action = NewObject<UInputAction>(Outer, Name, RF_Transient);
        Action->ValueType = Type;
        return Action;
    }

    template <typename TModifier>
    TModifier* AddModifier(FEnhancedActionKeyMapping& Mapping, UObject* Outer)
    {
        TModifier* Modifier = NewObject<TModifier>(Outer, NAME_None, RF_Transient);
        Mapping.Modifiers.Add(Modifier);
        return Modifier;
    }
}

FGenesisPrototypeInput FGenesisPrototypeInput::Create(UObject* Outer)
{
    FGenesisPrototypeInput Out;
    Out.Context = NewObject<UInputMappingContext>(Outer, TEXT("IMC_GenesisPrototype"), RF_Transient);
    Out.Move = MakeAction(Outer, TEXT("IA_Move"), EInputActionValueType::Axis2D);
    Out.Look = MakeAction(Outer, TEXT("IA_Look"), EInputActionValueType::Axis2D);
    Out.Jump = MakeAction(Outer, TEXT("IA_Jump"), EInputActionValueType::Boolean);
    UInputMappingContext* C = Out.Context;

    // Move: X = right, Y = forward. Keys deliver X, so forward/back are swizzled onto Y.
    AddModifier<UInputModifierSwizzleAxis>(C->MapKey(Out.Move, EKeys::W), C);
    {
        FEnhancedActionKeyMapping& S = C->MapKey(Out.Move, EKeys::S);
        AddModifier<UInputModifierSwizzleAxis>(S, C);
        AddModifier<UInputModifierNegate>(S, C);
    }
    AddModifier<UInputModifierNegate>(C->MapKey(Out.Move, EKeys::A), C);
    C->MapKey(Out.Move, EKeys::D);
    AddModifier<UInputModifierDeadZone>(C->MapKey(Out.Move, EKeys::Gamepad_Left2D), C);

    // Look: mouse delta as is (Y negated: mouse up = look up); stick scaled to degrees per second.
    AddModifier<UInputModifierNegate>(C->MapKey(Out.Look, EKeys::Mouse2D), C)->bX = false;
    {
        FEnhancedActionKeyMapping& Stick = C->MapKey(Out.Look, EKeys::Gamepad_Right2D);
        AddModifier<UInputModifierDeadZone>(Stick, C);
        AddModifier<UInputModifierNegate>(Stick, C)->bX = false;
        AddModifier<UInputModifierScalar>(Stick, C)->Scalar = FVector(GamepadLookRateDegPerSec, GamepadLookRateDegPerSec, 1.f);
        AddModifier<UInputModifierScaleByDeltaTime>(Stick, C);
    }

    C->MapKey(Out.Jump, EKeys::SpaceBar);
    C->MapKey(Out.Jump, EKeys::Gamepad_FaceButton_Bottom);
    return Out;
}

AGenesisPrototypeCharacter::AGenesisPrototypeCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
    bUseControllerRotationYaw = false;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    SpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    SpringArm->SetupAttachment(RootComponent);
    SpringArm->TargetArmLength = 280.f;
    SpringArm->bUsePawnControlRotation = true;
    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(SpringArm, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;
}

void AGenesisPrototypeCharacter::EnsureInputSetup()
{
    if (!InputSetup.Context) {
        InputSetup = FGenesisPrototypeInput::Create(this);
    }
}

void AGenesisPrototypeCharacter::NotifyControllerChanged()
{
    Super::NotifyControllerChanged();
    const APlayerController* PC = Cast<APlayerController>(Controller);
    if (!PC || !PC->GetLocalPlayer()) {
        return;
    }
    if (UEnhancedInputLocalPlayerSubsystem* Subsystem = PC->GetLocalPlayer()->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>()) {
        EnsureInputSetup();
        Subsystem->AddMappingContext(InputSetup.Context, 0);
    }
}

void AGenesisPrototypeCharacter::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    UEnhancedInputComponent* Enhanced = Cast<UEnhancedInputComponent>(Input);
    if (!ensureMsgf(Enhanced, TEXT("DefaultInputComponentClass must be EnhancedInputComponent"))) {
        return;
    }
    EnsureInputSetup();
    Enhanced->BindAction(InputSetup.Move, ETriggerEvent::Triggered, this, &AGenesisPrototypeCharacter::Move);
    Enhanced->BindAction(InputSetup.Look, ETriggerEvent::Triggered, this, &AGenesisPrototypeCharacter::Look);
    Enhanced->BindAction(InputSetup.Jump, ETriggerEvent::Started, this, &ACharacter::Jump);
    Enhanced->BindAction(InputSetup.Jump, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
}

void AGenesisPrototypeCharacter::Move(const FInputActionValue& Value)
{
    const FVector2D Axis = Value.Get<FVector2D>();
    if (Controller && !Axis.IsNearlyZero()) {
        const FRotationMatrix Yaw(FRotator(0.f, Controller->GetControlRotation().Yaw, 0.f));
        AddMovementInput(Yaw.GetUnitAxis(EAxis::X), Axis.Y);
        AddMovementInput(Yaw.GetUnitAxis(EAxis::Y), Axis.X);
    }
}

void AGenesisPrototypeCharacter::Look(const FInputActionValue& Value)
{
    const FVector2D Axis = Value.Get<FVector2D>();
    AddControllerYawInput(Axis.X);
    AddControllerPitchInput(Axis.Y);
}
