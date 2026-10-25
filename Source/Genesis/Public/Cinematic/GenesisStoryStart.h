#pragma once
#include "CoreMinimal.h"
#include "Cinematic/GenesisSceneTypes.h"
#include "World/GenesisWorldTypes.h"

class UGenesisCinematicSubsystem;

/** Where the story start (CR-001, MENU_FLOW STORY_START) stands. */
enum class EGenesisStoryStep : uint8
{
    NotStarted,
    C00,            // prologue (old man); skippable after a second confirmation, seeds the soul
    C01,            // light strike (FGenesisLightStrike)
    C02Film,        // C02-A: arrival in the oviduct
    C02Swim,        // C02-B: mandatory swim, InGameplaySegment of the C02 contract
    C02End,         // C02-C..F: fusion, pronuclei, first division
    Title,          // title card after C02 (E1), then the main menu
    Done,
};

/**
 * Story start BOOT -> C00 -> C01 -> C02 (swim) -> title (ScriptLock 1.2, CR-001). Every part runs
 * through a SceneContract of UGenesisCinematicSubsystem, so skip rules and commits are the same as
 * for all cinematics. Builds the new life on the side: the soul at C00 (PreIncarnation_SoulSeed,
 * also when C00 is skipped), the world, and a new life strictly after the soul seed before C02.
 * While C00-C02 have no produced masters the contracts are technical tests (bTechnicalTest).
 * Lives in the game instance, because the swim phase is its own map.
 */
struct GENESIS_API FGenesisStoryStart
{
    EGenesisStoryStep Step = EGenesisStoryStep::NotStarted;
    FGenesisSceneContract Scene;          // contract of the part that runs now (C00, C01 or C02)
    FGenesisWorldState Life;              // identity and story-start progress of the coming life
    bool bTechnicalTest = true;           // C00-C02 masters not produced yet (CM5)
    FString LastError;

    static const FName SwimSegment;       // C02B_SWIM
    static const FName PreIncarnationLife;

    bool Start(UGenesisCinematicSubsystem& Cine);
    bool IsActive() const { return Step != EGenesisStoryStep::NotStarted && Step != EGenesisStoryStep::Done; }
    bool IsFilmPart() const { return Step == EGenesisStoryStep::C00 || Step == EGenesisStoryStep::C01 || Step == EGenesisStoryStep::C02Film || Step == EGenesisStoryStep::C02End; }
    /** The swim (C02-B) is the only part that can never be skipped. C00 asks twice (UI). */
    bool CanSkip() const { return IsFilmPart(); }
    bool NeedsSkipConfirmation() const { return Step == EGenesisStoryStep::C00; }

    /** The film part ran to its end (bSkipped false) or was skipped. Moves to the next part. */
    bool FinishFilm(UGenesisCinematicSubsystem& Cine, bool bSkipped);
    /** End of the swim. Result Own or Other - there is no game over (E2). */
    bool FinishSwim(UGenesisCinematicSubsystem& Cine, FName ConceptionMode);
    /** The title card after C02 (first start) or the chapter card (new life from the menu) was
     *  shown: the story start is complete and the life can be handed to the game. */
    void Complete();
    void Reset() { *this = FGenesisStoryStart(); }

private:
    bool BeginScene(UGenesisCinematicSubsystem& Cine, FName SceneID);
    bool CloseScene(UGenesisCinematicSubsystem& Cine);
    bool Fail(const FString& Why);
};
