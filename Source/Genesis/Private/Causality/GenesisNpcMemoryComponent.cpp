#include "Causality/GenesisNpcMemoryComponent.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Save/GenesisSaveSubsystem.h"

const FGenesisSaveBundle* UGenesisNpcMemoryComponent::GetBundle() const
{
	const UGameInstance* GameInstance = GetWorld() ? GetWorld()->GetGameInstance() : nullptr;
	const UGenesisSaveSubsystem* Save = GameInstance ? GameInstance->GetSubsystem<UGenesisSaveSubsystem>() : nullptr;
	return Save ? &Save->GetCurrent() : nullptr;
}

EGenesisDisposition UGenesisNpcMemoryComponent::GetDispositionTowardPlayer() const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	if (!Bundle)
	{
		return EGenesisDisposition::Neutral;
	}
	return FGenesisCausality::ToDisposition(FGenesisCausality::GetAttitude(*Bundle, NpcId, FGenesisCausality::PlayerSubjectId(Bundle->Life.LifeIndex)));
}

FGenesisAttitude UGenesisNpcMemoryComponent::GetAttitudeToward(FName SubjectId) const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	return Bundle ? FGenesisCausality::GetAttitude(*Bundle, NpcId, SubjectId) : FGenesisAttitude();
}

TArray<FGenesisNpcMemory> UGenesisNpcMemoryComponent::GetSalientMemories(int32 MaxCount, float MinSalience) const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	if (!Bundle)
	{
		return {};
	}
	TArray<FGenesisNpcMemory> Memories = FGenesisCausality::GetMemories(*Bundle, NpcId, Bundle->World.WorldDateTime, *GetDefault<UGenesisCausalitySettings>(), MinSalience);
	if (Memories.Num() > MaxCount)
	{
		Memories.SetNum(MaxCount);
	}
	return Memories;
}

bool UGenesisNpcMemoryComponent::Remembers(FName EventId) const
{
	const FGenesisSaveBundle* Bundle = GetBundle();
	const FGenesisNpcState* Npc = Bundle ? FGenesisCausality::FindNpc(*Bundle, NpcId) : nullptr;
	return Npc && Npc->Memories.ContainsByPredicate([EventId](const FGenesisNpcMemory& M) { return M.EventId == EventId; });
}
