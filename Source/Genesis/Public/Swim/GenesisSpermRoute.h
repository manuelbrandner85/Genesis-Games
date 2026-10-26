#pragma once
#include "CoreMinimal.h"

/**
 * CR-002 (ScriptLock 1.3): the complete route of the sperm cell in five sections W1-W5, each an
 * analytic course (centre line, radius, flow) like FGenesisOviduct, at real micro scale (1 uu = 1 um)
 * across the lumen. The lengths are shortened ("Zeitmassstab: beschleunigt") so the route takes about
 * 8-12 min without input; the real distances are centimetres and the real times minutes to hours.
 */
enum class EGenesisRouteSection : uint8
{
    Vagina,         // W1: acidic milieu, the coagulum at the start
    Cervix,         // W2: mucus canal with crypts (dead ends)
    Uterus,         // W3: wide cavity, contraction waves, two tubal exits
    Isthmus,        // W4: narrow, winding; binding to the epithelium + capacitation (time jump), then hyperactivation
    Ampulla,        // W5: the existing swim to the oocyte (FGenesisOviduct)
    Count
};

/** A pocket off the main lumen (cervical crypt): the cell can swim in, and can get stuck there. */
struct GENESIS_API FGenesisCoursePocket
{
    FVector Center = FVector::ZeroVector;
    float Radius = 0.f;
    float S = 0.f;
};

/** One section of the route as an analytic tube; all functions take positions in the section's frame. */
struct GENESIS_API FGenesisCourse
{
    EGenesisRouteSection Section = EGenesisRouteSection::Ampulla;
    float Length = 4600.f;
    float StartS = 150.f;
    float EndS = 4300.f;                  // reaching this course position ends the section
    float RadiusStart = 420.f;
    float RadiusEnd = 650.f;
    float RadiusWobble = 40.f;
    float CurveY = 220.f, CurveYLen = 900.f;
    float CurveZ = 160.f, CurveZLen = 1300.f;
    float FlowMax = 12.f;                 // towards the start (against the swim), um/s at the centre
    float Drag = 1.f;                     // < 1: viscous medium (cervical mucus) slows the beat
    float FreeSeconds = 120.f;            // after this the course guides gently to the end
    TArray<FGenesisCoursePocket> Pockets;

    FVector Center(float S) const
    {
        return FVector(S, CurveY * FMath::Sin(S / CurveYLen), CurveZ * FMath::Sin(S / CurveZLen + 0.7f));
    }

    FVector Tangent(float S) const
    {
        return FVector(1.f, CurveY / CurveYLen * FMath::Cos(S / CurveYLen), CurveZ / CurveZLen * FMath::Cos(S / CurveZLen + 0.7f)).GetSafeNormal();
    }

    float Radius(float S) const
    {
        return FMath::Lerp(RadiusStart, RadiusEnd, FMath::Clamp(S / Length, 0.f, 1.f)) + RadiusWobble * FMath::Sin(S / 700.f);
    }

    FVector EndLocation() const { return Center(EndS); }

    float Project(const FVector& P, float Guess) const
    {
        float S = Guess;
        for (int32 I = 0; I < 4; ++I) {
            S += FVector::DotProduct(P - Center(S), Tangent(S));
        }
        return FMath::Clamp(S, 0.f, Length);
    }

    /** Parabolic flow over the cross-section, towards the start of the section. */
    FVector Flow(const FVector& P, float S) const
    {
        const FVector T = Tangent(S);
        const FVector Off = P - Center(S);
        const float R = (Off - T * FVector::DotProduct(Off, T)).Size() / Radius(S);
        return -T * FlowMax * FMath::Max(0.f, 1.f - R * R);
    }

    /** Index of the pocket that contains P (with margin), INDEX_NONE if none. */
    int32 PocketAt(const FVector& P, float Margin = 0.f) const
    {
        for (int32 I = 0; I < Pockets.Num(); ++I) {
            if (FVector::DistSquared(P, Pockets[I].Center) <= FMath::Square(Pockets[I].Radius - Margin)) {
                return I;
            }
        }
        return INDEX_NONE;
    }

    /** Keeps P inside the lumen or inside a pocket. Returns true if pushed back (OutNormal inward). */
    bool Constrain(FVector& P, float S, float Margin, FVector& OutNormal) const
    {
        for (const FGenesisCoursePocket& Pk : Pockets) {
            const FVector D = P - Pk.Center;
            if (D.SizeSquared() <= FMath::Square(Pk.Radius + Margin)) {
                // inside or at the rim of a pocket: free inside it, kept within its wall
                const FVector C = Center(S);
                const FVector T = Tangent(S);
                const FVector Off = P - C;
                const FVector Radial = Off - T * FVector::DotProduct(Off, T);
                if (Radial.SizeSquared() <= FMath::Square(Radius(S) - Margin)) {
                    return false;                              // still in the main lumen at the pocket mouth
                }
                if (D.SizeSquared() <= FMath::Square(Pk.Radius - Margin)) {
                    return false;
                }
                OutNormal = -D.GetSafeNormal();
                P = Pk.Center + D.GetSafeNormal() * (Pk.Radius - Margin);
                return true;
            }
        }
        const FVector C = Center(S);
        const FVector T = Tangent(S);
        const FVector Off = P - C;
        const FVector Radial = Off - T * FVector::DotProduct(Off, T);
        const float Max = Radius(S) - Margin;
        if (Radial.SizeSquared() <= Max * Max) {
            return false;
        }
        OutNormal = -Radial.GetSafeNormal();
        P = C + T * FVector::DotProduct(Off, T) + Radial.GetSafeNormal() * Max;
        return true;
    }
};

/** The five sections with their geometry, features and captions (ScriptLock 1.3, C02-B). */
struct GENESIS_API FGenesisSpermRoute
{
    static constexpr int32 NumSections = int32(EGenesisRouteSection::Count);

    // W1: the cell starts inside the coagulum and leaves it; acidic zones near the walls slow the beat.
    static constexpr float CoagulumRadius = 550.f;
    static constexpr float CoagulumDrag = 0.4f;
    static constexpr float AcidDrag = 0.6f;
    // W2: staying deep inside a crypt this long counts as stuck (F4: control passes to another cell).
    static constexpr float StuckSeconds = 6.f;
    // W3: contraction waves carry the cells towards the tubes.
    static constexpr float ContractionPeriod = 12.f;
    static constexpr float ContractionLength = 4.f;
    static constexpr float ContractionFlow = 35.f;
    // W4: binding to the epithelium, capacitation (a time jump), then hyperactivated motility.
    static constexpr float RestS = 2400.f;
    static constexpr float RestSeconds = 3.f;
    static constexpr float HyperactivatedSpeed = 1.3f;

    static FGenesisCourse Make(EGenesisRouteSection Section)
    {
        FGenesisCourse C;
        C.Section = Section;
        switch (Section) {
        case EGenesisRouteSection::Vagina:
            C.Length = 4800.f; C.StartS = 250.f; C.EndS = 4650.f;
            C.RadiusStart = 1400.f; C.RadiusEnd = 900.f; C.RadiusWobble = 120.f;     // posterior fornix towards the cervical os
            C.CurveY = 300.f; C.CurveYLen = 1600.f; C.CurveZ = 150.f; C.CurveZLen = 2000.f;
            C.FlowMax = 4.f; C.FreeSeconds = 80.f;
            break;
        case EGenesisRouteSection::Cervix:
            C.Length = 6600.f; C.StartS = 150.f; C.EndS = 6450.f;
            C.RadiusStart = 600.f; C.RadiusEnd = 340.f; C.RadiusWobble = 50.f;
            C.CurveY = 180.f; C.CurveYLen = 1100.f; C.CurveZ = 120.f; C.CurveZLen = 1500.f;
            C.FlowMax = 0.f; C.Drag = 0.85f; C.FreeSeconds = 140.f;
            for (int32 I = 0; I < 8; ++I) {                   // crypts alternating around the canal
                FGenesisCoursePocket P;
                P.S = 700.f + I * 700.f;
                const float Ang = I * 2.1f;
                const FVector T = C.Tangent(P.S);
                const FVector A = FVector::CrossProduct(T, FVector::UpVector).GetSafeNormal();
                const FVector B = FVector::CrossProduct(A, T).GetSafeNormal();
                const FVector Dir = A * FMath::Cos(Ang) + B * FMath::Sin(Ang);
                P.Radius = 230.f;
                P.Center = C.Center(P.S) + Dir * (C.Radius(P.S) + P.Radius * 0.55f);
                C.Pockets.Add(P);
            }
            break;
        case EGenesisRouteSection::Uterus:
            C.Length = 5200.f; C.StartS = 200.f; C.EndS = 5050.f;
            C.RadiusStart = 1200.f; C.RadiusEnd = 2500.f; C.RadiusWobble = 0.f;      // opens from the internal os into the cavity
            C.CurveY = 0.f; C.CurveYLen = 1000.f; C.CurveZ = 100.f; C.CurveZLen = 2500.f;
            C.FlowMax = 0.f; C.FreeSeconds = 80.f;
            break;
        case EGenesisRouteSection::Isthmus:
            C.Length = 6200.f; C.StartS = 120.f; C.EndS = 6050.f;
            C.RadiusStart = 160.f; C.RadiusEnd = 230.f; C.RadiusWobble = 15.f;
            C.CurveY = 260.f; C.CurveYLen = 500.f; C.CurveZ = 180.f; C.CurveZLen = 650.f;   // narrow and winding
            C.FlowMax = 12.f; C.FreeSeconds = 140.f;
            break;
        default:                                               // W5 = FGenesisOviduct (unchanged numbers)
            break;
        }
        return C;
    }

    /** Where in the uterus the two tubal exits are (W3): the correct one (with the oocyte) is +Y. */
    static FVector UterusExit(const FGenesisCourse& C, bool bCorrect)
    {
        return C.Center(C.EndS) + FVector(0.f, bCorrect ? 1.f : -1.f, 0.f) * C.RadiusEnd * 0.6f;
    }

    static float AcidZoneRadius() { return 320.f; }

    static const TCHAR* Caption(EGenesisRouteSection Section)
    {
        switch (Section) {
        case EGenesisRouteSection::Vagina:  return TEXT("Scheide – mikroskopische Darstellung | Zeitmaßstab: beschleunigt");
        case EGenesisRouteSection::Cervix:  return TEXT("Gebärmutterhals – mikroskopische Darstellung | Zeitmaßstab: beschleunigt");
        case EGenesisRouteSection::Uterus:  return TEXT("Gebärmutter – mikroskopische Darstellung | Zeitmaßstab: beschleunigt");
        case EGenesisRouteSection::Isthmus: return TEXT("Eileiter, Engstelle – mikroskopische Darstellung | Zeitmaßstab: beschleunigt");
        default:                            return TEXT("Eileiter – mikroskopische Darstellung | Zeitmaßstab: beschleunigt");
        }
    }
};
