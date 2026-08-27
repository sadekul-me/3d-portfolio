export const CONTROL_MODES = ['guided', 'limited-look', 'disabled'] as const;
export type ControlMode = (typeof CONTROL_MODES)[number];

/**
 * Default is guided cinematic travel, not mandatory WASD wandering.
 */
export const DEFAULT_CONTROL_MODE: ControlMode = 'guided';
