#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GenesisCharacterAppearance.generated.h"

class USkeletalMesh;
class USkeleton;
class UAnimInstance;
class UMaterialInterface;
class UPhysicsAsset;

/**
 * Verbindlicher Proportions- und Kameravertrag einer Figur.
 * Ein neues Modell darf eine Figur nur ersetzen, wenn es diesen Vertrag erfuellt,
 * damit Kameras, Interaktionen und Filmszenen ihre Bildkontinuitaet behalten.
 */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisProportionContract
{
	GENERATED_BODY()

	/** Koerpergroesse im Referenz-Pose (Fusssohle bis Scheitel), cm. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Contract")
	float ExpectedHeightCm = 180.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Contract")
	float HeightToleranceCm = 2.f;

	/** Hoehe des Kameraanker-Knochens ueber der Fusssohle im Referenz-Pose, cm. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Contract")
	float AnchorHeightCm = 160.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Contract")
	float AnchorHeightToleranceCm = 2.f;

	/** Knochen, an dem Kamera- und Blickregie haengt. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Contract")
	FName CameraAnchorBone = TEXT("head");

	/** Knochen, die Animation, IK, Interaktion und Physik voraussetzen. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Contract")
	TArray<FName> RequiredBones;

	/** Wenn gesetzt, muss das Mesh genau dieses Skelett benutzen (sonst ist ein Retargeter Pflicht). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Genesis|Contract")
	TSoftObjectPtr<USkeleton> RequiredSkeleton;
};

/** Gemessene Werte eines Meshes, Grundlage fuer Vertrag und Austauschpruefung. */
USTRUCT(BlueprintType)
struct GENESIS_API FGenesisMeasuredProportions
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Genesis|Contract")
	float HeightCm = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Genesis|Contract")
	float AnchorHeightCm = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Genesis|Contract")
	float FootZCm = 0.f;
};

/**
 * Das austauschbare Aussehen einer Figur. Spielsysteme kennen nur die CharacterAssetId;
 * welches Mesh, welche Animation und welche Materialien dahinterstehen, steht ausschliesslich hier.
 */
UCLASS(BlueprintType)
class GENESIS_API UGenesisCharacterAppearance : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/** Freigabestufe des Aussehens (Proxy, Master in Arbeit, freigegeben). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Appearance")
	FName ReleaseState = TEXT("PROXY");

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Appearance")
	TSoftObjectPtr<USkeletalMesh> Mesh;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Appearance")
	TSoftClassPtr<UAnimInstance> AnimClass;

	/** Leere Eintraege behalten das Material des Meshes. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Appearance")
	TArray<TSoftObjectPtr<UMaterialInterface>> MaterialOverrides;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Appearance")
	TSoftObjectPtr<UPhysicsAsset> PhysicsAssetOverride;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Appearance")
	float CapsuleRadius = 34.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Appearance")
	float CapsuleHalfHeight = 90.f;

	/** Lage des Meshes relativ zur Kapsel (Fusssohle auf Kapselboden, Blick nach +X). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Appearance")
	FTransform MeshRelativeTransform = FTransform(FRotator(0.f, -90.f, 0.f), FVector(0.f, 0.f, -90.f));
};
