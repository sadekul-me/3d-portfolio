import { describe, expect, it } from 'vitest';

import {
  ARCHITECTURE_BOUNDS,
  CAM_HERO_EXTERIOR_16X9,
  DEFAULT_EXTERIOR_CAMERA,
  EXTERIOR_CAMERA_IDS,
  ISLAND_BOUNDS,
  focalMmFromVerticalFov,
  makeFramedCamera,
  measureBoundsOccupancy,
  resolveExteriorCamera,
} from '@/experience/camera/exteriorCameras';

const DESKTOP_ASPECTS: Array<[number, number]> = [
  [1920, 1080],
  [2560, 1440],
  [3840, 2160],
  [1680, 1050],
  [2560, 1080],
];

describe('exterior camera presets', () => {
  it('registers the locked Exterior set with CAM_Hero_Exterior as default', () => {
    expect(EXTERIOR_CAMERA_IDS).toEqual([
      'CAM_Hero_Exterior',
      'CAM_Front_Exterior',
      'CAM_ThreeQuarter_Left',
      'CAM_ThreeQuarter_Right',
      'CAM_Entrance_Closeup',
      'CAM_Elevated_Island',
    ]);
    expect(DEFAULT_EXTERIOR_CAMERA).toBe('CAM_Hero_Exterior');
  });

  it('keeps the failed close-up only as CAM_Entrance_Closeup', () => {
    const close = resolveExteriorCamera('CAM_Entrance_Closeup', 1920, 1080);
    const hero = resolveExteriorCamera('CAM_Hero_Exterior', 1920, 1080);
    expect(close.position).toEqual([17.2, 8.35, 20.6]);
    expect(close.target).toEqual([-3.8, 5.4, -0.8]);
    expect(hero.position[2]).toBeGreaterThan(close.position[2] + 8);
    expect(hero.minDistance).toBeGreaterThan(22);
  });

  it('uses a 40–50mm equivalent vertical FOV on the hero', () => {
    const hero = CAM_HERO_EXTERIOR_16X9;
    expect(hero.focalMm).toBeGreaterThanOrEqual(40);
    expect(hero.focalMm).toBeLessThanOrEqual(50);
    expect(focalMmFromVerticalFov(hero.vfovDeg)).toBeCloseTo(hero.focalMm, 5);
  });

  it.each(DESKTOP_ASPECTS)(
    'frames the campus inside composition targets at %dx%d',
    (width, height) => {
      const pose = resolveExteriorCamera('CAM_Hero_Exterior', width, height);
      const aspect = width / height;
      const camera = makeFramedCamera(pose, aspect);
      const building = measureBoundsOccupancy(camera, ARCHITECTURE_BOUNDS);
      const island = measureBoundsOccupancy(camera, ISLAND_BOUNDS);

      expect(building.width).toBeGreaterThanOrEqual(0.58);
      expect(building.width).toBeLessThanOrEqual(0.88);
      expect(island.width).toBeGreaterThanOrEqual(0.68);
      expect(pose.position[2]).toBeGreaterThan(48);
      expect(pose.position[1]).toBeLessThan(23);
    },
  );
});
