/** Shared island heightfield (Three.js: X east, Y up, Z south / camera). */

export const WATER_Y = -1.62;

function noise(x: number, z: number): number {
  return (
    0.46 * Math.sin(x * 0.19 + z * 0.16) +
    0.28 * Math.sin(x * 0.47 - z * 0.39) +
    0.16 * Math.sin(x * 0.93 + z * 0.71) +
    0.08 * Math.sin(x * 1.85 - z * 1.42) +
    0.04 * Math.sin(x * 3.1 + z * 2.4)
  );
}

/**
 * 0 on the architectural pad, 1 at the first terrace edge, >1 stepping toward water.
 * Elongated south toward the hero camera; west shelf holds the identity monolith.
 */
function radial(x: number, z: number): number {
  const nx = (x + 3.2) / 21.4;
  const nzSouth = Math.max(0, z - 6.8) / 10.6;
  const nzNorth = Math.max(0, -z - 8.0) / 13.5;
  const nz = Math.max(nzSouth, nzNorth * 0.72);
  const box = Math.sqrt(nx * nx * 0.92 + nz * nz);
  const wobble = 0.08 * noise(x * 0.22, z * 0.2);
  return box + wobble;
}

export function heightAt(x: number, z: number): number {
  const n = noise(x, z);
  const u = radial(x, z);

  const gorge =
    Math.exp(-((x + 11.5) * (x + 11.5)) / 5.4) *
    Math.exp(-((z - 11.8) * (z - 11.8)) / 36) *
    (z > 6.5 ? 1 : 0.15);
  const path = Math.exp(-(x * x) / 16) * Math.max(0, Math.min(1, (z - 6.2) / 16));
  const westShelf = Math.exp(-((x + 28.2) * (x + 28.2)) / 28) * Math.exp(-(z * z) / 40);

  let y: number;
  if (u < 0.92) {
    y = 0.04 + n * 0.03;
  } else if (u < 1.18) {
    const t = (u - 0.92) / 0.26;
    y = 0.04 - t * 0.62 + n * 0.07;
  } else if (u < 1.48) {
    const t = (u - 1.18) / 0.3;
    y = -0.58 - t * 0.72 + n * 0.11;
  } else if (u < 1.82) {
    const t = (u - 1.48) / 0.34;
    y = -1.3 - t * 0.28 + n * 0.09;
  } else if (u < 2.12) {
    const t = (u - 1.82) / 0.3;
    y = -1.58 - t * 0.42 + n * 0.07;
  } else {
    y = -2.12 + n * 0.04;
  }

  y -= path * 0.38;
  y -= gorge * 1.35;
  y += westShelf * 0.22;
  return y;
}

export function terrainColor(x: number, z: number, y: number): [number, number, number] {
  const u = radial(x, z);
  const wet = y < WATER_Y + 0.22 ? 1 : Math.max(0, (WATER_Y + 0.55 - y) / 0.55);
  if (wet > 0.45) {
    return [0.16 + wet * 0.04, 0.18, 0.2];
  }
  if (u < 0.95) {
    return [0.42, 0.43, 0.45];
  }
  if (u < 1.22) {
    return [0.28, 0.34, 0.24];
  }
  if (u < 1.52) {
    return [0.36, 0.34, 0.32];
  }
  return [0.3, 0.31, 0.33];
}

export type ShoreSample = { x: number; z: number; y: number; theta: number };

export function sampleShoreline(count = 96): ShoreSample[] {
  const samples: ShoreSample[] = [];
  for (let i = 0; i < count; i += 1) {
    const theta = (i / count) * Math.PI * 2;
    let lo = 8;
    let hi = 38;
    for (let k = 0; k < 14; k += 1) {
      const mid = (lo + hi) * 0.5;
      const x = Math.cos(theta) * mid - 3.2;
      const z = Math.sin(theta) * mid + 6.8;
      if (heightAt(x, z) > WATER_Y) {
        lo = mid;
      } else {
        hi = mid;
      }
    }
    const r = (lo + hi) * 0.5;
    const x = Math.cos(theta) * r - 3.2;
    const z = Math.sin(theta) * r + 6.8;
    samples.push({ x, z, y: heightAt(x, z), theta });
  }
  return samples;
}

export const HERO_TREE_SITES: Array<{
  position: [number, number, number];
  scale: number;
  yaw: number;
  lod: 0 | 1 | 2;
}> = [
  { position: [-7.8, 0, 11.4], scale: 1.0, yaw: 0.42, lod: 0 },
  { position: [8.4, 0, 10.6], scale: 0.94, yaw: 1.85, lod: 0 },
  { position: [-14.2, 0, 7.2], scale: 0.82, yaw: 2.55, lod: 0 },
  { position: [13.6, 0, 6.8], scale: 0.8, yaw: 4.2, lod: 0 },
  { position: [-20.4, 0, 12.8], scale: 1.06, yaw: 0.95, lod: 1 },
  { position: [18.8, 0, 13.2], scale: 1.0, yaw: 5.1, lod: 1 },
  { position: [4.6, 0, 16.4], scale: 0.72, yaw: 1.4, lod: 1 },
  { position: [-22.8, 0, 18.6], scale: 1.12, yaw: 2.1, lod: 2 },
  { position: [21.6, 0, 19.2], scale: 1.08, yaw: 4.7, lod: 2 },
];
