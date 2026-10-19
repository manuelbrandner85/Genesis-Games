#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GenesisCharacter.generated.h"

class UCameraComponent;
class USpringArmComponent;
class UGenesisCharacterAppearance;
class UGenesisInputSet;
struct FGenesisProportionContract;
struct FInputActionValue;

/**
 * Spielbare oder NPC-Figur. Logik, Bewegung und Kamera liegen hier;
 * das Aussehen kommt ausschliesslich ueber die CharacterAssetId aus der Registry.
 */
UCLASS()
class GENESIS_API AGenesisCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AGenesisCharacter();

	/** Feste ID der Figur. Ein Modellwechsel aendert die Registry, nicht diese ID. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Genesis|Character")
	FName CharacterAssetId = TEXT("CHR_PLAYER_ADULT");

	/** Wendet das Aussehen der ID an (Mesh, Animation, Material, Kapsel, Kameraanker). */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Character")
	bool ApplyAppearance(FName InCharacterAssetId);

	/**
	 * Setzt ein Aussehen nur ein, wenn es den Vertrag der Figur erfuellt; sonst bleibt das bisherige Modell.
	 * Wird fuer Modellaustausch (Proxy -> Blender-Master) und dessen Regressionstest benutzt.
	 */
	bool TryApplyAppearanceAsset(UGenesisCharacterAppearance* Appearance, const FGenesisProportionContract& Contract, TArray<FString>& OutErrors);

	UFUNCTION(BlueprintPure, Category = "Genesis|Character")
	UGenesisCharacterAppearance* GetActiveAppearance() const { return ActiveAppearance; }

	USpringArmComponent* GetCameraBoom() const { return CameraBoom; }
	UCameraComponent* GetFollowCamera() const { return FollowCamera; }
	UGenesisInputSet* GetInputSet() const { return InputSet; }

	/** Naechste Figur vor dem Spieler ansprechen (Taste E / Controller X). */
	UFUNCTION(BlueprintCallable, Category = "Genesis|Character")
	bool TryInteract();

	void SetRunning(bool bInRunning);
	bool IsRunning() const { return bRunning; }

	/** Gehgeschwindigkeit eines Erwachsenen, ca. 5 km/h. */
	UPROPERTY(EditAnywhere, Category = "Genesis|Movement")
	float WalkSpeed = 150.f;

	/** Lockeres Joggen, ca. 13 km/h. */
	UPROPERTY(EditAnywhere, Category = "Genesis|Movement")
	float RunSpeed = 360.f;

protected:
	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;
	virtual void NotifyControllerChanged() override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	void HandleMove(const FInputActionValue& Value);
	void HandleLook(const FInputActionValue& Value);
	void HandleRunToggle(const FInputActionValue& Value);

private:
	void EnsureInputSet();
	void AddMappingContext();

	UPROPERTY(VisibleAnywhere, Category = "Genesis|Camera")
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere, Category = "Genesis|Camera")
	TObjectPtr<UCameraComponent> FollowCamera;

	UPROPERTY(Transient)
	TObjectPtr<UGenesisCharacterAppearance> ActiveAppearance;

	UPROPERTY(Transient)
	TObjectPtr<UGenesisInputSet> InputSet;

	bool bRunning = false;
};
