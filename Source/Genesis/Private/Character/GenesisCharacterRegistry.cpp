#include "Character/GenesisCharacterRegistry.h"

#include "Animation/AnimBlueprintGeneratedClass.h"
#include "Animation/AnimInstance.h"
#include "Animation/Skeleton.h"
#include "Character/GenesisCharacterAppearance.h"
#include "Engine/SkeletalMesh.h"
#include "Genesis.h"

const FGenesisCharacterRegistryEntry* UGenesisCharacterRegistry::FindEntry(FName CharacterAssetId)
{
	for (const FGenesisCharacterRegistryEntry& Entry : GetDefault<UGenesisCharacterRegistry>()->Entries)
	{
		if (Entry.CharacterAssetId == CharacterAssetId)
		{
			return &Entry;
		}
	}
	UE_LOG(LogGenesis, Warning, TEXT("Figur '%s' ist nicht in der Registry eingetragen."), *CharacterAssetId.ToString());
	return nullptr;
}

bool UGenesisCharacterRegistry::MeasureMesh(const USkeletalMesh* Mesh, FName AnchorBone, FGenesisMeasuredProportions& Out)
{
	if (!Mesh)
	{
		return false;
	}

	const FBox Box = Mesh->GetImportedBounds().GetBox();
	Out.HeightCm = Box.Max.Z - Box.Min.Z;
	Out.FootZCm = Box.Min.Z;

	const FReferenceSkeleton& RefSkeleton = Mesh->GetRefSkeleton();
	int32 BoneIndex = RefSkeleton.FindBoneIndex(AnchorBone);
	if (BoneIndex == INDEX_NONE)
	{
		Out.AnchorHeightCm = 0.f;
		return false;
	}

	// Komponentenraum-Position des Knochens im Referenz-Pose.
	FTransform ComponentSpace = RefSkeleton.GetRefBonePose()[BoneIndex];
	for (int32 Parent = RefSkeleton.GetParentIndex(BoneIndex); Parent != INDEX_NONE; Parent = RefSkeleton.GetParentIndex(Parent))
	{
		ComponentSpace = ComponentSpace * RefSkeleton.GetRefBonePose()[Parent];
	}
	Out.AnchorHeightCm = ComponentSpace.GetLocation().Z - Box.Min.Z;
	return true;
}

bool UGenesisCharacterRegistry::ValidateAppearance(const UGenesisCharacterAppearance* Appearance, const FGenesisProportionContract& Contract,
	TArray<FString>& OutErrors, FGenesisMeasuredProportions* OutMeasured)
{
	OutErrors.Reset();
	if (!Appearance)
	{
		OutErrors.Add(TEXT("Kein Aussehen."));
		return false;
	}

	USkeletalMesh* Mesh = Appearance->Mesh.LoadSynchronous();
	if (!Mesh)
	{
		OutErrors.Add(FString::Printf(TEXT("Mesh '%s' nicht ladbar."), *Appearance->Mesh.ToString()));
		return false;
	}

	FGenesisMeasuredProportions Measured;
	if (!MeasureMesh(Mesh, Contract.CameraAnchorBone, Measured))
	{
		OutErrors.Add(FString::Printf(TEXT("Kameraanker-Knochen '%s' fehlt."), *Contract.CameraAnchorBone.ToString()));
	}
	if (OutMeasured)
	{
		*OutMeasured = Measured;
	}

	if (FMath::Abs(Measured.HeightCm - Contract.ExpectedHeightCm) > Contract.HeightToleranceCm)
	{
		OutErrors.Add(FString::Printf(TEXT("Hoehe %.1f cm ausserhalb Vertrag %.1f +/- %.1f cm."),
			Measured.HeightCm, Contract.ExpectedHeightCm, Contract.HeightToleranceCm));
	}
	if (FMath::Abs(Measured.AnchorHeightCm - Contract.AnchorHeightCm) > Contract.AnchorHeightToleranceCm)
	{
		OutErrors.Add(FString::Printf(TEXT("Ankerhoehe %.1f cm ausserhalb Vertrag %.1f +/- %.1f cm."),
			Measured.AnchorHeightCm, Contract.AnchorHeightCm, Contract.AnchorHeightToleranceCm));
	}

	const FReferenceSkeleton& RefSkeleton = Mesh->GetRefSkeleton();
	for (const FName Bone : Contract.RequiredBones)
	{
		if (RefSkeleton.FindBoneIndex(Bone) == INDEX_NONE)
		{
			OutErrors.Add(FString::Printf(TEXT("Pflichtknochen '%s' fehlt."), *Bone.ToString()));
		}
	}

	if (!Contract.RequiredSkeleton.IsNull() && Mesh->GetSkeleton() != Contract.RequiredSkeleton.LoadSynchronous())
	{
		OutErrors.Add(FString::Printf(TEXT("Skelett '%s' statt vertraglich '%s'."),
			*GetNameSafe(Mesh->GetSkeleton()), *Contract.RequiredSkeleton.ToString()));
	}

	if (!Appearance->AnimClass.IsNull())
	{
		UClass* AnimClass = Appearance->AnimClass.LoadSynchronous();
		const UAnimBlueprintGeneratedClass* AnimBPClass = Cast<UAnimBlueprintGeneratedClass>(AnimClass);
		if (!AnimClass)
		{
			OutErrors.Add(FString::Printf(TEXT("AnimClass '%s' nicht ladbar."), *Appearance->AnimClass.ToString()));
		}
		else if (AnimBPClass && AnimBPClass->TargetSkeleton && AnimBPClass->TargetSkeleton != Mesh->GetSkeleton())
		{
			bool bCompatible = false;
#if WITH_EDITOR
			bCompatible = AnimBPClass->TargetSkeleton->IsCompatibleForEditor(Mesh->GetSkeleton());
#endif
			if (!bCompatible)
			{
				OutErrors.Add(FString::Printf(TEXT("AnimClass erwartet Skelett '%s', Mesh hat '%s'."),
					*GetNameSafe(AnimBPClass->TargetSkeleton), *GetNameSafe(Mesh->GetSkeleton())));
			}
		}
	}

	// Die Figur muss aufrecht stehen: nur Gier um die Hochachse ist erlaubt.
	const FRotator MeshRotation = Appearance->MeshRelativeTransform.Rotator();
	if (FMath::Abs(MeshRotation.Pitch) > 0.5f || FMath::Abs(MeshRotation.Roll) > 0.5f)
	{
		OutErrors.Add(FString::Printf(TEXT("Mesh nicht aufrecht (Neigung %.1f, Rollen %.1f Grad)."), MeshRotation.Pitch, MeshRotation.Roll));
	}

	// Fusssohle muss auf dem Kapselboden stehen, sonst schwebt oder versinkt die Figur.
	const float FootInCapsule = Appearance->MeshRelativeTransform.GetLocation().Z + Measured.FootZCm * Appearance->MeshRelativeTransform.GetScale3D().Z;
	if (FMath::Abs(FootInCapsule + Appearance->CapsuleHalfHeight) > 1.f)
	{
		OutErrors.Add(FString::Printf(TEXT("Fusssohle bei %.1f cm, Kapselboden bei %.1f cm."), FootInCapsule, -Appearance->CapsuleHalfHeight));
	}
	if (Appearance->CapsuleHalfHeight * 2.f > Measured.HeightCm + 5.f)
	{
		OutErrors.Add(FString::Printf(TEXT("Kapsel (%.1f cm) hoeher als die Figur (%.1f cm)."), Appearance->CapsuleHalfHeight * 2.f, Measured.HeightCm));
	}

	return OutErrors.Num() == 0;
}

FGenesisMeasuredProportions UGenesisCharacterLibrary::MeasureSkeletalMesh(USkeletalMesh* Mesh, FName AnchorBone)
{
	FGenesisMeasuredProportions Out;
	UGenesisCharacterRegistry::MeasureMesh(Mesh, AnchorBone, Out);
	return Out;
}

TArray<FString> UGenesisCharacterLibrary::ValidateAppearanceForCharacter(UGenesisCharacterAppearance* Appearance, FName CharacterAssetId)
{
	TArray<FString> Errors;
	const FGenesisCharacterRegistryEntry* Entry = UGenesisCharacterRegistry::FindEntry(CharacterAssetId);
	if (!Entry)
	{
		Errors.Add(TEXT("Figur nicht in der Registry."));
		return Errors;
	}
	UGenesisCharacterRegistry::ValidateAppearance(Appearance, Entry->Contract, Errors);
	return Errors;
}
