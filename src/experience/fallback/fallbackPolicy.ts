import { EXPERIENCE_MODE_RANK, type ExperienceMode } from '@/types/experience';

export type FallbackInput = {
  webgl: boolean;
  contextLost: boolean;
  reducedMotion: boolean;
  userOverride?: ExperienceMode;
  sceneFailed?: boolean;
  assetFailed?: boolean;
};

/**
 * Premium 3D → Reduced 3D → Lightweight → Quick Portfolio → Static Core
 * User overrides are respected unless they require an unavailable capability.
 */
export function decideExperienceMode(input: FallbackInput): ExperienceMode {
  if (input.userOverride === 'STATIC_CORE') {
    return 'STATIC_CORE';
  }
  if (input.userOverride === 'QUICK_PORTFOLIO') {
    return 'QUICK_PORTFOLIO';
  }

  if (!input.webgl) {
    return clampToAvailable(input.userOverride, 'QUICK_PORTFOLIO');
  }

  if (input.contextLost || input.sceneFailed) {
    return clampToAvailable(input.userOverride, 'QUICK_PORTFOLIO');
  }

  if (input.assetFailed) {
    return clampToAvailable(input.userOverride, 'LIGHTWEIGHT');
  }

  if (input.reducedMotion) {
    return clampToAvailable(input.userOverride, 'REDUCED_3D');
  }

  return input.userOverride ?? 'PREMIUM_3D';
}

function clampToAvailable(
  override: ExperienceMode | undefined,
  maximum: ExperienceMode,
): ExperienceMode {
  if (!override) {
    return maximum;
  }
  if (EXPERIENCE_MODE_RANK[override] > EXPERIENCE_MODE_RANK[maximum]) {
    return maximum;
  }
  return override;
}

export const FALLBACK_HIERARCHY: ExperienceMode[] = [
  'PREMIUM_3D',
  'REDUCED_3D',
  'LIGHTWEIGHT',
  'QUICK_PORTFOLIO',
  'STATIC_CORE',
];
