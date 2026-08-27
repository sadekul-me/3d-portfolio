import { describe, expect, it } from 'vitest';

import { translate } from '@/i18n/translate';
import { localizedValue } from '@/types/locale';

describe('i18n fallback', () => {
  it('returns Simplified Chinese UI copy when requested', () => {
    expect(translate('zh-CN', 'landing.enterExperience')).toBe('进入体验');
  });

  it('falls back to English for a localized content field', () => {
    expect(localizedValue({ en: 'Engineer' }, 'zh-CN')).toBe('Engineer');
  });
});
