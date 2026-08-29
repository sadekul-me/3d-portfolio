import { describe, expect, it } from 'vitest';

import {
  heightAt,
  HERO_TREE_SITES,
  sampleShoreline,
  WATER_Y,
} from '@/experience/environment/islandHeight';

describe('island heightfield', () => {
  it('keeps the architectural pad above the waterline', () => {
    expect(heightAt(0, 0)).toBeGreaterThan(WATER_Y + 1.2);
    expect(heightAt(-18, 2)).toBeGreaterThan(WATER_Y + 0.8);
    expect(heightAt(0, 22)).toBeLessThan(WATER_Y + 0.35);
  });

  it('samples a closed shoreline', () => {
    const shore = sampleShoreline(48);
    expect(shore.length).toBe(48);
    expect(shore.every((p) => Math.abs(p.y - WATER_Y) < 1.2)).toBe(true);
  });

  it('grounds hero trees on land', () => {
    for (const tree of HERO_TREE_SITES) {
      expect(heightAt(tree.position[0], tree.position[2])).toBeGreaterThan(WATER_Y);
    }
  });
});
