import { useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { useTexture } from '@react-three/drei';
import { AdditiveBlending, DoubleSide, RepeatWrapping, ShaderMaterial, Vector3 } from 'three';

import type { VisualLook } from '@/experience/look/visualLook';
import { WATER_Y } from '@/experience/environment/islandHeight';
import { WATER_CHANNEL } from '@/experience/environment/waterContainment';

const FOAM_URL = '/assets/world/water/water-foam-shore.png';

const VERTEX = `
uniform float uTime;
varying vec2 vUv;
varying vec3 vWorld;
void main() {
  vUv = uv;
  vec3 pos = position;
  pos.x += 0.015 * sin(uv.y * 28.0 + uTime * 3.2);
  pos.z += 0.02 * sin(uv.y * 18.0 - uTime * 2.4);
  vec4 world = modelMatrix * vec4(pos, 1.0);
  vWorld = world.xyz;
  gl_Position = projectionMatrix * viewMatrix * world;
}
`;

const FRAGMENT = `
uniform float uTime;
uniform vec3 uTint;
varying vec2 vUv;
varying vec3 vWorld;
void main() {
  float flow = fract(vUv.y * 5.2 - uTime * 0.85);
  float bands = smoothstep(0.0, 0.16, flow) * smoothstep(1.0, 0.62, flow);
  float streaks = pow(max(sin((vUv.x + 0.04 * sin(vUv.y * 40.0 - uTime * 2.0)) * 18.0), 0.0), 4.0);
  float edge = smoothstep(0.0, 0.1, vUv.x) * smoothstep(1.0, 0.9, vUv.x);
  float mist = pow(1.0 - vUv.y, 2.1);
  vec3 col = mix(uTint, vec3(0.92, 0.96, 0.98), mist * 0.55 + bands * 0.22 + streaks * 0.12);
  float alpha = (0.28 + bands * 0.48 + streaks * 0.18 + mist * 0.32) * edge;
  gl_FragColor = vec4(col, alpha);
}
`;

const SHEETS: Array<{
  position: [number, number, number];
  rotation: [number, number, number];
  size: [number, number];
}> = [
  { position: [WATER_CHANNEL.x, 4.55, 8.15], rotation: [0.22, 0, 0], size: [WATER_CHANNEL.width, 2.35] },
  { position: [WATER_CHANNEL.x, 2.55, 8.95], rotation: [0.48, 0, 0], size: [1.72, 2.15] },
  { position: [WATER_CHANNEL.x, 0.55, 9.75], rotation: [0.78, 0, 0], size: [1.58, 1.85] },
  { position: [WATER_CHANNEL.x, -0.85, 10.45], rotation: [1.05, 0, 0], size: [1.42, 1.45] },
];

export function WaterFeature({ look }: { look: VisualLook }) {
  const foam = useTexture(FOAM_URL);
  foam.wrapS = RepeatWrapping;
  foam.wrapT = RepeatWrapping;
  const material = useMemo(
    () =>
      new ShaderMaterial({
        uniforms: {
          uTime: { value: 0 },
          uTint: {
            value: look === 'SYSTEM' ? new Vector3(0.42, 0.72, 0.8) : new Vector3(0.78, 0.5, 0.24),
          },
        },
        vertexShader: VERTEX,
        fragmentShader: FRAGMENT,
        transparent: true,
        depthWrite: false,
        side: DoubleSide,
      }),
    [look],
  );

  useFrame((_, delta) => {
    const time = material.uniforms.uTime;
    if (time) {
      time.value = (time.value as number) + delta;
    }
    foam.offset.y -= delta * 0.35;
  });

  const basinZ = WATER_CHANNEL.zEnd + 0.45;
  const debug =
    typeof window !== 'undefined' && new URLSearchParams(window.location.search).has('debugWater');

  return (
    <group name="WATER_WATERFALL">
      {SHEETS.map((sheet, index) => (
        <mesh key={index} position={sheet.position} rotation={sheet.rotation} material={material}>
          <planeGeometry args={[sheet.size[0], sheet.size[1], 4, 20]} />
        </mesh>
      ))}
      <mesh
        name="WATER_BASIN"
        position={[WATER_CHANNEL.x, WATER_Y + 0.07, basinZ]}
        rotation={[-Math.PI / 2, 0, 0]}
      >
        <circleGeometry args={[1.28, 24]} />
        <meshStandardMaterial
          color={debug ? '#ff7a18' : look === 'SYSTEM' ? '#8ec9d4' : '#d4894a'}
          transparent
          opacity={debug ? 0.85 : 0.5}
          roughness={0.06}
          metalness={0.1}
          depthWrite={false}
        />
      </mesh>
      <mesh position={[WATER_CHANNEL.x, WATER_Y + 0.12, basinZ]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[1.05, 20]} />
        <meshBasicMaterial
          map={foam}
          transparent
          opacity={0.7}
          depthWrite={false}
          blending={AdditiveBlending}
        />
      </mesh>
    </group>
  );
}
