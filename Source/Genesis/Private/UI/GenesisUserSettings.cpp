#include "UI/GenesisUserSettings.h"
#include "AudioDevice.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "HAL/IConsoleManager.h"

UGenesisUserSettings* UGenesisUserSettings::Get()
{
    return GEngine ? Cast<UGenesisUserSettings>(GEngine->GetGameUserSettings()) : nullptr;
}

void UGenesisUserSettings::SetToDefaults()
{
    Super::SetToDefaults();
    const UGenesisUserSettings* D = GetDefault<UGenesisUserSettings>();
    MasterVolume = D->MasterVolume;
    SpeechVolume = D->SpeechVolume;
    MusicVolume = D->MusicVolume;
    EffectsVolume = D->EffectsVolume;
    CameraSensitivity = D->CameraSensitivity;
    bInvertCameraY = D->bInvertCameraY;
    bMotionBlur = D->bMotionBlur;
    bSubtitles = D->bSubtitles;
    bSubtitleSpeakerNames = D->bSubtitleSpeakerNames;
    TextScale = D->TextScale;
    ReadingSpeed = D->ReadingSpeed;
    bReduceFlashes = DefaultReduceFlashes;          // not the CDO: that one carries the ini value
    bAutoSwim = D->bAutoSwim;
    GenesisOptionsVersion = CurrentOptionsVersion;
    bReduceCameraShake = D->bReduceCameraShake;
}

void UGenesisUserSettings::LoadSettings(bool bForceReload)
{
    Super::LoadSettings(bForceReload);
    UpgradeOptions();
}

void UGenesisUserSettings::UpgradeOptions()
{
    if (GenesisOptionsVersion < CurrentOptionsVersion) {
        bReduceFlashes = true;           // an old "off" cannot be told apart from the old default: safe side
        GenesisOptionsVersion = CurrentOptionsVersion;
    }
}

void UGenesisUserSettings::ApplyGenesisOptions(const UObject* WorldContext) const
{
    if (IConsoleVariable* Blur = IConsoleManager::Get().FindConsoleVariable(TEXT("r.MotionBlurQuality"))) {
        Blur->Set(bMotionBlur ? 4 : 0, ECVF_SetByGameSetting);
    }
    const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
    if (FAudioDevice* Audio = World ? World->GetAudioDeviceRaw() : nullptr) {
        Audio->SetTransientPrimaryVolume(FMath::Clamp(MasterVolume, 0.f, 1.f));
    }
}
