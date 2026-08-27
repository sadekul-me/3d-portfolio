/** 60 FPS frame budget in milliseconds. Stability matters more than average FPS. */
export const FRAME_BUDGET_MS = 1000 / 60;

export const UPDATE_FREQUENCIES = {
  frameCriticalHz: 60,
  interactionHintHz: 15,
  analyticsHz: 1,
} as const;

export function isOverFrameBudget(frameTimeMs: number, budgetMs = FRAME_BUDGET_MS): boolean {
  return frameTimeMs > budgetMs;
}

/**
 * Render-loop rule: no uncontrolled O(n) work per frame.
 * Partition work by frequency instead of doing everything inside useFrame.
 */
export function shouldRunAtHz(elapsedMs: number, hz: number): boolean {
  const interval = 1000 / hz;
  return elapsedMs >= interval;
}
