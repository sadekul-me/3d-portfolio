import type { RoomId } from '@/types/ids';
import type { ExperienceMode, QualityPreset } from '@/types/experience';
import type { AssetLifecycleState } from '@/assets/loaders/assetLifecycle';

export type DiagnosticsSnapshot = {
  fps: number | null;
  frameTimeMs: number | null;
  drawCalls: number | null;
  triangles: number | null;
  currentRoom: RoomId | null;
  qualityMode: QualityPreset;
  experienceMode: ExperienceMode;
  assetReadyCount: number;
  assetTotalCount: number;
  aiStatus: 'idle' | 'healthy' | 'degraded' | 'unavailable';
  assetStatus: AssetLifecycleState | 'mixed';
};

export function createEmptyDiagnostics(
  qualityMode: QualityPreset,
  experienceMode: ExperienceMode,
): DiagnosticsSnapshot {
  return {
    fps: null,
    frameTimeMs: null,
    drawCalls: null,
    triangles: null,
    currentRoom: null,
    qualityMode,
    experienceMode,
    assetReadyCount: 0,
    assetTotalCount: 0,
    aiStatus: 'idle',
    assetStatus: 'UNLOADED',
  };
}

export function shouldExposeDiagnostics(flag: boolean, isDev: boolean): boolean {
  return isDev && flag;
}
