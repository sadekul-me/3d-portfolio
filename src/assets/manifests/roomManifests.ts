import type { RoomId } from '@/types/ids';
import type { AssetManifest } from '@/assets/registry/assetRegistry';

/**
 * Room-level manifests without shipping Blender source or final art.
 * URLs are structural placeholders; loaders must tolerate FAILED and use fallbacks.
 */
export function createEmptyRoomManifest(roomId: RoomId): AssetManifest {
  return {
    id: `room-${roomId}`,
    version: '0.1.0',
    roomId,
    assets: [],
  };
}

export const ROOM_MANIFEST_IDS = {
  exterior: 'room-exterior',
  identity: 'room-identity',
  engineering: 'room-engineering',
  'ai-lab': 'room-ai-lab',
  projects: 'room-projects',
  architecture: 'room-architecture',
  'command-center': 'room-command-center',
} as const;
