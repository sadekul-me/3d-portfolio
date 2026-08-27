import { loadCatalog } from '@/content/repositories/catalogRepository';
import type { RoomId } from '@/types/ids';
import { isRoomId } from '@/types/ids';

export const FALLBACK_ROOM_ID: RoomId = 'identity';

export type RoomGraph = Record<RoomId, readonly RoomId[]>;

export function createRoomGraph(): RoomGraph {
  const catalog = loadCatalog();
  const graph = {} as RoomGraph;
  for (const room of catalog.rooms) {
    graph[room.id] = room.adjacentRoomIds;
  }
  return graph;
}

export type NavigationPath = {
  from: RoomId;
  to: RoomId;
  rooms: RoomId[];
};

/**
 * Unweighted BFS. Compatible with a later Dijkstra/A* adapter for cinematic weights.
 */
export function resolvePath(
  from: RoomId,
  to: RoomId,
  graph = createRoomGraph(),
): NavigationPath | null {
  if (from === to) {
    return { from, to, rooms: [from] };
  }

  const queue: RoomId[] = [from];
  const visited = new Set<RoomId>([from]);
  const parent = new Map<RoomId, RoomId>();

  while (queue.length > 0) {
    const current = queue.shift();
    if (!current) {
      break;
    }
    const neighbors = graph[current] ?? [];
    for (const neighbor of neighbors) {
      if (visited.has(neighbor)) {
        continue;
      }
      visited.add(neighbor);
      parent.set(neighbor, current);
      if (neighbor === to) {
        return { from, to, rooms: reconstruct(parent, from, to) };
      }
      queue.push(neighbor);
    }
  }

  return null;
}

function reconstruct(parent: Map<RoomId, RoomId>, from: RoomId, to: RoomId): RoomId[] {
  const rooms: RoomId[] = [to];
  let cursor = to;
  while (cursor !== from) {
    const next = parent.get(cursor);
    if (!next) {
      return [from, to];
    }
    rooms.push(next);
    cursor = next;
  }
  rooms.reverse();
  return rooms;
}

export function resolveDestination(target: string, graph = createRoomGraph()): RoomId | null {
  if (!isRoomId(target)) {
    return null;
  }
  return graph[target] ? target : null;
}
