import { STORAGE_KEYS, readStorage } from '@/lib/storage';
import { isLocale } from '@/types/locale';
import { isExperienceMode, isQualityPreset } from '@/types/experience';
import { useAppStore } from '@/store/appStore';
import { detectReducedMotion } from '@/app/bootstrap/detectCapabilities';

export function hydratePreferences(): void {
  const localeRaw = readStorage(STORAGE_KEYS.locale);
  const qualityRaw = readStorage(STORAGE_KEYS.qualityPreset);
  const soundRaw = readStorage(STORAGE_KEYS.soundEnabled);
  const modeRaw = readStorage(STORAGE_KEYS.experienceModeOverride);
  const reducedMotion = detectReducedMotion();

  const current = useAppStore.getState();
  current.replace({
    ...current,
    preferences: {
      ...current.preferences,
      locale: localeRaw && isLocale(localeRaw) ? localeRaw : current.preferences.locale,
      qualityPreset:
        qualityRaw && isQualityPreset(qualityRaw) ? qualityRaw : current.preferences.qualityPreset,
      soundEnabled: soundRaw === 'true',
      experienceModeOverride:
        modeRaw && isExperienceMode(modeRaw) ? modeRaw : current.preferences.experienceModeOverride,
      reducedMotion,
    },
    session: {
      ...current.session,
      language: localeRaw && isLocale(localeRaw) ? localeRaw : current.session.language,
      motionPreference: reducedMotion ? 'reduced' : 'standard',
    },
  });
}
