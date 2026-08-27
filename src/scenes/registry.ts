import type { RoomDefinition } from '@/content/domain/models';
import { loadCatalog } from '@/content/repositories/catalogRepository';
import type { RoomId } from '@/types/ids';

export type SceneModule = {
  roomId: RoomId;
  definition: RoomDefinition;
};

export function getSceneModule(roomId: RoomId): SceneModule {
  const definition = loadCatalog().rooms.find((room) => room.id === roomId);
  if (!definition) {
    throw new Error(`Unknown room: ${roomId}`);
  }
  return { roomId, definition };
}

export function listSceneModules(): SceneModule[] {
  return loadCatalog().rooms.map((definition) => ({ roomId: definition.id, definition }));
}
