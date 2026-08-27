import { useAppStore } from '@/store/appStore';

export function useLocale() {
  return useAppStore((state) => state.preferences.locale);
}

export function useCurrentRoom() {
  return useAppStore((state) => state.navigation.currentRoomId);
}
