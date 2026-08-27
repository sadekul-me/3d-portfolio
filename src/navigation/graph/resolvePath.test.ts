import { describe, expect, it } from 'vitest';

import { createRoomGraph, resolvePath } from '@/navigation/graph/resolvePath';
import { ROOM_IDS } from '@/types/ids';

describe('room navigation graph', () => {
  it('contains every locked experience zone', () => {
    const graph = createRoomGraph();
    for (const roomId of ROOM_IDS) {
      expect(graph[roomId]).toBeDefined();
    }
  });

  it('resolves a BFS path between non-adjacent rooms', () => {
    const path = resolvePath('exterior', 'architecture');
    expect(path).not.toBeNull();
    expect(path?.rooms[0]).toBe('exterior');
    expect(path?.rooms.at(-1)).toBe('architecture');
    expect((path?.rooms.length ?? 0) > 1).toBe(true);
  });

  it('returns a single-node path when already at the target', () => {
    const path = resolvePath('identity', 'identity');
    expect(path?.rooms).toEqual(['identity']);
  });
});
