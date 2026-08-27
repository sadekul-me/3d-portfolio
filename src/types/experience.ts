export const QUALITY_PRESETS = ['AUTO', 'HIGH', 'BALANCED', 'LOW'] as const;
export type QualityPreset = (typeof QUALITY_PRESETS)[number];

export const RESOLVED_QUALITY_TIERS = ['HIGH', 'BALANCED', 'LOW'] as const;
export type ResolvedQualityTier = (typeof RESOLVED_QUALITY_TIERS)[number];

export const EXPERIENCE_MODES = [
  'PREMIUM_3D',
  'REDUCED_3D',
  'LIGHTWEIGHT',
  'QUICK_PORTFOLIO',
  'STATIC_CORE',
] as const;
export type ExperienceMode = (typeof EXPERIENCE_MODES)[number];

export const EXPERIENCE_MODE_RANK: Record<ExperienceMode, number> = {
  PREMIUM_3D: 4,
  REDUCED_3D: 3,
  LIGHTWEIGHT: 2,
  QUICK_PORTFOLIO: 1,
  STATIC_CORE: 0,
};

export function isExperienceMode(value: string): value is ExperienceMode {
  return (EXPERIENCE_MODES as readonly string[]).includes(value);
}

export function isQualityPreset(value: string): value is QualityPreset {
  return (QUALITY_PRESETS as readonly string[]).includes(value);
}
