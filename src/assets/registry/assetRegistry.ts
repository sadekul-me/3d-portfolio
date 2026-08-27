import type { RoomId } from '@/types/ids';
import type { QualityPreset } from '@/types/experience';
import type { AssetKind, AssetRecord } from '@/assets/loaders/assetLifecycle';

export type AssetManifest = {
  id: string;
  version: string;
  roomId?: RoomId;
  assets: AssetRecord[];
};

export type RegisteredAsset = Omit<AssetRecord, 'state'> & {
  compatibleQuality: QualityPreset[];
};

const registry = new Map<string, RegisteredAsset>();

export function registerAsset(asset: RegisteredAsset): void {
  registry.set(asset.id, asset);
}

export function getRegisteredAsset(id: string): RegisteredAsset | undefined {
  return registry.get(id);
}

export function listAssetsByKind(kind: AssetKind): RegisteredAsset[] {
  return [...registry.values()].filter((asset) => asset.kind === kind);
}

export function clearAssetRegistry(): void {
  registry.clear();
}

export function selectAssetUrl(
  asset: RegisteredAsset,
  quality: Exclude<QualityPreset, 'AUTO'>,
): string {
  return asset.qualityVariants[quality] ?? asset.url;
}
