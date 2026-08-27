import { describe, expect, it } from 'vitest';

import { decideExperienceMode } from '@/experience/fallback/fallbackPolicy';

describe('fallback decisions', () => {
  it('uses Quick Portfolio when WebGL is unavailable', () => {
    expect(
      decideExperienceMode({
        webgl: false,
        contextLost: false,
        reducedMotion: false,
      }),
    ).toBe('QUICK_PORTFOLIO');
  });

  it('respects a Quick Portfolio user override on a capable device', () => {
    expect(
      decideExperienceMode({
        webgl: true,
        contextLost: false,
        reducedMotion: false,
        userOverride: 'QUICK_PORTFOLIO',
      }),
    ).toBe('QUICK_PORTFOLIO');
  });

  it('does not honor a premium override when WebGL is missing', () => {
    expect(
      decideExperienceMode({
        webgl: false,
        contextLost: false,
        reducedMotion: false,
        userOverride: 'PREMIUM_3D',
      }),
    ).toBe('QUICK_PORTFOLIO');
  });

  it('downgrades to lightweight after an asset failure', () => {
    expect(
      decideExperienceMode({
        webgl: true,
        contextLost: false,
        reducedMotion: false,
        assetFailed: true,
      }),
    ).toBe('LIGHTWEIGHT');
  });
});
