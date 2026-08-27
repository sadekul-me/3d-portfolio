export const AI_MAINTENANCE_DOCTRINE = {
  preserveBeforeImprove: true,
  patchBeforeRewrite: true,
  validateBeforeApply: true,
  rollBackBeforeRiskingStability: true,
} as const;

export const AI_MAINTENANCE_TIERS = {
  1: 'Diagnose only. Read allowed context, classify, propose a patch. No writes.',
  2: 'Safe minimal patch. Bounded files, targeted tests, deterministic validation, revert own patch.',
  3: 'Human-approved repair or refactor. Never fully autonomous in production.',
} as const;
