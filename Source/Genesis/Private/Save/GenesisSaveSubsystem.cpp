#include "Save/GenesisSaveSubsystem.h"

#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Genesis.h"
#include "Save/GenesisSaveStore.h"
#include "Time/GenesisTimeTypes.h"

namespace
{
	/** Kartenname ohne PIE-Praefix, damit Spielstaende aus Editor-Test und Spiel zusammenpassen. */
	FName GetMapId(const UWorld* World)
	{
		return FName(*UWorld::RemovePIEPrefix(World->GetOutermost()->GetName()));
	}
}

void UGenesisSaveSubsystem::StartNewSoul(FName BodyAssetId, FDateTime WorldDateTime)
{
	Current = FGenesisSaveBundle();
	Current.Soul.SoulId = FGuid::NewGuid();
	Current.World.WorldSeed = FMath::Rand();
	Current.World.WorldDateTime = FGenesisLifeCycle::ToSavePrecision(WorldDateTime);
	Current.Life.LifeIndex = 0;
	Current.Life.BodyAssetId = BodyAssetId;
	Current.Life.ConceptionDateTime = Current.World.WorldDateTime;
	Current.Life.bBorn = false;
	Current.Life.Stage = EGenesisLifeStage::Conception;
}

void UGenesisSaveSubsystem::StartTestLife(FName BodyAssetId, FDateTime WorldDateTime, float AgeYears)
{
	StartNewSoul(BodyAssetId, WorldDateTime);
	Current.Life.bBorn = true;
	Current.World.WorldDateTime = FGenesisLifeCycle::ToSavePrecision(WorldDateTime);
	Current.Life.BirthDateTime = FGenesisLifeCycle::ToSavePrecision(WorldDateTime - FTimespan::FromDays(AgeYears * FGenesisLifeCycle::DaysPerYear));
	Current.Life.ConceptionDateTime = Current.Life.BirthDateTime - FTimespan::FromDays(GetDefault<UGenesisTimeSettings>()->BirthStartDay);
	Current.Life.Stage = FGenesisLifeCycle::ComputeStage(Current.Life, WorldDateTime, *GetDefault<UGenesisTimeSettings>());
}

FString UGenesisSaveSubsystem::GetDirectory() const
{
	return DirectoryOverride.IsEmpty() ? FGenesisSaveStore::DefaultDirectory() : DirectoryOverride;
}

void UGenesisSaveSubsystem::CaptureFromWorld()
{
	const UWorld* World = GetGameInstance() ? GetGameInstance()->GetWorld() : nullptr;
	const APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
	if (const APawn* Pawn = PC ? PC->GetPawn() : nullptr)
	{
		Current.Life.PlayerTransform = Pawn->GetActorTransform();
		Current.Life.LocationId = GetMapId(World);
	}
}

void UGenesisSaveSubsystem::ApplyToWorld() const
{
	const UWorld* World = GetGameInstance() ? GetGameInstance()->GetWorld() : nullptr;
	APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
	APawn* Pawn = PC ? PC->GetPawn() : nullptr;
	if (!Pawn)
	{
		return;
	}
	if (!Current.Life.LocationId.IsNone() && Current.Life.LocationId != GetMapId(World))
	{
		// Levelwechsel beim Laden kommt mit dem Weltaufbau; bis dahin nicht in eine fremde Karte teleportieren.
		UE_LOG(LogGenesis, Warning, TEXT("Spielstand liegt in '%s', aktuelle Karte ist '%s'; Position nicht gesetzt."),
			*Current.Life.LocationId.ToString(), *GetMapId(World).ToString());
		return;
	}
	Pawn->SetActorLocationAndRotation(Current.Life.PlayerTransform.GetLocation(), Current.Life.PlayerTransform.GetRotation(),
		false, nullptr, ETeleportType::TeleportPhysics);
	PC->SetControlRotation(FRotator(0.f, Current.Life.PlayerTransform.Rotator().Yaw, 0.f));
}

EGenesisSaveResult UGenesisSaveSubsystem::SaveToSlot(const FString& Slot)
{
	CaptureFromWorld();
	const EGenesisSaveResult Result = FGenesisSaveStore(GetDirectory()).Save(Slot, Current);
	UE_LOG(LogGenesis, Log, TEXT("Speichern '%s' -> %s (Sequenz %lld)"),
		*Slot, *UEnum::GetValueAsString(Result), Current.Sequence);
	return Result;
}

EGenesisSaveResult UGenesisSaveSubsystem::LoadFromSlot(const FString& Slot)
{
	FGenesisSaveBundle Loaded;
	const EGenesisSaveResult Result = FGenesisSaveStore(GetDirectory()).Load(Slot, Loaded);
	if (Result == EGenesisSaveResult::Ok)
	{
		Current = MoveTemp(Loaded);
		ApplyToWorld();
	}
	UE_LOG(LogGenesis, Log, TEXT("Laden '%s' -> %s (Sequenz %lld)"),
		*Slot, *UEnum::GetValueAsString(Result), Current.Sequence);
	return Result;
}
