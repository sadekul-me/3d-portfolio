import { WATER_Y, heightAt, sampleShoreline } from '@/experience/environment/islandHeight';

/** Ocean rest pose. Slightly below WATER_Y so troughs sit in the wet band. */
export const OCEAN_BASE_Y = WATER_Y - 0.02;

/**
 * Peak Gerstner amplitudes (metres). Sum is the theoretical stacked crest.
 * Horizontal Q is applied separately and kept < 1 so vertices cannot walk inland.
 */
export const OCEAN_WAVE_AMPLITUDES = [0.1, 0.055, 0.028, 0.012] as const;

export const OCEAN_MAX_WAVE_HEIGHT = OCEAN_WAVE_AMPLITUDES.reduce((sum, amp) => sum + amp, 0);

export const OCEAN_MAX_WAVE_Y = OCEAN_BASE_Y + OCEAN_MAX_WAVE_HEIGHT;

/** Seaward inflate of the shoreline hole, metres. */
export const OCEAN_EXCLUSION_EXPAND = 2.4;

/**
 * Dry-land samples on the architectural pad and upper terraces (not the wet beach).
 * Used for the MAX_WAVE_Y < MIN_DRY - margin invariant.
 */
export const DRY_LAND_SAMPLE_XZ: ReadonlyArray<readonly [number, number]> = [
  [0, 0],
  [0, 8],
  [-12, 4],
  [12, 4],
  [-20, 2],
  [18, 2],
  [-28.4, -1.7],
  [-8, 10],
  [8, 10],
  [-16, 8],
];

export function minDryLandY(): number {
  let min = Infinity;
  for (const [x, z] of DRY_LAND_SAMPLE_XZ) {
    min = Math.min(min, heightAt(x, z));
  }
  return min;
}

export const MIN_DRY_LAND_Y = minDryLandY();

export const WATER_SAFETY_MARGIN = 0.45;

export const WATER_CHANNEL = {
  x: -18.4,
  zStart: 6.9,
  zEnd: 10.8,
  width: 1.85,
  lipY: 5.45,
} as const;

/** True where ocean mesh/fragments are forbidden (dry island + exclusion inflate). */
export function isOceanForbidden(x: number, z: number): boolean {
  const nx = (x + 3.2) / 21.4;
  const nzSouth = Math.max(0, z - 6.8) / 10.6;
  const nzNorth = Math.max(0, -z - 8.0) / 13.5;
  const nz = Math.max(nzSouth, nzNorth * 0.72);
  const radial = Math.sqrt(nx * nx * 0.92 + nz * nz);
  if (radial < 2.02) {
    return true;
  }
  return heightAt(x, z) > OCEAN_MAX_WAVE_Y + WATER_SAFETY_MARGIN;
}

export function expandedShoreline(count = 96): Array<{ x: number; z: number; theta: number }> {
  return sampleShoreline(count).map((sample) => {
    const dx = sample.x + 3.2;
    const dz = sample.z - 6.8;
    const len = Math.hypot(dx, dz) || 1;
    return {
      x: sample.x + (dx / len) * OCEAN_EXCLUSION_EXPAND,
      z: sample.z + (dz / len) * OCEAN_EXCLUSION_EXPAND,
      theta: sample.theta,
    };
  });
}

export const OCEAN_GLSL_EXCLUSION = `
float oceanRadial(vec2 xz) {
  float nx = (xz.x + 3.2) / 21.4;
  float nzSouth = max(0.0, xz.y - 6.8) / 10.6;
  float nzNorth = max(0.0, -xz.y - 8.0) / 13.5;
  float nz = max(nzSouth, nzNorth * 0.72);
  return sqrt(nx * nx * 0.92 + nz * nz);
}

bool oceanForbidden(vec2 xz) {
  return oceanRadial(xz) < 2.02;
}
`;
