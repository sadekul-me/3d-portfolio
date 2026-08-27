import type { RoomId } from '@/types/ids';

export type CameraTravelOptions = {
  reducedMotion: boolean;
  interruptible: boolean;
};

/**
 * GSAP owns cinematic camera timelines. React/Zustand never store per-frame transforms.
 */
export type CameraDirector = {
  travelTo(roomId: RoomId, options: CameraTravelOptions): Promise<void>;
  interrupt(): void;
  dispose(): void;
};

export const CAMERA_MOTION_CATEGORY = 'cinematic' as const;
