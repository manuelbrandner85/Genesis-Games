#include "GenesisGameMode.h"
#include "GenesisPrototypeCharacter.h"
AGenesisGameMode::AGenesisGameMode()
{
    DefaultPawnClass = AGenesisPrototypeCharacter::StaticClass();
}
