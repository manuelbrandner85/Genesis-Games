#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "GenesisPrototypeCharacter.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EnhancedInputComponent.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"

namespace
{
    constexpr EAutomationTestFlags GenesisTestFlags = EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::ProductFilter;

    const FEnhancedActionKeyMapping* FindMapping(const UInputMappingContext* Context, const UInputAction* Action, const FKey& Key)
    {
        for (const FEnhancedActionKeyMapping& Mapping : Context->GetMappings()) {
            if (Mapping.Action == Action && Mapping.Key == Key) {
                return &Mapping;
            }
        }
        return nullptr;
    }

    /** Runs a raw key value through the mapping's modifier chain, as the Enhanced Input pipeline does. */
    FVector Apply(const FEnhancedActionKeyMapping& Mapping, const FVector& Raw, float DeltaTime)
    {
        FInputActionValue Value(EInputActionValueType::Axis2D, Raw);
        for (const UInputModifier* Modifier : Mapping.Modifiers) {
            Value = Modifier->ModifyRaw(nullptr, Value, DeltaTime);
        }
        return Value.Get<FVector>();
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisInputMappingTest, "Genesis.Input.PrototypeMapping", GenesisTestFlags)
bool FGenesisInputMappingTest::RunTest(const FString&)
{
    const FGenesisPrototypeInput Input = FGenesisPrototypeInput::Create(GetTransientPackage());
    if (!TestNotNull(TEXT("Mapping context"), Input.Context.Get()) || !Input.Move || !Input.Look || !Input.Jump) {
        return false;
    }
    TestEqual(TEXT("Move is Axis2D"), Input.Move->ValueType, EInputActionValueType::Axis2D);
    TestEqual(TEXT("Look is Axis2D"), Input.Look->ValueType, EInputActionValueType::Axis2D);
    TestEqual(TEXT("Jump is Boolean"), Input.Jump->ValueType, EInputActionValueType::Boolean);
    TestEqual(TEXT("Number of key mappings"), Input.Context->GetMappings().Num(), 9);

    struct FCase { FKey Key; FVector Raw; FVector Expected; float DeltaTime; const UInputAction* Action; };
    const float Rate = FGenesisPrototypeInput::GamepadLookRateDegPerSec;
    const FCase Cases[] = {
        { EKeys::W, FVector(1, 0, 0), FVector(0, 1, 0), 0.f, Input.Move },
        { EKeys::S, FVector(1, 0, 0), FVector(0, -1, 0), 0.f, Input.Move },
        { EKeys::A, FVector(1, 0, 0), FVector(-1, 0, 0), 0.f, Input.Move },
        { EKeys::D, FVector(1, 0, 0), FVector(1, 0, 0), 0.f, Input.Move },
        { EKeys::Gamepad_Left2D, FVector(0, 1, 0), FVector(0, 1, 0), 0.f, Input.Move },
        { EKeys::Gamepad_Left2D, FVector(0.1, 0.1, 0), FVector::ZeroVector, 0.f, Input.Move },
        { EKeys::Mouse2D, FVector(3, 2, 0), FVector(3, -2, 0), 0.f, Input.Look },
        { EKeys::Gamepad_Right2D, FVector(1, 0, 0), FVector(Rate * 0.1f, 0, 0), 0.1f, Input.Look },
        { EKeys::Gamepad_Right2D, FVector(0, 1, 0), FVector(0, -Rate * 0.1f, 0), 0.1f, Input.Look },
        { EKeys::SpaceBar, FVector(1, 0, 0), FVector(1, 0, 0), 0.f, Input.Jump },
        { EKeys::Gamepad_FaceButton_Bottom, FVector(1, 0, 0), FVector(1, 0, 0), 0.f, Input.Jump },
    };
    for (const FCase& Case : Cases) {
        const FEnhancedActionKeyMapping* Mapping = FindMapping(Input.Context, Case.Action, Case.Key);
        if (!TestNotNull(*FString::Printf(TEXT("Mapping for %s"), *Case.Key.ToString()), Mapping)) {
            continue;
        }
        const FVector Result = Apply(*Mapping, Case.Raw, Case.DeltaTime);
        TestTrue(*FString::Printf(TEXT("%s %s -> %s (got %s)"), *Case.Key.ToString(), *Case.Raw.ToString(), *Case.Expected.ToString(), *Result.ToString()),
            Result.Equals(Case.Expected, 1e-4));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGenesisInputBindingTest, "Genesis.Input.PrototypeBindings", GenesisTestFlags)
bool FGenesisInputBindingTest::RunTest(const FString&)
{
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
    FWorldContext& WorldContext = GEngine->CreateNewWorldContext(EWorldType::Game);
    WorldContext.SetCurrentWorld(World);

    AGenesisPrototypeCharacter* Character = World->SpawnActor<AGenesisPrototypeCharacter>();
    if (TestNotNull(TEXT("Spawned prototype character"), Character)) {
        UEnhancedInputComponent* Component = NewObject<UEnhancedInputComponent>(Character);
        Character->SetupPlayerInputComponent(Component);
        const FGenesisPrototypeInput& Input = Character->GetPrototypeInput();
        int32 Move = 0, Look = 0, JumpStarted = 0, JumpCompleted = 0;
        for (const TUniquePtr<FEnhancedInputActionEventBinding>& Binding : Component->GetActionEventBindings()) {
            const UInputAction* Action = Binding->GetAction();
            const ETriggerEvent Event = Binding->GetTriggerEvent();
            Move += Action == Input.Move && Event == ETriggerEvent::Triggered;
            Look += Action == Input.Look && Event == ETriggerEvent::Triggered;
            JumpStarted += Action == Input.Jump && Event == ETriggerEvent::Started;
            JumpCompleted += Action == Input.Jump && Event == ETriggerEvent::Completed;
        }
        TestEqual(TEXT("Total bindings"), Component->GetActionEventBindings().Num(), 4);
        TestEqual(TEXT("Move bound on Triggered"), Move, 1);
        TestEqual(TEXT("Look bound on Triggered"), Look, 1);
        TestEqual(TEXT("Jump bound on Started"), JumpStarted, 1);
        TestEqual(TEXT("StopJumping bound on Completed"), JumpCompleted, 1);
    }

    GEngine->DestroyWorldContext(World);
    World->DestroyWorld(false);
    return true;
}
#endif
