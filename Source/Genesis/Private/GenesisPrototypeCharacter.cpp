#include "GenesisPrototypeCharacter.h"
#include "UI/GenesisUserSettings.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimInstance.h"
#include "Player/GenesisPlayerController.h"
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
    Out.Sprint = MakeAction(Outer, TEXT("IA_Sprint"), EInputActionValueType::Boolean);
    Out.SprintToggle = MakeAction(Outer, TEXT("IA_SprintToggle"), EInputActionValueType::Boolean);
    Out.Interact = MakeAction(Outer, TEXT("IA_Interact"), EInputActionValueType::Boolean);
    Out.Confirm = MakeAction(Outer, TEXT("IA_Confirm"), EInputActionValueType::Boolean);
    Out.ChoiceUp = MakeAction(Outer, TEXT("IA_ChoiceUp"), EInputActionValueType::Boolean);
    Out.ChoiceDown = MakeAction(Outer, TEXT("IA_ChoiceDown"), EInputActionValueType::Boolean);
    for (int32 I = 1; I <= 6; ++I) {
        Out.Choices.Add(MakeAction(Outer, *FString::Printf(TEXT("IA_Choice%d"), I), EInputActionValueType::Boolean));
    }
    Out.SaveGame = MakeAction(Outer, TEXT("IA_SaveGame"), EInputActionValueType::Boolean);
    Out.LoadGame = MakeAction(Outer, TEXT("IA_LoadGame"), EInputActionValueType::Boolean);
    Out.Pause = MakeAction(Outer, TEXT("IA_Pause"), EInputActionValueType::Boolean);
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
        AddModifier<UInputModifierDeadZone>(Stick, C)->LowerThreshold = LookDeadZone;
        AddModifier<UInputModifierNegate>(Stick, C)->bX = false;
        AddModifier<UInputModifierScalar>(Stick, C)->Scalar = FVector(GamepadLookRateDegPerSec, GamepadLookRateDegPerSec, 1.f);
        AddModifier<UInputModifierScaleByDeltaTime>(Stick, C);
    }

    C->MapKey(Out.Jump, EKeys::SpaceBar);
    C->MapKey(Out.Jump, EKeys::Gamepad_FaceButton_Bottom);

    // Sprint: held on the keyboard, toggled by clicking the left stick (as in most games).
    C->MapKey(Out.Sprint, EKeys::LeftShift);
    C->MapKey(Out.SprintToggle, EKeys::Gamepad_LeftThumbstick);

    // Interaction and conversations.
    C->MapKey(Out.Interact, EKeys::E);
    C->MapKey(Out.Interact, EKeys::Gamepad_FaceButton_Left);
    C->MapKey(Out.Confirm, EKeys::Enter);
    C->MapKey(Out.Confirm, EKeys::Gamepad_FaceButton_Bottom);    // = jump outside of conversations
    C->MapKey(Out.ChoiceUp, EKeys::Up);
    C->MapKey(Out.ChoiceUp, EKeys::Gamepad_DPad_Up);
    C->MapKey(Out.ChoiceDown, EKeys::Down);
    C->MapKey(Out.ChoiceDown, EKeys::Gamepad_DPad_Down);
    const FKey Digits[] = { EKeys::One, EKeys::Two, EKeys::Three, EKeys::Four, EKeys::Five, EKeys::Six };
    for (int32 I = 0; I < 6; ++I) {
        C->MapKey(Out.Choices[I], Digits[I]);
    }
    C->MapKey(Out.SaveGame, EKeys::F5);
    C->MapKey(Out.LoadGame, EKeys::F9);
    C->MapKey(Out.Pause, EKeys::Escape);
    C->MapKey(Out.Pause, EKeys::P);                  // Esc ends PIE in the editor
    C->MapKey(Out.Pause, EKeys::Gamepad_Special_Right);
    return Out;
}

AGenesisPrototypeCharacter::AGenesisPrototypeCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
    bUseControllerRotationYaw = false;
    GetCapsuleComponent()->InitCapsuleSize(42.f, 96.f);   // mannequin proxy contract (1.8 m adult)

    UCharacterMovementComponent* MoveComp = GetCharacterMovement();
    MoveComp->bOrientRotationToMovement = true;
    MoveComp->RotationRate = FRotator(0.f, 540.f, 0.f);
    MoveComp->MaxWalkSpeed = WalkSpeed;
    MoveComp->MinAnalogWalkSpeed = 20.f;
    MoveComp->BrakingDecelerationWalking = 1400.f;
    MoveComp->GroundFriction = 8.f;
    MoveComp->JumpZVelocity = FMath::Sqrt(2.f * 980.f * JumpHeight);   // v = sqrt(2 g h) -> ~297 cm/s
    MoveComp->AirControl = 0.25f;
    MoveComp->MaxStepHeight = 40.f;                                     // a high stair step
    MoveComp->SetWalkableFloorAngle(44.f);

    SpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    SpringArm->SetupAttachment(RootComponent);
    SpringArm->TargetArmLength = 280.f;
    SpringArm->SocketOffset = FVector(0.f, 45.f, 60.f);             // over the right shoulder
    SpringArm->bUsePawnControlRotation = true;
    SpringArm->bDoCollisionTest = true;
    SpringArm->bEnableCameraLag = true;
    SpringArm->CameraLagSpeed = 12.f;
    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(SpringArm, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;
    FollowCamera->SetFieldOfView(70.f);

    // Mannequin proxy: feet on the capsule bottom, facing +X.
    GetMesh()->SetRelativeLocationAndRotation(FVector(0.f, 0.f, -96.f), FRotator(0.f, -90.f, 0.f));
}

void AGenesisPrototypeCharacter::PostInitializeComponents()
{
    Super::PostInitializeComponents();
    if (USkeletalMesh* LoadedMesh = ProxyMesh.LoadSynchronous()) {
        GetMesh()->SetSkeletalMesh(LoadedMesh);
    }
    if (UClass* Anim = ProxyAnimClass.LoadSynchronous()) {
        GetMesh()->SetAnimInstanceClass(Anim);
    }
}

void AGenesisPrototypeCharacter::SetSprinting(bool bNewSprinting)
{
    bSprinting = bNewSprinting;
    GetCharacterMovement()->MaxWalkSpeed = bSprinting ? SprintSpeed : WalkSpeed;
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
    if (PC->PlayerCameraManager) {
        PC->PlayerCameraManager->ViewPitchMin = PitchMin;
        PC->PlayerCameraManager->ViewPitchMax = PitchMax;
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
    Enhanced->BindAction(InputSetup.Jump, ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::DoJump);
    Enhanced->BindAction(InputSetup.Jump, ETriggerEvent::Completed, this, &AGenesisPrototypeCharacter::DoStopJumping);
    Enhanced->BindAction(InputSetup.Sprint, ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::StartSprint);
    Enhanced->BindAction(InputSetup.Sprint, ETriggerEvent::Completed, this, &AGenesisPrototypeCharacter::StopSprint);
    Enhanced->BindAction(InputSetup.SprintToggle, ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::ToggleSprint);
    Enhanced->BindAction(InputSetup.Interact, ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::OnInteract);
    Enhanced->BindAction(InputSetup.Confirm, ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::OnConfirm);
    Enhanced->BindAction(InputSetup.ChoiceUp, ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::OnChoiceUp);
    Enhanced->BindAction(InputSetup.ChoiceDown, ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::OnChoiceDown);
    for (int32 I = 0; I < InputSetup.Choices.Num(); ++I) {
        Enhanced->BindAction(InputSetup.Choices[I], ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::OnChoice, I);
    }
    Enhanced->BindAction(InputSetup.SaveGame, ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::OnSave);
    Enhanced->BindAction(InputSetup.LoadGame, ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::OnLoad);
    Enhanced->BindAction(InputSetup.Pause, ETriggerEvent::Started, this, &AGenesisPrototypeCharacter::OnPause);
}

AGenesisPlayerController* AGenesisPrototypeCharacter::GenesisPC() const
{
    return Cast<AGenesisPlayerController>(Controller);
}

void AGenesisPrototypeCharacter::DoJump()
{
    const AGenesisPlayerController* PC = GenesisPC();
    if (!PC || !PC->IsInDialog()) {
        Jump();
    }
}

void AGenesisPrototypeCharacter::DoStopJumping() { StopJumping(); }
void AGenesisPrototypeCharacter::OnInteract() { if (AGenesisPlayerController* PC = GenesisPC()) PC->HandleInteract(); }
void AGenesisPrototypeCharacter::OnConfirm() { if (AGenesisPlayerController* PC = GenesisPC(); PC && PC->IsInDialog()) PC->ConfirmHighlight(); }
void AGenesisPrototypeCharacter::OnChoiceUp() { if (AGenesisPlayerController* PC = GenesisPC()) PC->MoveHighlight(-1); }
void AGenesisPrototypeCharacter::OnChoiceDown() { if (AGenesisPlayerController* PC = GenesisPC()) PC->MoveHighlight(1); }
void AGenesisPrototypeCharacter::OnChoice(int32 Index) { if (AGenesisPlayerController* PC = GenesisPC()) PC->Choose(Index); }
void AGenesisPrototypeCharacter::OnSave() { if (AGenesisPlayerController* PC = GenesisPC()) PC->SaveGame(); }
void AGenesisPrototypeCharacter::OnLoad() { if (AGenesisPlayerController* PC = GenesisPC()) PC->LoadGame(); }
void AGenesisPrototypeCharacter::OnPause() { if (AGenesisPlayerController* PC = GenesisPC()) PC->TogglePauseMenu(); }

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
    const UGenesisUserSettings* U = UGenesisUserSettings::Get();
    const float Sensitivity = U ? FMath::Clamp(U->CameraSensitivity, 0.3f, 2.f) : 1.f;
    AddControllerYawInput(Axis.X * Sensitivity);
    AddControllerPitchInput(Axis.Y * Sensitivity * (U && U->bInvertCameraY ? -1.f : 1.f));
}
