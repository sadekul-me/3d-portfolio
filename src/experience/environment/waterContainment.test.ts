import { describe, expect, it } from 'vitest';

import { WATER_Y, heightAt } from '@/experience/environment/islandHeight';
import {
  DRY_LAND_SAMPLE_XZ,
  MIN_DRY_LAND_Y,
  OCEAN_BASE_Y,
  OCEAN_MAX_WAVE_HEIGHT,
  OCEAN_MAX_WAVE_Y,
  WATER_CHANNEL,
  WATER_SAFETY_MARGIN,
  isOceanForbidden,
} from '@/experience/environment/waterContainment';

describe('water containment', () => {
  it('keeps stacked ocean crests below dry land with a safety margin', () => {
    expect(OCEAN_BASE_Y).toBeLessThan(WATER_Y);
    expect(OCEAN_MAX_WAVE_HEIGHT).toBeLessThan(0.22);
    expect(OCEAN_MAX_WAVE_Y).toBeLessThan(MIN_DRY_LAND_Y - WATER_SAFETY_MARGIN);
    expect(MIN_DRY_LAND_Y - OCEAN_MAX_WAVE_Y).toBeGreaterThanOrEqual(WATER_SAFETY_MARGIN);
  });

  it('forbids ocean on the architectural pad and identity shelf', () => {
    expect(isOceanForbidden(0, 0)).toBe(true);
    expect(isOceanForbidden(-28.4, -1.7)).toBe(true);
    expect(isOceanForbidden(-12, 8)).toBe(true);
    expect(isOceanForbidden(0, 8)).toBe(true);
  });

  it('allows ocean well outside the shoreline', () => {
    expect(isOceanForbidden(0, 48)).toBe(false);
    expect(isOceanForbidden(55, 8)).toBe(false);
    expect(isOceanForbidden(-55, 8)).toBe(false);
  });

  it('keeps sampled dry land above the wave ceiling', () => {
    for (const [x, z] of DRY_LAND_SAMPLE_XZ) {
      expect(heightAt(x, z)).toBeGreaterThan(OCEAN_MAX_WAVE_Y + WATER_SAFETY_MARGIN);
    }
  });

  it('places the waterfall channel west of the entrance massing', () => {
    expect(WATER_CHANNEL.x).toBeLessThan(-16);
    expect(WATER_CHANNEL.width).toBeLessThan(2.2);
    expect(WATER_CHANNEL.zEnd - WATER_CHANNEL.zStart).toBeGreaterThan(2);
  });
});
