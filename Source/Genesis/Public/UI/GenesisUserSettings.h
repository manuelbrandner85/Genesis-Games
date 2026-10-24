#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameUserSettings.h"
#include "GenesisUserSettings.generated.h"

/**
 * Player options (ScriptLock III-D settings + accessibility), stored per Windows user in
 * Saved/Config/Windows/GameUserSettings.ini next to the engine's graphics settings.
 * Applied now: graphics profile, window mode, VSync, frame limit, master volume, camera
 * sensitivity/invert, motion blur, text size. Stored for the systems that follow (CM4+):
 * speech/music/effects volume, subtitles, speaker names, reading speed, flash and shake reduction.
 */
UCLASS(Config = GameUserSettings, ConfigDoNotCheckDefaults)
class GENESIS_API UGenesisUserSettings : public UGameUserSettings
{
    GENERATED_BODY()
public:
    static UGenesisUserSettings* Get();

    UPROPERTY(Config) float MasterVolume = 1.f;
    UPROPERTY(Config) float SpeechVolume = 1.f;
    UPROPERTY(Config) float MusicVolume = 0.8f;
    UPROPERTY(Config) float EffectsVolume = 1.f;
    UPROPERTY(Config) float CameraSensitivity = 1.f;
    UPROPERTY(Config) bool bInvertCameraY = false;
    UPROPERTY(Config) bool bMotionBlur = true;
    UPROPERTY(Config) bool bSubtitles = true;
    UPROPERTY(Config) bool bSubtitleSpeakerNames = true;
    UPROPERTY(Config) float TextScale = 1.f;            // 1.0 / 1.25 / 1.5
    UPROPERTY(Config) int32 ReadingSpeed = 1;           // 0 slow, 1 normal, 2 fast
    UPROPERTY(Config) bool bReduceFlashes = false;
    UPROPERTY(Config) bool bReduceCameraShake = false;

    /** Applies the Genesis options that have a runtime effect today (after ApplySettings). */
    void ApplyGenesisOptions(const UObject* WorldContext) const;

    virtual void SetToDefaults() override;
};
