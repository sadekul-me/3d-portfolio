export const motionTokens = {
  uiHoverMs: 160,
  panelOpenMs: 280,
  cameraTravelMs: 1600,
  roomActivationMs: 420,
  reducedMotionMs: 1,
} as const;

export const easingTokens = {
  ui: 'power2.out',
  panel: 'power3.out',
  cinematic: 'power3.inOut',
  snap: 'power1.out',
} as const;

export function durationForMotion(
  reducedMotion: boolean,
  token: keyof typeof motionTokens,
): number {
  return reducedMotion ? motionTokens.reducedMotionMs : motionTokens[token];
}
