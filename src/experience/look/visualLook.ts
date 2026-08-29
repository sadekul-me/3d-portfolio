export const VISUAL_LOOKS = ['SYSTEM', 'CINEMATIC'] as const;
export type VisualLook = (typeof VISUAL_LOOKS)[number];

export type VisualLookProfile = {
  id: VisualLook;
  background: string;
  fog: string;
  fogNear: number;
  fogFar: number;
  exposure: number;
  skyHorizon: [number, number, number];
  skyMid: [number, number, number];
  skyZenith: [number, number, number];
  sunDir: [number, number, number];
  sunGlow: [number, number, number];
  sunPower: number;
  envHemisphere: string;
  envGround: string;
  envIntensity: number;
  hemisphereSky: string;
  hemisphereGround: string;
  hemisphereIntensity: number;
  ambient: string;
  ambientIntensity: number;
  sunPosition: [number, number, number];
  sunColor: string;
  sunIntensity: number;
  fillPosition: [number, number, number];
  fillColor: string;
  fillIntensity: number;
  rimPosition: [number, number, number];
  rimColor: string;
  rimIntensity: number;
  warmKeyPosition: [number, number, number];
  warmKeyColor: string;
  warmKeyIntensity: number;
  interiorBoost: number;
  oceanDeep: [number, number, number];
  oceanShallow: [number, number, number];
  oceanSpecular: [number, number, number];
  plantTint: string;
  stoneTint: string;
  glassColor: string;
  glassOpacity: number;
};

export const VISUAL_LOOK_PROFILES: Record<VisualLook, VisualLookProfile> = {
  SYSTEM: {
    id: 'SYSTEM',
    background: '#7eb4dc',
    fog: '#8ebfdc',
    fogNear: 70,
    fogFar: 220,
    exposure: 1.12,
    skyHorizon: [0.78, 0.86, 0.94],
    skyMid: [0.38, 0.62, 0.88],
    skyZenith: [0.12, 0.34, 0.72],
    sunDir: [0.28, 0.86, 0.42],
    sunGlow: [1.0, 0.96, 0.88],
    sunPower: 80,
    envHemisphere: '#e4eef8',
    envGround: '#4a5248',
    envIntensity: 1.18,
    hemisphereSky: '#d8e6f4',
    hemisphereGround: '#3a4038',
    hemisphereIntensity: 0.95,
    ambient: '#9aa8b0',
    ambientIntensity: 0.42,
    sunPosition: [18, 42, 16],
    sunColor: '#fff3dc',
    sunIntensity: 2.15,
    fillPosition: [6, 14, 28],
    fillColor: '#c8d8e8',
    fillIntensity: 0.55,
    rimPosition: [-24, 18, -8],
    rimColor: '#5ec4e0',
    rimIntensity: 0.32,
    warmKeyPosition: [4, 8, 14],
    warmKeyColor: '#ffd4a0',
    warmKeyIntensity: 0.22,
    interiorBoost: 5.2,
    oceanDeep: [0.02, 0.18, 0.26],
    oceanShallow: [0.05, 0.46, 0.52],
    oceanSpecular: [0.82, 0.92, 1.0],
    plantTint: '#ffffff',
    stoneTint: '#3f4348',
    glassColor: '#2a3844',
    glassOpacity: 0.16,
  },
  CINEMATIC: {
    id: 'CINEMATIC',
    background: '#1a1020',
    fog: '#3a2418',
    fogNear: 55,
    fogFar: 180,
    exposure: 1.38,
    skyHorizon: [1.0, 0.48, 0.12],
    skyMid: [0.32, 0.14, 0.1],
    skyZenith: [0.06, 0.07, 0.14],
    sunDir: [-0.78, 0.12, 0.32],
    sunGlow: [1.0, 0.48, 0.12],
    sunPower: 28,
    envHemisphere: '#f0c8a0',
    envGround: '#2a2030',
    envIntensity: 1.05,
    hemisphereSky: '#e8b080',
    hemisphereGround: '#241820',
    hemisphereIntensity: 0.72,
    ambient: '#6a4a48',
    ambientIntensity: 0.28,
    sunPosition: [-38, 5.5, 14],
    sunColor: '#ff7a28',
    sunIntensity: 2.55,
    fillPosition: [10, 12, 22],
    fillColor: '#6a88b0',
    fillIntensity: 0.48,
    rimPosition: [16, 10, -12],
    rimColor: '#ffb060',
    rimIntensity: 0.55,
    warmKeyPosition: [8, 8, 12],
    warmKeyColor: '#ff9a48',
    warmKeyIntensity: 0.7,
    interiorBoost: 8.4,
    oceanDeep: [0.03, 0.04, 0.08],
    oceanShallow: [0.28, 0.14, 0.08],
    oceanSpecular: [1.0, 0.62, 0.28],
    plantTint: '#f4ead8',
    stoneTint: '#3a3c40',
    glassColor: '#241c18',
    glassOpacity: 0.12,
  },
};
