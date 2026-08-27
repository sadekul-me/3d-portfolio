import type { ExperienceMode, QualityPreset, ResolvedQualityTier } from '@/types/experience';

export type DeviceCapabilities = {
  webgl: boolean;
  webgl2: boolean;
  maxDpr: number;
  saveData: boolean;
  hardwareConcurrency: number;
  prefersReducedMotion: boolean;
};

export type ResolvedQuality = {
  tier: ResolvedQualityTier;
  dprCap: number;
  particles: 'full' | 'reduced' | 'off';
  postProcessing: 'full' | 'reduced' | 'off';
  shadows: boolean;
  textureQuality: 'HIGH' | 'BALANCED' | 'LOW';
};

/**
 * Deterministic quality resolution. Automatic tuning can later replace the AUTO branch
 * without changing consumers.
 */
export function resolveQuality(
  preset: QualityPreset,
  capabilities: DeviceCapabilities,
): ResolvedQuality {
  if (preset === 'HIGH') {
    return {
      tier: 'HIGH',
      dprCap: Math.min(capabilities.maxDpr, 2),
      particles: 'full',
      postProcessing: 'full',
      shadows: true,
      textureQuality: 'HIGH',
    };
  }
  if (preset === 'LOW') {
    return {
      tier: 'LOW',
      dprCap: 1,
      particles: 'off',
      postProcessing: 'off',
      shadows: false,
      textureQuality: 'LOW',
    };
  }
  if (preset === 'BALANCED') {
    return {
      tier: 'BALANCED',
      dprCap: Math.min(capabilities.maxDpr, 1.5),
      particles: 'reduced',
      postProcessing: 'reduced',
      shadows: true,
      textureQuality: 'BALANCED',
    };
  }

  if (!capabilities.webgl || capabilities.saveData || capabilities.hardwareConcurrency <= 4) {
    return resolveQuality('LOW', capabilities);
  }
  if (capabilities.webgl2 && capabilities.hardwareConcurrency >= 8 && capabilities.maxDpr >= 2) {
    return resolveQuality('HIGH', capabilities);
  }
  return resolveQuality('BALANCED', capabilities);
}

export function qualityToExperienceHint(tier: ResolvedQualityTier): ExperienceMode {
  if (tier === 'HIGH') {
    return 'PREMIUM_3D';
  }
  if (tier === 'BALANCED') {
    return 'REDUCED_3D';
  }
  return 'LIGHTWEIGHT';
}
