#include "Input/GenesisInputSet.h"

#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"

namespace GenesisInput
{
	static UInputAction* MakeAction(UObject* Outer, const TCHAR* Name, EInputActionValueType Type)
	{
		UInputAction* Action = NewObject<UInputAction>(Outer, Name);
		Action->ValueType = Type;
		return Action;
	}

	template <typename TModifier>
	static TModifier* AddModifier(UInputMappingContext* Context, FEnhancedActionKeyMapping& Mapping)
	{
		TModifier* Modifier = NewObject<TModifier>(Context);
		Mapping.Modifiers.Add(Modifier);
		return Modifier;
	}

	static void MapForward(UInputMappingContext* Context, UInputAction* Move, const FKey& Key, bool bNegate)
	{
		FEnhancedActionKeyMapping& Mapping = Context->MapKey(Move, Key);
		AddModifier<UInputModifierSwizzleAxis>(Context, Mapping)->Order = EInputAxisSwizzle::YXZ;
		if (bNegate)
		{
			AddModifier<UInputModifierNegate>(Context, Mapping);
		}
	}

	static void MapRight(UInputMappingContext* Context, UInputAction* Move, const FKey& Key, bool bNegate)
	{
		FEnhancedActionKeyMapping& Mapping = Context->MapKey(Move, Key);
		if (bNegate)
		{
			AddModifier<UInputModifierNegate>(Context, Mapping);
		}
	}
}

UGenesisInputSet* UGenesisInputSet::CreateDefault(UObject* Outer)
{
	using namespace GenesisInput;

	UGenesisInputSet* Set = NewObject<UGenesisInputSet>(Outer);
	Set->Move = MakeAction(Set, TEXT("IA_Move"), EInputActionValueType::Axis2D);
	Set->Look = MakeAction(Set, TEXT("IA_Look"), EInputActionValueType::Axis2D);
	Set->Jump = MakeAction(Set, TEXT("IA_Jump"), EInputActionValueType::Boolean);
	Set->RunHold = MakeAction(Set, TEXT("IA_RunHold"), EInputActionValueType::Boolean);
	Set->RunToggle = MakeAction(Set, TEXT("IA_RunToggle"), EInputActionValueType::Boolean);

	UInputMappingContext* Context = NewObject<UInputMappingContext>(Set, TEXT("IMC_GenesisDefault"));
	Set->Context = Context;

	// Bewegung: WASD, Pfeiltasten, linker Stick.
	MapForward(Context, Set->Move, EKeys::W, false);
	MapForward(Context, Set->Move, EKeys::S, true);
	MapRight(Context, Set->Move, EKeys::D, false);
	MapRight(Context, Set->Move, EKeys::A, true);
	MapForward(Context, Set->Move, EKeys::Up, false);
	MapForward(Context, Set->Move, EKeys::Down, true);
	MapRight(Context, Set->Move, EKeys::Right, false);
	MapRight(Context, Set->Move, EKeys::Left, true);
	{
		FEnhancedActionKeyMapping& Stick = Context->MapKey(Set->Move, EKeys::Gamepad_Left2D);
		UInputModifierDeadZone* DeadZone = AddModifier<UInputModifierDeadZone>(Context, Stick);
		DeadZone->LowerThreshold = 0.15f;
		DeadZone->Type = EDeadZoneType::Radial;
	}

	// Kamera: Maus und rechter Stick. Ohne Legacy-Skalierung bedeutet +Y direkt "nach oben schauen".
	{
		FEnhancedActionKeyMapping& Mouse = Context->MapKey(Set->Look, EKeys::Mouse2D);
		// Mit Mausempfindlichkeit 0,07 ergibt das ca. 0,175 Grad pro Pixel (Legacy-Skalierung ist aus).
		UInputModifierScalar* Scalar = AddModifier<UInputModifierScalar>(Context, Mouse);
		Scalar->Scalar = FVector(MouseLookScale, MouseLookScale, 1.0);
	}
	{
		FEnhancedActionKeyMapping& Stick = Context->MapKey(Set->Look, EKeys::Gamepad_Right2D);
		UInputModifierDeadZone* DeadZone = AddModifier<UInputModifierDeadZone>(Context, Stick);
		DeadZone->LowerThreshold = 0.12f;
		DeadZone->Type = EDeadZoneType::Radial;
		// Bildratenunabhaengige Drehgeschwindigkeit.
		AddModifier<UInputModifierScaleByDeltaTime>(Context, Stick);
		UInputModifierScalar* Scalar = AddModifier<UInputModifierScalar>(Context, Stick);
		Scalar->Scalar = FVector(GamepadLookDegreesPerSecond, GamepadLookDegreesPerSecond, 1.0);
	}

	Context->MapKey(Set->Jump, EKeys::SpaceBar);
	Context->MapKey(Set->Jump, EKeys::Gamepad_FaceButton_Bottom);

	Context->MapKey(Set->RunHold, EKeys::LeftShift);
	Context->MapKey(Set->RunToggle, EKeys::Gamepad_LeftThumbstick);

	Set->Interact = MakeAction(Set, TEXT("IA_Interact"), EInputActionValueType::Boolean);
	Context->MapKey(Set->Interact, EKeys::E);
	Context->MapKey(Set->Interact, EKeys::Gamepad_FaceButton_Left);

	const FKey ChoiceKeys[] = { EKeys::One, EKeys::Two, EKeys::Three, EKeys::Four };
	const FKey ChoicePad[] = { EKeys::Gamepad_DPad_Up, EKeys::Gamepad_DPad_Right, EKeys::Gamepad_DPad_Down, EKeys::Gamepad_DPad_Left };
	for (int32 i = 0; i < 4; ++i)
	{
		UInputAction* Choice = MakeAction(Set, *FString::Printf(TEXT("IA_Choice%d"), i + 1), EInputActionValueType::Boolean);
		Context->MapKey(Choice, ChoiceKeys[i]);
		Context->MapKey(Choice, ChoicePad[i]);
		Set->Choices.Add(Choice);
	}

	return Set;
}
