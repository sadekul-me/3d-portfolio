export const ASSET_LIFECYCLE_STATES = ['UNLOADED', 'QUEUED', 'LOADING', 'READY', 'FAILED'] as const;
export type AssetLifecycleState = (typeof ASSET_LIFECYCLE_STATES)[number];

export type AssetKind = 'glb' | 'ktx2' | 'audio' | 'image' | 'video' | 'json';

export type AssetRecord = {
  id: string;
  kind: AssetKind;
  url: string;
  bytesEstimate: number;
  qualityVariants: Partial<Record<'HIGH' | 'BALANCED' | 'LOW', string>>;
  fallbackAssetId?: string;
  state: AssetLifecycleState;
  preloadPriority: 'critical' | 'high' | 'normal' | 'low';
};

export function nextAssetState(
  current: AssetLifecycleState,
  event: 'queue' | 'start' | 'succeed' | 'fail' | 'reset',
): AssetLifecycleState {
  switch (event) {
    case 'queue':
      return current === 'READY' ? 'READY' : 'QUEUED';
    case 'start':
      return current === 'QUEUED' || current === 'UNLOADED' ? 'LOADING' : current;
    case 'succeed':
      return current === 'LOADING' ? 'READY' : current;
    case 'fail':
      return current === 'LOADING' || current === 'QUEUED' ? 'FAILED' : current;
    case 'reset':
      return 'UNLOADED';
    default:
      return current;
  }
}
