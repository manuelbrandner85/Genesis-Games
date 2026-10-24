#include "GenesisGameMode.h"
#include "GenesisPrototypeCharacter.h"
#include "Player/GenesisPlayerController.h"
AGenesisGameMode::AGenesisGameMode()
{
    DefaultPawnClass = AGenesisPrototypeCharacter::StaticClass();
    PlayerControllerClass = AGenesisPlayerController::StaticClass();
}
