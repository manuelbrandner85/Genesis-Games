#include "World/GenesisWorld.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Save/GenesisSaveSubsystem.h"

const FGenesisWorldObjectDef* UGenesisWorldSettings::FindObject(FName ObjectId) const
{
	return Objects.FindByPredicate([ObjectId](const FGenesisWorldObjectDef& D) { return D.ObjectId == ObjectId; });
}

// ---------------------------------------------------------------- Zustand

namespace
{
	/** "VS01_BRIDGE_01.Closed" -> (VS01_BRIDGE_01, Closed), wenn der Teil vor dem Punkt ein Weltobjekt ist. */
	bool SplitObjectKey(FName Key, FName& OutObject, FName& OutValue)
	{
		FString Left, Right;
		if (!Key.ToString().Split(TEXT("."), &Left, &Right) || !FGenesisWorldStateLib::IsWorldObjectId(FName(*Left)))
		{
			return false;
		}
		OutObject = FName(*Left);
		OutValue = FName(*Right);
		return true;
	}

	bool SplitKnowledgeKey(FName Key, FName& OutName)
	{
		const FString Text = Key.ToString();
		if (!Text.StartsWith(TEXT("Know.")))
		{
			return false;
		}
		OutName = FName(*Text.RightChop(5));
		return true;
	}
}

bool FGenesisWorldStateLib::IsWorldObjectId(FName Id)
{
	return !Id.IsNone() && GetDefault<UGenesisWorldSettings>()->FindObject(Id) != nullptr;
}

const FGenesisWorldObjectState* FGenesisWorldStateLib::FindObject(const FGenesisSaveBundle& Bundle, FName ObjectId)
{
	return Bundle.World.Objects.FindByPredicate([ObjectId](const FGenesisWorldObjectState& O) { return O.ObjectId == ObjectId; });
}

int32 FGenesisWorldStateLib::GetObjectValue(const FGenesisSaveBundle& Bundle, FName ObjectId, FName Key)
{
	if (const FGenesisWorldObjectState* State = FindObject(Bundle, ObjectId))
	{
		return State->Values.FindRef(Key);
	}
	const FGenesisWorldObjectDef* Def = GetDefault<UGenesisWorldSettings>()->FindObject(ObjectId);
	return Def ? Def->InitialValues.FindRef(Key) : 0;
}

bool FGenesisWorldStateLib::SetObjectValue(FGenesisSaveBundle& Bundle, FName ObjectId, FName Key, int32 Value, FName EventId)
{
	FGenesisWorldObjectState* State = Bundle.World.Objects.FindByPredicate([ObjectId](const FGenesisWorldObjectState& O) { return O.ObjectId == ObjectId; });
	if (!State)
	{
		State = &Bundle.World.Objects.AddDefaulted_GetRef();
		State->ObjectId = ObjectId;
		if (const FGenesisWorldObjectDef* Def = GetDefault<UGenesisWorldSettings>()->FindObject(ObjectId))
		{
			State->Values = Def->InitialValues;
		}
	}
	const int32* Existing = State->Values.Find(Key);
	if (Existing ? *Existing == Value : Value == 0)
	{
		return false;
	}
	State->Values.Add(Key, Value);
	++State->Version;
	State->LastEventId = EventId;
	State->LastChange = Bundle.World.WorldDateTime;
	return true;
}

int32 FGenesisWorldStateLib::GetValue(const FGenesisSaveBundle& Bundle, FName Key)
{
	FName Object, Value;
	if (SplitKnowledgeKey(Key, Value))
	{
		return Bundle.Life.Knowledge.FindRef(Value);
	}
	if (SplitObjectKey(Key, Object, Value))
	{
		return GetObjectValue(Bundle, Object, Value);
	}
	return Bundle.World.EventFlags.FindRef(Key);
}

bool FGenesisWorldStateLib::SetValue(FGenesisSaveBundle& Bundle, FName Key, int32 Value, FName EventId)
{
	FName Object, Name;
	if (SplitKnowledgeKey(Key, Name))
	{
		const bool bChanged = Bundle.Life.Knowledge.FindRef(Name) != Value;
		Bundle.Life.Knowledge.Add(Name, Value);
		return bChanged;
	}
	if (SplitObjectKey(Key, Object, Name))
	{
		return SetObjectValue(Bundle, Object, Name, Value, EventId);
	}
	const bool bChanged = Bundle.World.EventFlags.FindRef(Key) != Value;
	Bundle.World.EventFlags.Add(Key, Value);
	return bChanged;
}

// ---------------------------------------------------------------- Actor

AGenesisWorldObject::AGenesisWorldObject()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickInterval = 0.25f;
	Visual = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Visual"));
	RootComponent = Visual;
}

void AGenesisWorldObject::BeginPlay()
{
	Super::BeginPlay();
	BaseZ = GetActorLocation().Z;
	ApplyState();
}

void AGenesisWorldObject::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	ApplyState();
}

void AGenesisWorldObject::ApplyState()
{
	const UGenesisSaveSubsystem* Save = GetGameInstance() ? GetGameInstance()->GetSubsystem<UGenesisSaveSubsystem>() : nullptr;
	if (!Save || !Save->HasActiveSoul())
	{
		return;
	}
	const FGenesisSaveBundle& Bundle = Save->GetCurrent();

	if (!HeightFollowsKey.IsNone())
	{
		FVector Location = GetActorLocation();
		Location.Z = BaseZ + float(FGenesisWorldStateLib::GetValue(Bundle, HeightFollowsKey));
		SetActorLocation(Location);
	}

	bool bShow = true;
	if (!ShowWhenKey.IsNone())
	{
		const int32 Value = FGenesisWorldStateLib::GetObjectValue(Bundle, ObjectId, ShowWhenKey);
		bShow = bShowWhenAtLeast ? Value >= ShowWhenValue : Value == ShowWhenValue;
	}
	if (bShow == bShown && bStateApplied)
	{
		return;
	}
	bShown = bShow;
	bStateApplied = true;
	Visual->SetVisibility(bShow, true);
	if (bBlockingWhenShown)
	{
		// Sperren und Truemmer blockieren dann auch die Wegfindung (dynamisches Navmesh baut neu).
		Visual->SetCollisionEnabled(bShow ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
		Visual->SetCanEverAffectNavigation(bShow);
	}
	else if (!ShowWhenKey.IsNone())
	{
		Visual->SetCollisionEnabled(bShow ? ECollisionEnabled::QueryOnly : ECollisionEnabled::NoCollision);
	}
}
