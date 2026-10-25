#pragma once
#include "CoreMinimal.h"

/**
 * CR-001 C01-A light strike (ScriptLock 1.2): point of light -> one bright strike -> white -> the
 * picture opens into the tissue of C02. Returns the white overlay level 0..1 over time.
 * Photosensitivity rules: at most one pulse, never red, and with "Lichtblitze verringern" (default
 * on) no strike at all, only a soft fade to white over 1.5 s.
 */
struct GENESIS_API FGenesisLightStrike
{
    static constexpr float PointSeconds = 0.8f;      // the light point grows, screen stays dark
    static constexpr float StrikeRise = 0.12f;       // normal: the one strike to full white
    static constexpr float SoftRise = 1.5f;          // reduced: soft fade to white
    static constexpr float HoldSeconds = 0.6f;
    static constexpr float FadeOutSeconds = 1.6f;      // smoothstep: < 0.02 change per frame at 60 fps

    static float Duration(bool bReduceFlashes)
    {
        return PointSeconds + (bReduceFlashes ? SoftRise : StrikeRise) + HoldSeconds + FadeOutSeconds;
    }

    /** Overlay opacity of the full-screen white at time T. */
    static float WhiteLevel(float T, bool bReduceFlashes)
    {
        const float Rise = bReduceFlashes ? SoftRise : StrikeRise;
        if (T <= PointSeconds) {
            return 0.f;
        }
        T -= PointSeconds;
        if (T < Rise) {
            const float A = T / Rise;
            return bReduceFlashes ? A * A * (3.f - 2.f * A) : A;     // smoothstep for the soft variant
        }
        T -= Rise;
        if (T < HoldSeconds) {
            return 1.f;
        }
        T -= HoldSeconds;
        const float A = FMath::Clamp(T / FadeOutSeconds, 0.f, 1.f);
        return 1.f - A * A * (3.f - 2.f * A);
    }

    /** Radius (share of the screen height) of the light point before the strike. */
    static float PointSize(float T)
    {
        return FMath::Clamp(T / PointSeconds, 0.f, 1.f) * 0.05f;
    }

    /** Warm white (no saturated red: ScriptLock 1.2 / photosensitivity). */
    static FLinearColor Color() { return FLinearColor(1.f, 0.97f, 0.92f, 1.f); }
};
