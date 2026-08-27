import type { AssetManifest } from '@/assets/registry/assetRegistry';

export const EXTERIOR_MAIN_ASSET_ID = 'exterior-main';

export const EXTERIOR_GLB_URL = '/assets/world/exterior/digital-residence-exterior.glb';

export function createExteriorManifest(): AssetManifest {
  return {
    id: 'room-exterior',
    version: '0.2.0',
    roomId: 'exterior',
    assets: [
      {
        id: EXTERIOR_MAIN_ASSET_ID,
        kind: 'glb',
        url: EXTERIOR_GLB_URL,
        bytesEstimate: 697_248,
        qualityVariants: {
          HIGH: EXTERIOR_GLB_URL,
          BALANCED: EXTERIOR_GLB_URL,
          LOW: EXTERIOR_GLB_URL,
        },
        preloadPriority: 'critical',
        state: 'UNLOADED',
      },
    ],
  };
}
