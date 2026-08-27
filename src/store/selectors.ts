import type { AppStoreState } from '@/store/types';
import { EXPERIENCE_MODE_RANK } from '@/types/experience';
import type { RoomId } from '@/types/ids';

export function selectCurrentRoomId(state: AppStoreState): RoomId {
  return state.navigation.currentRoomId;
}

export function selectIsTransitioning(state: AppStoreState): boolean {
  return state.navigation.phase === 'REQUESTED' || state.navigation.phase === 'TRANSITIONING';
}

export function selectLocale(state: AppStoreState) {
  return state.preferences.locale;
}

export function selectHasVisited(state: AppStoreState, roomId: RoomId): boolean {
  return state.navigation.visitedRoomIds.includes(roomId);
}

export function selectEffectiveExperienceRank(state: AppStoreState): number {
  const override = state.preferences.experienceModeOverride;
  if (!override) {
    return EXPERIENCE_MODE_RANK.PREMIUM_3D;
  }
  return EXPERIENCE_MODE_RANK[override];
}

export function selectSelectedProjectId(state: AppStoreState) {
  return state.selection.projectId;
}
