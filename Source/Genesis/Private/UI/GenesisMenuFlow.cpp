#include "UI/GenesisMenuFlow.h"
#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
    const FName ExitNode(TEXT("EXIT"));

    TSet<FName> Reach(const TMap<FName, FGenesisMenuFlow::FNode>& Nodes, FName Start, bool bReverse)
    {
        TSet<FName> Seen;
        TArray<FName> Open = { Start };
        while (Open.Num() > 0) {
            const FName N = Open.Pop();
            if (Seen.Contains(N)) {
                continue;
            }
            Seen.Add(N);
            for (const TPair<FName, FGenesisMenuFlow::FNode>& P : Nodes) {
                if (!bReverse && P.Key == N) {
                    Open.Append(P.Value.Edges);
                }
                else if (bReverse && P.Value.Edges.Contains(N)) {
                    Open.Add(P.Key);
                }
            }
        }
        return Seen;
    }
}

FString FGenesisMenuFlow::DefaultPath()
{
    return FPaths::ProjectContentDir() / TEXT("Genesis/Data/menu_flow.json");
}

bool FGenesisMenuFlow::LoadFromFile(const FString& Path, FString& OutError)
{
    Nodes.Reset();
    FString Text;
    TSharedPtr<FJsonObject> Root;
    if (!FFileHelper::LoadFileToString(Text, *Path)) {
        OutError = TEXT("missing ") + Path;
        return false;
    }
    if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text), Root) || !Root.IsValid()) {
        OutError = TEXT("not json");
        return false;
    }
    Initial = FName(Root->GetStringField(TEXT("initial")));
    for (const TSharedPtr<FJsonValue>& V : Root->GetArrayField(TEXT("nodes"))) {
        const TSharedPtr<FJsonObject> O = V->AsObject();
        FNode N;
        N.Mode = O->GetStringField(TEXT("mode"));
        for (const TSharedPtr<FJsonValue>& E : O->GetArrayField(TEXT("edges"))) {
            N.Edges.Add(FName(E->AsString()));
        }
        for (const TSharedPtr<FJsonValue>& A : O->GetArrayField(TEXT("actions"))) {
            N.Actions.Add(A->AsString());
        }
        Nodes.Add(FName(O->GetStringField(TEXT("id"))), MoveTemp(N));
    }
    Current = Initial;
    return Nodes.Contains(Initial);
}

TArray<FString> FGenesisMenuFlow::Validate() const
{
    TArray<FString> Errors;
    if (!Nodes.Contains(Initial)) {
        Errors.Add(TEXT("initial node missing"));
        return Errors;
    }
    for (const TPair<FName, FNode>& P : Nodes) {
        for (const FName& E : P.Value.Edges) {
            if (!Nodes.Contains(E)) {
                Errors.Add(FString::Printf(TEXT("%s -> unknown %s"), *P.Key.ToString(), *E.ToString()));
            }
        }
        if (P.Value.Edges.Num() == 0 && P.Key != ExitNode) {
            Errors.Add(FString::Printf(TEXT("%s has no way out"), *P.Key.ToString()));
        }
    }
    const TSet<FName> FromStart = Reach(Nodes, Initial, false);
    const TSet<FName> ToExit = Reach(Nodes, ExitNode, true);
    for (const TPair<FName, FNode>& P : Nodes) {
        if (!FromStart.Contains(P.Key)) {
            Errors.Add(FString::Printf(TEXT("%s is not reachable"), *P.Key.ToString()));
        }
        if (!ToExit.Contains(P.Key)) {
            Errors.Add(FString::Printf(TEXT("%s cannot reach EXIT (dead end)"), *P.Key.ToString()));
        }
    }
    return Errors;
}

bool FGenesisMenuFlow::CanGo(FName To) const
{
    const FNode* N = Nodes.Find(Current);
    return N && N->Edges.Contains(To);
}

bool FGenesisMenuFlow::Go(FName To)
{
    if (!CanGo(To)) {
        return false;
    }
    Current = To;
    return true;
}
