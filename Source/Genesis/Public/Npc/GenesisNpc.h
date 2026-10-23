#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GenesisNpc.generated.h"

struct FGenesisWorldEvent;

/**
 * A Flussdorf resident. Follows its daily schedule (FGenesisNpcSchedules) on the nav mesh and
 * learns about events only by perceiving them: within PerceptionRadius and line of sight.
 * At home it is inside the closed house (hidden, no collision) - private rooms are not open.
 */
UCLASS()
class GENESIS_API AGenesisNpc : public ACharacter
{
    GENERATED_BODY()
public:
    AGenesisNpc();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;

    UPROPERTY(EditAnywhere, Category = "Genesis") FName NpcID;
    UPROPERTY(EditAnywhere, Category = "Genesis") FText RoleName;
    /** Walking speed cm/s (people walk 1.2-1.5 m/s in a village). */
    UPROPERTY(EditAnywhere, Category = "Genesis") float WalkSpeed = 140.f;
    UPROPERTY(EditAnywhere, Category = "Genesis") float PerceptionRadius = 1500.f;

    void SetInsidePrivate(bool bInside);
    bool IsInsidePrivate() const { return bInsidePrivate; }
    /** True if this NPC can currently perceive the location (range + line of sight). */
    bool CanPerceive(const FVector& Location, const AActor* Subject) const;

private:
    void HandleWorldEvent(const FGenesisWorldEvent& Event);
    FDelegateHandle EventHandle;
    bool bInsidePrivate = false;
};
