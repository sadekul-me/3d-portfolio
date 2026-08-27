import { createExteriorManifest } from '@/assets/manifests/exteriorManifest';
import { registerAsset } from '@/assets/registry/assetRegistry';

export function registerDefaultAssets(): void {
  for (const asset of createExteriorManifest().assets) {
    const { state: _state, ...record } = asset;
    registerAsset({
      ...record,
      compatibleQuality: ['AUTO', 'HIGH', 'BALANCED', 'LOW'],
    });
  }
}
