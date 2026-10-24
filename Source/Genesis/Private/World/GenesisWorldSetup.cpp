#include "World/GenesisWorldSetup.h"
#include "World/GenesisWorldStateSubsystem.h"
#include "Engine/World.h"

AGenesisWorldSetup::AGenesisWorldSetup()
{
    PrimaryActorTick.bCanEverTick = false;
    SetHidden(true);
}

void AGenesisWorldSetup::BeginPlay()
{
    Super::BeginPlay();
    UGenesisWorldStateSubsystem* WS = GetWorld()->GetSubsystem<UGenesisWorldStateSubsystem>();
    if (!WS || WS->GetState().Ledger.Num() > 0) {
        return;                                   // a running or loaded game keeps its state
    }
    FGenesisWorldState S;
    S.PlayerMoneyGE = StartMoneyGE;
    S.MarketStock = MarketStock;
    S.ObjectStates = ObjectStates;
    WS->ResetState(S);
    WS->EnsureIdentity();
    WS->SetClock(StartDay, StartHour, StartMinute);
}
