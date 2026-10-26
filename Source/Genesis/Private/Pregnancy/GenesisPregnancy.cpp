#include "Pregnancy/GenesisPregnancy.h"

const TArray<FGenesisPregStage>& FGenesisPregnancy::Stages()
{
    // Days since fertilisation (embryology); play seconds per stage after P1 (~2.5 h in all).
    static const TArray<FGenesisPregStage> S = {
        { TEXT("S1"),  TEXT("Erste Teilungen, Wanderung durch den Eileiter"),           0.f,   4.f,  600.f },
        { TEXT("S2"),  TEXT("Blastozyste schlüpft, Einnistung"),                         4.f,  10.f,  600.f },
        { TEXT("S3"),  TEXT("Keimscheibe, Neuralrohr, erster Herzschlag"),              10.f,  28.f,  900.f },
        { TEXT("S4"),  TEXT("Embryo: Organe, Gliedmaßenknospen, erste Zuckungen"),     28.f,  56.f,  900.f },
        { TEXT("S5"),  TEXT("Fötus: Reflexe, Schlucken, Greifen"),                     56.f,  84.f, 1080.f },
        { TEXT("S6"),  TEXT("Wachstum, kräftige Bewegungen"),                          84.f, 126.f, 1080.f },
        { TEXT("S7"),  TEXT("Das Hören beginnt"),                                     126.f, 175.f, 1200.f },
        { TEXT("S8"),  TEXT("Augen öffnen sich, hell und dunkel"),                     175.f, 224.f, 1200.f },
        { TEXT("S9"),  TEXT("Wenig Platz, Ruhe- und Wachphasen"),                      224.f, 266.f, 1080.f },
        { TEXT("S10"), TEXT("Geburt"),                                                266.f, 266.f,  180.f },
    };
    return S;
}

float FGenesisPregnancy::FirstDay(EGenesisPregAction A)
{
    switch (A) {
    case EGenesisPregAction::Twitch:       return 38.f;    // spontaneous movements ~7.5 weeks after the last period
    case EGenesisPregAction::Stretch:
    case EGenesisPregAction::Grasp:
    case EGenesisPregAction::Swallow:      return 56.f;
    case EGenesisPregAction::ThumbSuck:    return 70.f;
    case EGenesisPregAction::Kick:
    case EGenesisPregAction::Turn:         return 84.f;
    case EGenesisPregAction::ReactToVoice: return 154.f;   // hearing ~SSW 24
    case EGenesisPregAction::TurnToLight:  return 175.f;   // eyes open ~SSW 27
    case EGenesisPregAction::SleepWake:    return 224.f;
    default:                               return 0.f;     // observe, time lapse, lens
    }
}

float FGenesisPregnancy::LastDay(EGenesisPregAction A)
{
    if (A == EGenesisPregAction::Turn) {
        return 224.f;                                       // later there is no room to turn over
    }
    if (A == EGenesisPregAction::Twitch) {
        return 84.f;                                        // replaced by real kicks
    }
    return BirthDay;
}

const TCHAR* FGenesisPregnancy::ActionName(EGenesisPregAction A)
{
    switch (A) {
    case EGenesisPregAction::Observe:      return TEXT("Umsehen");
    case EGenesisPregAction::TimeLapse:    return TEXT("Zeitraffer");
    case EGenesisPregAction::Magnify:      return TEXT("Lupe");
    case EGenesisPregAction::Twitch:       return TEXT("Zucken");
    case EGenesisPregAction::Stretch:      return TEXT("Strecken");
    case EGenesisPregAction::Grasp:        return TEXT("Greifen");
    case EGenesisPregAction::Swallow:      return TEXT("Schlucken");
    case EGenesisPregAction::ThumbSuck:    return TEXT("Daumen");
    case EGenesisPregAction::Kick:         return TEXT("Treten");
    case EGenesisPregAction::Turn:         return TEXT("Drehen");
    case EGenesisPregAction::ReactToVoice: return TEXT("Auf Stimme reagieren");
    case EGenesisPregAction::TurnToLight:  return TEXT("Zum Licht wenden");
    case EGenesisPregAction::SleepWake:    return TEXT("Schlafen/Wachen");
    default:                               return TEXT("");
    }
}

bool FGenesisPregnancy::IsAllowed(EGenesisPregAction A) const
{
    return !bBorn && A < EGenesisPregAction::Count && Day >= FirstDay(A) && Day <= LastDay(A);
}

TArray<EGenesisPregAction> FGenesisPregnancy::AllowedActions() const
{
    TArray<EGenesisPregAction> Out;
    for (int32 I = 0; I < int32(EGenesisPregAction::Count); ++I) {
        if (IsAllowed(EGenesisPregAction(I))) {
            Out.Add(EGenesisPregAction(I));
        }
    }
    return Out;
}

bool FGenesisPregnancy::Perform(EGenesisPregAction A, FName& OutWorld) const
{
    OutWorld = NAME_None;
    if (!IsAllowed(A)) {
        return false;
    }
    switch (A) {
    case EGenesisPregAction::Kick:
    case EGenesisPregAction::Turn:
    case EGenesisPregAction::Stretch:
        // Only from ~SSW 20 the mother can feel it; earlier it shows only in an ultrasound.
        OutWorld = Day >= QuickeningDay ? FName(TEXT("Mother.FeltMovement")) : FName(TEXT("Movement.Unfelt"));
        break;
    case EGenesisPregAction::ReactToVoice:
        OutWorld = TEXT("Mother.NoticedReaction");
        break;
    default:
        break;
    }
    return true;
}

void FGenesisPregnancy::EnterStage(int32 NewStage)
{
    Stage = FMath::Clamp(NewStage, 0, Stages().Num() - 1);
    StageTime = 0.f;
    Day = Current().StartDay;
}

bool FGenesisPregnancy::Tick(float DeltaSeconds)
{
    if (bBorn) {
        return false;
    }
    StageTime += DeltaSeconds * TimeScale;
    const FGenesisPregStage& S = Current();
    Day = FMath::Lerp(S.StartDay, S.EndDay, FMath::Clamp(StageTime / S.PlaySeconds, 0.f, 1.f));
    if (!bC03Done && Day >= 196.f) {
        bC03Due = true;                                     // late pregnancy (SSW 30): C03
    }
    if (StageTime < S.PlaySeconds) {
        return false;
    }
    if (Stage == Stages().Num() - 1) {
        bBorn = true;
        Day = BirthDay;
        return false;
    }
    EnterStage(Stage + 1);
    return true;
}

bool FGenesisPregnancy::ShortenStage()
{
    if (bBorn) {
        return false;
    }
    ++Shortened;
    if (Stage == Stages().Num() - 1) {
        bBorn = true;
        Day = BirthDay;
        return true;
    }
    EnterStage(Stage + 1);
    if (!bC03Done && Day >= 196.f) {
        bC03Due = true;
    }
    return true;
}

void FGenesisPregnancy::Restore(FName StageId, float InDay, bool bInC03Done)
{
    bC03Done = bInC03Done;
    if (StageId == TEXT("Born")) {
        bBorn = true;
        Day = BirthDay;
        return;
    }
    for (int32 I = 0; I < Stages().Num(); ++I) {
        if (StageId == FName(Stages()[I].Id)) {
            Stage = I;
            const FGenesisPregStage& S = Stages()[I];
            Day = FMath::Clamp(InDay, S.StartDay, S.EndDay);
            StageTime = S.EndDay > S.StartDay ? (Day - S.StartDay) / (S.EndDay - S.StartDay) * S.PlaySeconds : 0.f;
            bC03Due = !bC03Done && Day >= 196.f;
            return;
        }
    }
    EnterStage(0);
}
