export const SAFE_RECOVERY_ACTIONS = [
  'retry_asset',
  'switch_asset_variant',
  'set_quality_mode',
  'restore_safe_scene',
  'switch_ai_provider',
  'disable_optional_effect',
] as const;

export type SafeRecoveryAction = (typeof SAFE_RECOVERY_ACTIONS)[number];

export const MAINTENANCE_TIERS = ['diagnose', 'safe-patch', 'human-approved'] as const;
export type MaintenanceTier = (typeof MAINTENANCE_TIERS)[number];
