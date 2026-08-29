import { describe, expect, it } from 'vitest';

import { VISUAL_LOOK_PROFILES, VISUAL_LOOKS } from '@/experience/look/visualLook';

describe('visual look profiles', () => {
  it('defines System and Cinematic on the same world', () => {
    expect(VISUAL_LOOKS).toEqual(['SYSTEM', 'CINEMATIC']);
    expect(VISUAL_LOOK_PROFILES.SYSTEM.exposure).toBeGreaterThan(1);
    expect(VISUAL_LOOK_PROFILES.CINEMATIC.sunColor).toMatch(/^#ff/);
    expect(VISUAL_LOOK_PROFILES.SYSTEM.stoneTint).toMatch(/^#3/);
    expect(VISUAL_LOOK_PROFILES.SYSTEM.oceanShallow[1]).toBeGreaterThan(
      VISUAL_LOOK_PROFILES.CINEMATIC.oceanDeep[1],
    );
  });
});
