import { useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { DoubleSide, ShaderMaterial, Vector3 } from 'three';

import { VISUAL_LOOK_PROFILES, type VisualLook } from '@/experience/look/visualLook';
import { WATER_Y } from '@/experience/environment/islandHeight';

const VERTEX = `
uniform float uTime;
varying vec3 vWorld;
varying float vHeight;
varying float vShore;

void gerstner(inout vec3 pos, vec2 dir, float steep, float amp, float freq, float speed) {
  vec2 d = normalize(dir);
  float q = steep / max(freq * amp, 0.0001);
  float theta = dot(d, pos.xy) * freq + uTime * speed;
  float s = sin(theta);
  float c = cos(theta);
  pos.x += q * amp * d.x * c;
  pos.y += q * amp * d.y * c;
  pos.z += amp * s;
}

void main() {
  vec3 pos = position;
  gerstner(pos, vec2(1.0, 0.32), 0.32, 0.28, 0.055, 0.72);
  gerstner(pos, vec2(-0.72, 0.78), 0.26, 0.16, 0.09, 1.05);
  gerstner(pos, vec2(0.18, -1.0), 0.18, 0.08, 0.16, 1.45);
  gerstner(pos, vec2(0.9, 0.55), 0.12, 0.035, 0.34, 2.1);
  vHeight = pos.z - position.z;
  vec4 world = modelMatrix * vec4(pos, 1.0);
  vWorld = world.xyz;
  vShore = length(vec2(world.x + 3.0, world.z - 6.5));
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
varying vec3 vWorld;
varying float vHeight;
varying float vShore;

void main() {
  vec3 view = normalize(cameraPosition - vWorld);
  vec3 nrm = normalize(vec3(-dFdx(vHeight) * 5.2, 1.0, -dFdy(vHeight) * 5.2));
  nrm.x += 0.045 * sin(vWorld.x * 9.4 + uTime * 2.2) + 0.02 * sin(vWorld.z * 17.0 - uTime * 3.1);
  nrm.z += 0.045 * cos(vWorld.z * 8.6 - uTime * 1.8) + 0.02 * cos(vWorld.x * 15.5 + uTime * 2.6);
  nrm = normalize(nrm);
  float ndv = max(dot(view, nrm), 0.0);
  float fresnel = pow(1.0 - ndv, 3.2);
  float shore = smoothstep(30.0, 19.0, vShore);
  float depthMix = clamp(shore * 0.72 + fresnel * 0.22, 0.0, 1.0);
  vec3 col = mix(uDeep, uShallow, depthMix);
  col = mix(col, uSky, fresnel * 0.55);
  vec3 halfV = normalize(view + normalize(uSunDir));
  col += uSpec * pow(max(dot(nrm, halfV), 0.0), 48.0) * 1.05;
  float foam = shore * (0.28 + 0.72 * sin(vShore * 1.55 - uTime * 1.45 + vWorld.x * 0.08));
  col += vec3(0.88, 0.94, 1.0) * foam * 0.26;
  float sparkle = pow(max(dot(nrm, halfV), 0.0), 180.0) * (0.35 + 0.65 * sin(uTime * 4.0 + vWorld.x));
  col += uSpec * sparkle * 0.55;
  gl_FragColor = vec4(col, 0.96);
}
`;

export function IslandOcean({ look }: { look: VisualLook }) {
  const profile = VISUAL_LOOK_PROFILES[look];
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
        },
        vertexShader: VERTEX,
        fragmentShader: FRAGMENT,
        transparent: true,
        depthWrite: false,
        side: DoubleSide,
      }),
    [profile],
  );

  useFrame((_, delta) => {
    const time = material.uniforms.uTime;
    if (time) {
      time.value = (time.value as number) + delta;
    }
  });

  return (
    <mesh
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, WATER_Y - 0.04, 4]}
      material={material}
      frustumCulled={false}
    >
      <circleGeometry args={[180, 192]} />
    </mesh>
  );
}
