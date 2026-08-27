const STORAGE_PREFIX = 'digital-residence:';

export const STORAGE_KEYS = {
  locale: `${STORAGE_PREFIX}locale`,
  soundEnabled: `${STORAGE_PREFIX}sound-enabled`,
  qualityPreset: `${STORAGE_PREFIX}quality-preset`,
  experienceModeOverride: `${STORAGE_PREFIX}experience-mode-override`,
} as const;

export function readStorage(key: string): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

export function writeStorage(key: string, value: string): void {
  if (typeof window === 'undefined') {
    return;
  }
  try {
    window.localStorage.setItem(key, value);
  } catch {
    // Persistence is optional. Private mode or blocked storage must not break the app.
  }
}
