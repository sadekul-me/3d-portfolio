export const LOCALES = ['en', 'zh-CN'] as const;

export type Locale = (typeof LOCALES)[number];

export const FALLBACK_LOCALE: Locale = 'en';

export function isLocale(value: string): value is Locale {
  return (LOCALES as readonly string[]).includes(value);
}

/**
 * English is required. Other locales may fall back to English during development.
 * Production-required content is separately enforced by catalog validation.
 */
export type LocalizedText = {
  en: string;
  'zh-CN'?: string | undefined;
};

export type RequiredLocalizedText = {
  en: string;
  'zh-CN': string;
};

export function localizedValue(text: LocalizedText, locale: Locale): string {
  if (locale !== FALLBACK_LOCALE) {
    const translated = text[locale];
    if (translated && translated.trim().length > 0) {
      return translated;
    }
  }
  return text.en;
}
