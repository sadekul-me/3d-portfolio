import type { PreloadPriority } from '@/content/domain/models';
import type { RoomId } from '@/types/ids';

export type LoadingPlan = {
  current: RoomId;
  preload: RoomId[];
  lazy: RoomId[];
};

export function planRoomLoading(
  current: RoomId,
  adjacent: readonly RoomId[],
  all: readonly RoomId[],
): LoadingPlan {
  const preload = adjacent.filter((roomId) => roomId !== current);
  const lazy = all.filter((roomId) => roomId !== current && !preload.includes(roomId));
  return { current, preload, lazy };
}

export function comparePreloadPriority(left: PreloadPriority, right: PreloadPriority): number {
  const rank: Record<PreloadPriority, number> = {
    critical: 0,
    high: 1,
    normal: 2,
    low: 3,
  };
  return rank[left] - rank[right];
}
