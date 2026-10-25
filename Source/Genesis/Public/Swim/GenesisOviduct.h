#pragma once
#include "CoreMinimal.h"

/**
 * C02-B graybox (CR-001 phase 2): the swim course through the oviduct towards the oocyte.
 * Scale: 1 Unreal unit = 1 micrometre (not 1 cm), so sizes and speeds are the real ones:
 * sperm head ~5 um, cell ~55 um long, progressive swimming 25-60 um/s (hyperactivated faster),
 * oocyte 120 um across with a ~15 um zona pellucida, ampulla lumen roughly 0.8-1.4 mm wide.
 * The course is shortened to ~4 mm so the swim lasts 60-120 s (E4).
 * The tube is analytic (centre line + radius), so movement, walls and flow need no collision mesh.
 */
struct GENESIS_API FGenesisOviduct
{
    static constexpr float Length = 4600.f;          // course length along the centre line (um)
    static constexpr float StartS = 150.f;
    static constexpr float EggS = 4300.f;
    static constexpr float OocyteRadius = 60.f;
    static constexpr float ZonaRadius = 75.f;        // the sperm arrives at the zona pellucida
    static constexpr float FlowMax = 12.f;           // ciliary/fluid flow towards the uterus (um/s, centre)

    /** Centre line, gently curving (s = distance along the course, ~x). */
    static FVector Center(float S)
    {
        return FVector(S, 220.f * FMath::Sin(S / 900.f), 160.f * FMath::Sin(S / 1300.f + 0.7f));
    }

    static FVector Tangent(float S)
    {
        return FVector(1.f, 220.f / 900.f * FMath::Cos(S / 900.f), 160.f / 1300.f * FMath::Cos(S / 1300.f + 0.7f)).GetSafeNormal();
    }

    /** Lumen radius: isthmus narrower, ampulla wider towards the oocyte. */
    static float Radius(float S)
    {
        return 420.f + 230.f * FMath::Clamp(S / Length, 0.f, 1.f) + 40.f * FMath::Sin(S / 700.f);
    }

    static FVector EggLocation() { return Center(EggS); }

    /** Course position of a point, refined from a guess (the curve is gentle: a few steps suffice). */
    static float Project(const FVector& P, float Guess)
    {
        float S = Guess;
        for (int32 I = 0; I < 4; ++I) {
            S += FVector::DotProduct(P - Center(S), Tangent(S));
        }
        return FMath::Clamp(S, 0.f, Length);
    }

    /** Flow towards the uterus (-tangent), parabolic over the cross-section: strongest in the centre. */
    static FVector Flow(const FVector& P, float S)
    {
        const FVector T = Tangent(S);
        const FVector Off = P - Center(S);
        const float R = (Off - T * FVector::DotProduct(Off, T)).Size() / Radius(S);
        return -T * FlowMax * FMath::Max(0.f, 1.f - R * R);
    }

    /** Keeps a point inside the lumen (Margin from the wall). Returns true if it was pushed back;
     *  OutNormal is the inward wall normal then. */
    static bool Constrain(FVector& P, float S, float Margin, FVector& OutNormal)
    {
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
