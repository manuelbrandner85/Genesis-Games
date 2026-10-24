#include "Mission/GenesisWorkshopContract.h"
#include "Npc/GenesisNpcSchedule.h"
#include "World/GenesisWorldStateSubsystem.h"

const FName FGenesisWorkshopContract::Contract = TEXT("CT_GENERATOR_N02");
const FName FGenesisWorkshopContract::Generator = TEXT("OBJ_GENERATOR_N02");
const FName FGenesisWorkshopContract::Tool = TEXT("TOOL_PLUG_WRENCH");
const FName FGenesisWorkshopContract::Part = TEXT("ITEM_SPARK_PLUG");
const FName FGenesisWorkshopContract::Reservation = TEXT("RES_ITEM_SPARK_PLUG");
const FName FGenesisWorkshopContract::FactPlugWorn = TEXT("FACT_PLUG_WORN");
const FName FGenesisWorkshopContract::FactFilterOk = TEXT("FACT_FILTER_OK");

namespace
{
    using C = FGenesisWorkshopContract;
    // Contract states
    const TCHAR* Offered = TEXT("Offered");
    const TCHAR* PriceRejected = TEXT("PriceRejected");
    const TCHAR* Accepted = TEXT("Accepted");
    const TCHAR* AwaitingInspection = TEXT("AwaitingInspection");
    const TCHAR* ReferredToN01 = TEXT("ReferredToN01");
    const TCHAR* WithN01 = TEXT("WithN01");
    const TCHAR* Completed = TEXT("Completed");
    const TCHAR* CompletedByN01 = TEXT("CompletedByN01");
    const TCHAR* Declined = TEXT("Declined");
    const TCHAR* Withdrawn = TEXT("Withdrawn");

    const FVector WorkshopLocation(5100.f, -120.f, 100.f);   // generator in R03 (for perception)
    const FVector MarketLocation(2950.f, -150.f, 100.f);

    FText T(const TCHAR* S) { return FText::FromString(S); }
    FName At(const FGenesisPresence& P, FName Npc) { const FName* R = P.Find(Npc); return R ? *R : NAME_None; }
    bool Is(const FString& S, const TCHAR* V) { return S == V; }

    FGenesisChoice Choice(const TCHAR* Action, const TCHAR* Text, bool bEnabled = true, const TCHAR* Reason = TEXT(""))
    {
        FGenesisChoice Ch;
        Ch.Action = Action;
        Ch.Text = T(Text);
        Ch.bEnabled = bEnabled;
        Ch.Reason = T(Reason);
        return Ch;
    }

    FGenesisReply Say(FName Who, const TCHAR* Line) { return FGenesisReply{ Who, T(Line) }; }

    void SetState(UGenesisWorldStateSubsystem& WS, const TCHAR* Action, FName Actor, const TCHAR* NewState, const FVector& Where)
    {
        // Idempotency per transition: confirming the same step twice records it once.
        const FName Key(*FString::Printf(TEXT("ct_generator:%s->%s"), *C::State(WS), NewState));
        WS.ApplyEvent(Action, Actor, C::Contract, NewState, Key, {}, &Where);
    }

    void ReleaseReservation(UGenesisWorldStateSubsystem& WS)
    {
        if (WS.GetObjectState(C::Reservation) == TEXT("Player")) {
            WS.ApplyEvent(TEXT("Market.ReservationReleased"), TEXT("N03"), C::Reservation, TEXT("None"));
        }
    }

    bool PlayerHasTool(const UGenesisWorldStateSubsystem& WS) { return WS.GetObjectState(C::Tool) == TEXT("Player"); }
    int32 Stock(const UGenesisWorldStateSubsystem& WS) { return WS.GetState().MarketStock.FindRef(C::Part); }
}

FString FGenesisWorkshopContract::State(const UGenesisWorldStateSubsystem& WS)
{
    const FString S = WS.GetObjectState(Contract);
    return S.IsEmpty() ? FString(TEXT("None")) : S;
}

bool FGenesisWorkshopContract::IsTerminal(const FString& S)
{
    return S == Completed || S == CompletedByN01 || S == Declined || S == Withdrawn;
}

TArray<FGenesisChoice> FGenesisWorkshopContract::Choices(const UGenesisWorldStateSubsystem& WS, FName Target, const FGenesisPresence& P)
{
    TArray<FGenesisChoice> Out;
    const FString S = State(WS);
    const bool bRepaired = WS.GetObjectState(Generator) == TEXT("Repaired");

    if (Target == TEXT("N02")) {
        if (At(P, TEXT("N02")).IsNone()) {
            return Out;                                            // not reachable (at home / walking)
        }
        if (Is(S, TEXT("None")) && !bRepaired) {
            Out.Add(Choice(TEXT("N02.Ask"), TEXT("Sie wirken besorgt – kann ich helfen?")));
        }
        if (Is(S, Offered) || Is(S, PriceRejected)) {
            Out.Add(Choice(TEXT("N02.Accept60"), TEXT("Ich repariere den Generator für 60 GE.")));
            if (Is(S, Offered)) {
                Out.Add(Choice(TEXT("N02.Quote90"), TEXT("Das kostet 90 GE.")));
            }
            Out.Add(Choice(TEXT("N02.Refer"), TEXT("Fragen Sie in der Werkstatt nach – dort macht das jemand vom Fach.")));
            Out.Add(Choice(TEXT("N02.Decline"), TEXT("Das kann ich leider nicht übernehmen.")));
        }
        if (Is(S, Accepted)) {
            Out.Add(Choice(TEXT("N02.ReportDone"), TEXT("Der Generator läuft wieder."), bRepaired, TEXT("Er ist noch nicht repariert.")));
            Out.Add(Choice(TEXT("N02.GiveBack"), TEXT("Ich schaffe es doch nicht – bitte suchen Sie sich jemand anderen.")));
        }
        return Out;
    }
    if (Target == TEXT("N03")) {
        if (At(P, TEXT("N03")) != TEXT("R02")) {
            return Out;                                            // shop closed / not at the counter
        }
        const FString Res = WS.GetObjectState(Reservation);
        const bool bForOther = !Res.IsEmpty() && Res != TEXT("None") && Res != TEXT("Player");
        const bool bAfford = WS.GetState().PlayerMoneyGE >= PartPriceGE;
        const TCHAR* Why = Stock(WS) <= 0 ? TEXT("Nicht vorrätig.") : bForOther ? TEXT("Für jemand anderen reserviert.")
                         : !bAfford ? TEXT("Zu wenig Geld (18 GE).") : TEXT("");
        Out.Add(Choice(TEXT("N03.BuyPlug"), TEXT("Eine Zündkerze für einen Generator, bitte (18 GE)."),
                       Stock(WS) > 0 && !bForOther && bAfford, Why));
        Out.Add(Choice(TEXT("N03.AskStock"), TEXT("Haben Sie Ersatzteile für Generatoren?")));
        return Out;
    }
    if (Target == TEXT("N01")) {
        if (At(P, TEXT("N01")) != TEXT("R03")) {
            return Out;                                            // not at work
        }
        const bool bNeed = Is(S, Accepted);
        if (!PlayerHasTool(WS)) {
            Out.Add(Choice(TEXT("N01.BorrowTool"), TEXT("Kann ich mir einen Zündkerzenschlüssel leihen?"), bNeed,
                           TEXT("Du hast keinen Auftrag, für den du ihn brauchst.")));
        } else {
            Out.Add(Choice(TEXT("N01.ReturnTool"), TEXT("Hier ist der Zündkerzenschlüssel zurück, danke.")));
        }
        Out.Add(Choice(TEXT("N01.Advice"), TEXT("Woran kann es liegen, wenn ein Generator nicht anspringt?")));
        return Out;
    }
    if (Target == Generator) {
        if (bRepaired) {
            Out.Add(Choice(TEXT("Gen.Look"), TEXT("Generator ansehen")));
            return Out;
        }
        Out.Add(Choice(TEXT("Gen.TryStart"), TEXT("Startversuch")));
        Out.Add(Choice(TEXT("Gen.InspectFilter"), TEXT("Kraftstofffilter prüfen")));
        Out.Add(Choice(TEXT("Gen.InspectPlug"), TEXT("Zündkerze ausbauen und prüfen"), PlayerHasTool(WS),
                       TEXT("Dafür brauchst du einen Zündkerzenschlüssel.")));
        const bool bDiag = WS.WasApplied(TEXT("fact:plug_worn"));
        const TCHAR* Why = !Is(S, Accepted) ? TEXT("Ohne Auftrag reparierst du kein fremdes Gerät.")
                         : !bDiag ? TEXT("Die Ursache ist noch nicht festgestellt.")
                         : WS.GetItemCount(Part) < 1 ? TEXT("Du hast keine Ersatz-Zündkerze.")
                         : !PlayerHasTool(WS) ? TEXT("Dafür brauchst du einen Zündkerzenschlüssel.") : TEXT("");
        Out.Add(Choice(TEXT("Gen.Repair"), TEXT("Neue Zündkerze einsetzen"), FCString::Strlen(Why) == 0, Why));
        return Out;
    }
    return Out;
}

FGenesisReply FGenesisWorkshopContract::Execute(UGenesisWorldStateSubsystem& WS, FName Target, FName Action, const FGenesisPresence& P)
{
    // Only choices offered right now (and enabled) can happen - also protects against stale UI.
    const TArray<FGenesisChoice> Now = Choices(WS, Target, P);
    const FGenesisChoice* Ch = Now.FindByPredicate([&](const FGenesisChoice& X) { return X.Action == Action; });
    if (!Ch || !Ch->bEnabled) {
        return Say(NAME_None, Ch ? *Ch->Reason.ToString() : TEXT("Das geht gerade nicht."));
    }
    const FName N01 = TEXT("N01"), N02 = TEXT("N02"), N03 = TEXT("N03");

    if (Action == TEXT("N02.Ask")) {
        SetState(WS, TEXT("Contract.Offered"), N02, Offered, MarketLocation);
        return Say(N02, TEXT("Mein Generator springt nicht mehr an. Er steht schon in der Werkstatt. Würden Sie ihn reparieren? Mehr als 70 GE kann ich nicht ausgeben."));
    }
    if (Action == TEXT("N02.Accept60")) {
        SetState(WS, TEXT("Contract.Accepted"), TEXT("Player"), Accepted, MarketLocation);
        if (Stock(WS) > 0 && WS.GetObjectState(Reservation).IsEmpty()) {
            WS.ApplyEvent(TEXT("Market.Reserved"), N03, Reservation, TEXT("Player"), TEXT("reserve_plug_for_contract"));
        }
        return Say(N02, TEXT("Einverstanden, 60 GE. Sagen Sie mir Bescheid, wenn er läuft – ich sehe ihn mir dann selbst an."));
    }
    if (Action == TEXT("N02.Quote90")) {
        SetState(WS, TEXT("Contract.PriceRejected"), N02, PriceRejected, MarketLocation);
        return Say(N02, TEXT("90 GE? Das ist mir zu teuer, so viel habe ich nicht."));
    }
    if (Action == TEXT("N02.Refer")) {
        SetState(WS, TEXT("Contract.Referred"), N02, ReferredToN01, MarketLocation);
        return Say(N02, TEXT("Gut, dann frage ich in der Werkstatt nach, sobald dort geöffnet ist."));
    }
    if (Action == TEXT("N02.Decline")) {
        SetState(WS, TEXT("Contract.Declined"), N02, Declined, MarketLocation);
        return Say(N02, TEXT("Schade. Dann muss ich mir selbst etwas überlegen."));
    }
    if (Action == TEXT("N02.ReportDone")) {
        SetState(WS, TEXT("Contract.ReportedDone"), TEXT("Player"), AwaitingInspection, MarketLocation);
        return Say(N02, TEXT("Wirklich? Ich gehe gleich in die Werkstatt und sehe ihn mir an."));
    }
    if (Action == TEXT("N02.GiveBack")) {
        ReleaseReservation(WS);
        SetState(WS, TEXT("Contract.ReturnedByPlayer"), TEXT("Player"), Declined, MarketLocation);
        return Say(N02, TEXT("Schade, dass Sie das nicht früher gesagt haben. Ich kümmere mich selbst darum."));
    }
    if (Action == TEXT("N03.BuyPlug")) {
        if (!WS.TryPay(PartPriceGE, TEXT("Market.Buy"), Part, FName(*FString::Printf(TEXT("buy_plug_%d"), WS.GetState().NextEventNumber)))) {
            return Say(N03, TEXT("Das reicht leider nicht."));
        }
        WS.GetMutableState().MarketStock.Add(Part, Stock(WS) - 1);
        WS.GetMutableState().PlayerItems.Add(Part, WS.GetItemCount(Part) + 1);
        if (WS.GetObjectState(Reservation) == TEXT("Player")) {
            WS.ApplyEvent(TEXT("Market.ReservationCollected"), N03, Reservation, TEXT("None"));
        }
        return Say(N03, TEXT("Bitte schön, eine Zündkerze. 18 GE."));
    }
    if (Action == TEXT("N03.AskStock")) {
        return Say(N03, Stock(WS) > 0 ? TEXT("Zündkerzen habe ich, eine einzige noch.") : TEXT("Zündkerzen sind gerade aus. Die nächste Lieferung kommt erst noch."));
    }
    if (Action == TEXT("N01.BorrowTool")) {
        WS.ApplyEvent(TEXT("Workshop.ToolLent"), N01, Tool, TEXT("Player"), FName(*FString::Printf(TEXT("lend_tool_%d"), WS.GetState().NextEventNumber)), {}, &WorkshopLocation);
        return Say(N01, TEXT("Hier, der Zündkerzenschlüssel. Bring ihn bitte zurück, wenn du fertig bist."));
    }
    if (Action == TEXT("N01.ReturnTool")) {
        WS.ApplyEvent(TEXT("Workshop.ToolReturned"), TEXT("Player"), Tool, TEXT("N01"), FName(*FString::Printf(TEXT("return_tool_%d"), WS.GetState().NextEventNumber)), {}, &WorkshopLocation);
        return Say(N01, TEXT("Danke, zurück an seinen Platz."));
    }
    if (Action == TEXT("N01.Advice")) {
        return Say(N01, TEXT("Erst schauen, ob Kraftstoff ankommt – Filter ansehen. Dann die Zündkerze. Meistens ist es eins von beiden."));
    }
    if (Action == TEXT("Gen.TryStart")) {
        return Say(NAME_None, TEXT("Der Motor dreht, springt aber nicht an."));
    }
    if (Action == TEXT("Gen.InspectFilter")) {
        WS.ApplyEvent(TEXT("Diagnosis.FilterChecked"), TEXT("Player"), FactFilterOk, TEXT("Ok"), TEXT("fact:filter_ok"), {}, &WorkshopLocation);
        return Say(NAME_None, TEXT("Der Kraftstofffilter ist klar, Kraftstoff läuft durch. Daran liegt es nicht."));
    }
    if (Action == TEXT("Gen.InspectPlug")) {
        WS.ApplyEvent(TEXT("Diagnosis.PlugChecked"), TEXT("Player"), FactPlugWorn, TEXT("Worn"), TEXT("fact:plug_worn"), {}, &WorkshopLocation);
        return Say(NAME_None, TEXT("Die Zündkerze ist verrußt, die Elektrode abgebrannt. Sie zündet nicht mehr zuverlässig."));
    }
    if (Action == TEXT("Gen.Repair")) {
        WS.GetMutableState().PlayerItems.Add(Part, WS.GetItemCount(Part) - 1);
        WS.ApplyEvent(TEXT("Repair.Done"), TEXT("Player"), Generator, TEXT("Repaired"), TEXT("repair_generator_n02"), {}, &WorkshopLocation);
        return Say(NAME_None, TEXT("Neue Zündkerze eingesetzt. Der Generator springt an und läuft gleichmäßig."));
    }
    if (Action == TEXT("Gen.Look")) {
        return Say(NAME_None, TEXT("Der Generator läuft gleichmäßig."));
    }
    return Say(NAME_None, TEXT("Das geht gerade nicht."));
}

void FGenesisWorkshopContract::Update(UGenesisWorldStateSubsystem& WS, const FGenesisPresence& P)
{
    const FString S = State(WS);
    const FName N01 = TEXT("N01"), N02 = TEXT("N02");
    if (Is(S, AwaitingInspection) && At(P, N02) == TEXT("R03")) {
        // The customer checks it herself (acceptance) and pays exactly once.
        WS.NpcObserve(N02, WS.FindLastEvent(TEXT("Repair.Done")) ? WS.FindLastEvent(TEXT("Repair.Done"))->EventID : NAME_None);
        WS.Earn(RewardGE, TEXT("Contract.Paid"), N02, Contract, TEXT("pay_ct_generator_n02"));
        SetState(WS, TEXT("Contract.Completed"), N02, Completed, WorkshopLocation);
        return;
    }
    if (Is(S, ReferredToN01) && At(P, N01) == TEXT("R03") && At(P, N02) == TEXT("R03")) {
        SetState(WS, TEXT("Contract.TakenByN01"), N01, WithN01, WorkshopLocation);
        if (Stock(WS) > 0 && WS.GetObjectState(Reservation) != TEXT("Player")) {
            WS.GetMutableState().MarketStock.Add(Part, Stock(WS) - 1);       // N01 gets the part from the market
            WS.ApplyEvent(TEXT("Workshop.PartBought"), N01, TEXT("N01_PART"), TEXT("Have"), TEXT("n01_buy_plug"));
        } else {
            WS.ApplyEvent(TEXT("Workshop.WaitingForParts"), N01, TEXT("N01_PART"), TEXT("Waiting"), TEXT("n01_wait_plug"));
        }
        return;
    }
    if (Is(S, WithN01) && WS.GetObjectState(TEXT("N01_PART")) == TEXT("Have") && At(P, N01) == TEXT("R03")) {
        const FGenesisWorldEvent* Taken = WS.FindLastEvent(TEXT("Contract.TakenByN01"));
        if (Taken && WS.GetWorldMinute() - Taken->WorldMinute >= N01RepairMinutes) {
            WS.ApplyEvent(TEXT("Repair.DoneByN01"), N01, Generator, TEXT("Repaired"), TEXT("n01_repair_generator"), {}, &WorkshopLocation);
            SetState(WS, TEXT("Contract.CompletedByN01"), N01, CompletedByN01, WorkshopLocation);
        }
        return;
    }
    // The customer needs the generator: an open order that is not done by the end of day 2 is
    // withdrawn (source: "Kundin geht" as a failure case). A finished repair is always accepted.
    const bool bOpen = Is(S, Offered) || Is(S, PriceRejected) || Is(S, Accepted) || Is(S, ReferredToN01) || Is(S, WithN01);
    if (bOpen && WS.GetDay() > WithdrawAfterDay) {
        ReleaseReservation(WS);
        SetState(WS, TEXT("Contract.Withdrawn"), N02, Withdrawn, MarketLocation);
    }
}

FName FGenesisWorkshopContract::NpcOverrideAnchor(const UGenesisWorldStateSubsystem& WS, FName NpcID)
{
    if (NpcID != TEXT("N02")) {
        return NAME_None;
    }
    const FString S = State(WS);
    if (Is(S, AwaitingInspection)) {
        return TEXT("N02_Workshop");                                // appointment: comes to inspect
    }
    if (Is(S, ReferredToN01)) {
        const FGenesisScheduleEntry* E = FGenesisNpcSchedules::Find(TEXT("N01"), WS.GetMinuteOfDay());
        if (E && E->Region == TEXT("R03")) {
            return TEXT("N02_Workshop");                            // asks in the workshop while it is open
        }
    }
    return NAME_None;
}

FText FGenesisWorkshopContract::TaskText(const UGenesisWorldStateSubsystem& WS)
{
    const FString S = State(WS);
    if (Is(S, TEXT("None"))) return T(TEXT(""));
    if (Is(S, Offered) || Is(S, PriceRejected)) return T(TEXT("Auftrag angeboten: Generator der Kundin (60 GE möglich)"));
    if (Is(S, Accepted)) {
        if (WS.GetObjectState(Generator) == TEXT("Repaired")) return T(TEXT("Generator läuft – der Kundin Bescheid geben"));
        if (!WS.WasApplied(TEXT("fact:plug_worn"))) return T(TEXT("Auftrag: Generator in der Werkstatt – Ursache finden"));
        if (WS.GetItemCount(Part) < 1) return T(TEXT("Ursache: Zündkerze – Ersatz am Markt besorgen"));
        return T(TEXT("Neue Zündkerze einsetzen"));
    }
    if (Is(S, AwaitingInspection)) return T(TEXT("Die Kundin sieht sich den Generator in der Werkstatt an"));
    if (Is(S, ReferredToN01) || Is(S, WithN01)) return T(TEXT("Die Kundin hat sich an die Werkstatt gewandt"));
    if (Is(S, Completed)) return T(TEXT("Auftrag erledigt – 60 GE erhalten"));
    if (Is(S, CompletedByN01)) return T(TEXT("Die Werkstatt hat den Generator repariert"));
    if (Is(S, Declined)) return T(TEXT("Auftrag nicht übernommen"));
    if (Is(S, Withdrawn)) return T(TEXT("Die Kundin hat den Auftrag zurückgezogen"));
    return T(TEXT(""));
}
