import { useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import {
  BufferAttribute,
  BufferGeometry,
  ShaderMaterial,
  Vector3,
} from 'three';

import { VISUAL_LOOK_PROFILES, type VisualLook } from '@/experience/look/visualLook';
import {
  OCEAN_BASE_Y,
  OCEAN_GLSL_EXCLUSION,
  expandedShoreline,
  isOceanForbidden,
} from '@/experience/environment/waterContainment';

const VERTEX = `
uniform float uTime;
varying vec3 vWorld;
varying float vHeight;

void gerstner(inout vec3 pos, vec2 dir, float q, float amp, float freq, float speed) {
  vec2 d = normalize(dir);
  float theta = dot(d, pos.xz) * freq + uTime * speed;
  float s = sin(theta);
  float c = cos(theta);
  pos.x += q * amp * d.x * c;
  pos.z += q * amp * d.y * c;
  pos.y += amp * s;
}

void main() {
  vec3 pos = position;
  gerstner(pos, vec2(1.0, 0.32), 0.42, 0.10, 0.055, 0.72);
  gerstner(pos, vec2(-0.72, 0.78), 0.38, 0.055, 0.09, 1.05);
  gerstner(pos, vec2(0.18, -1.0), 0.32, 0.028, 0.16, 1.45);
  gerstner(pos, vec2(0.9, 0.55), 0.28, 0.012, 0.34, 2.1);
  vHeight = pos.y - position.y;
  vec4 world = modelMatrix * vec4(pos, 1.0);
  vWorld = world.xyz;
  gl_Position = projectionMatrix * viewMatrix * world;
}
`;

const FRAGMENT = `
uniform vec3 uDeep;
uniform vec3 uShallow;
uniform vec3 uSpec;
uniform vec3 uSky;
uniform vec3 uSunDir;
uniform float uTime;
uniform float uDebug;
varying vec3 vWorld;
varying float vHeight;

${OCEAN_GLSL_EXCLUSION}

void main() {
  if (oceanForbidden(vWorld.xz)) {
    discard;
  }
  if (uDebug > 0.5) {
    gl_FragColor = vec4(0.12, 0.38, 0.92, 0.92);
    return;
  }
  vec3 view = normalize(cameraPosition - vWorld);
  vec3 nrm = normalize(vec3(-dFdx(vHeight) * 5.2, 1.0, -dFdy(vHeight) * 5.2));
  nrm.x += 0.045 * sin(vWorld.x * 9.4 + uTime * 2.2) + 0.02 * sin(vWorld.z * 17.0 - uTime * 3.1);
  nrm.z += 0.045 * cos(vWorld.z * 8.6 - uTime * 1.8) + 0.02 * cos(vWorld.x * 15.5 + uTime * 2.6);
  nrm = normalize(nrm);
  float ndv = max(dot(view, nrm), 0.0);
  float fresnel = pow(1.0 - ndv, 3.2);
  float shore = smoothstep(2.45, 2.08, oceanRadial(vWorld.xz));
  float depthMix = clamp(shore * 0.72 + fresnel * 0.22, 0.0, 1.0);
  vec3 col = mix(uDeep, uShallow, depthMix);
  col = mix(col, uSky, fresnel * 0.55);
  vec3 halfV = normalize(view + normalize(uSunDir));
  col += uSpec * pow(max(dot(nrm, halfV), 0.0), 48.0) * 1.05;
  float foam = shore * (0.28 + 0.72 * sin(oceanRadial(vWorld.xz) * 8.0 - uTime * 1.45 + vWorld.x * 0.08));
  col += vec3(0.88, 0.94, 1.0) * foam * 0.26;
  float sparkle = pow(max(dot(nrm, halfV), 0.0), 180.0) * (0.35 + 0.65 * sin(uTime * 4.0 + vWorld.x));
  col += uSpec * sparkle * 0.55;
  gl_FragColor = vec4(col, 0.96);
}
`;

const OUTER_RADIUS = 165;
const RADIAL_SEGS = 14;

function buildOceanRingGeometry(): BufferGeometry {
  const shore = expandedShoreline(96);
  const ringCount = shore.length;
  const positions: number[] = [];
  const uvs: number[] = [];
  const indices: number[] = [];

  for (let r = 0; r <= RADIAL_SEGS; r += 1) {
    const t = r / RADIAL_SEGS;
    for (let i = 0; i < ringCount; i += 1) {
      const sample = shore[i]!;
      const outerX = Math.cos(sample.theta) * OUTER_RADIUS - 3.2;
      const outerZ = Math.sin(sample.theta) * OUTER_RADIUS + 6.8;
      const x = sample.x * (1 - t) + outerX * t;
      const z = sample.z * (1 - t) + outerZ * t;
      positions.push(x, 0, z);
      uvs.push(i / ringCount, t);
    }
  }

  for (let r = 0; r < RADIAL_SEGS; r += 1) {
    for (let i = 0; i < ringCount; i += 1) {
      const a = r * ringCount + i;
      const b = r * ringCount + ((i + 1) % ringCount);
      const c = (r + 1) * ringCount + i;
      const d = (r + 1) * ringCount + ((i + 1) % ringCount);
      const ax = positions[a * 3]!;
      const az = positions[a * 3 + 2]!;
      const bx = positions[b * 3]!;
      const bz = positions[b * 3 + 2]!;
      const cx = positions[c * 3]!;
      const cz = positions[c * 3 + 2]!;
      const mx = (ax + bx + cx) / 3;
      const mz = (az + bz + cz) / 3;
      if (isOceanForbidden(mx, mz)) {
        continue;
      }
      indices.push(a, c, b, b, c, d);
    }
  }

  const geometry = new BufferGeometry();
  geometry.setAttribute('position', new BufferAttribute(new Float32Array(positions), 3));
  geometry.setAttribute('uv', new BufferAttribute(new Float32Array(uvs), 2));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  return geometry;
}

export function IslandOcean({ look }: { look: VisualLook }) {
  const profile = VISUAL_LOOK_PROFILES[look];
  const debug =
    typeof window !== 'undefined' && new URLSearchParams(window.location.search).has('debugWater');
  const geometry = useMemo(() => buildOceanRingGeometry(), []);
  const material = useMemo(
    () =>
      new ShaderMaterial({
        uniforms: {
          uTime: { value: 0 },
          uDeep: { value: new Vector3(...profile.oceanDeep) },
          uShallow: { value: new Vector3(...profile.oceanShallow) },
          uSpec: { value: new Vector3(...profile.oceanSpecular) },
          uSky: { value: new Vector3(...profile.skyHorizon) },
          uSunDir: { value: new Vector3(...profile.sunDir).normalize() },
          uDebug: { value: debug ? 1 : 0 },
        },
        vertexShader: VERTEX,
        fragmentShader: FRAGMENT,
        transparent: true,
        depthWrite: true,
      }),
    [profile, debug],
  );

  useFrame((_, delta) => {
    const time = material.uniforms.uTime;
    if (time) {
      time.value = (time.value as number) + delta;
    }
  });

  return (
    <mesh
      geometry={geometry}
      position={[0, OCEAN_BASE_Y, 0]}
      material={material}
      frustumCulled={false}
      name="WATER_OCEAN"
      renderOrder={-10}
    />
  );
}
