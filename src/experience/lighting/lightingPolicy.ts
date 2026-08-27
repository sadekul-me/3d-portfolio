export const LIGHTING_PROFILES = ['arrival', 'interior', 'lab', 'gallery', 'command'] as const;
export type LightingProfile = (typeof LIGHTING_PROFILES)[number];

export type LightingBudget = {
  profile: LightingProfile;
  shadows: boolean;
  maxLights: number;
};
