import { useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { useTexture } from '@react-three/drei';
import { AdditiveBlending, DoubleSide, RepeatWrapping, ShaderMaterial, Vector3 } from 'three';

import type { VisualLook } from '@/experience/look/visualLook';
import { WATER_Y } from '@/experience/environment/islandHeight';

const FOAM_URL = '/assets/world/water/water-foam-shore.png';

const VERTEX = `
uniform float uTime;
varying vec2 vUv;
varying vec3 vWorld;
void main() {
  vUv = uv;
  vec3 pos = position;
  pos.x += 0.04 * sin(uv.y * 28.0 + uTime * 3.2);
  pos.z += 0.03 * sin(uv.y * 18.0 - uTime * 2.4);
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
  { position: [-11.6, 1.55, 8.55], rotation: [0.18, 0.04, 0], size: [5.8, 3.2] },
  { position: [-11.55, 0.15, 10.7], rotation: [0.55, 0.05, 0], size: [5.2, 3.0] },
  { position: [-11.5, -0.85, 13.4], rotation: [0.92, 0.04, 0], size: [4.6, 2.6] },
  { position: [-11.45, -1.35, 15.6], rotation: [1.12, 0.03, 0], size: [4.0, 1.8] },
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

  return (
    <group>
      <mesh position={[-11.6, 0.55, 9.15]}>
        <boxGeometry args={[6.6, 2.4, 0.42]} />
        <meshStandardMaterial color="#3a3e42" roughness={0.7} metalness={0.05} />
      </mesh>
      <mesh position={[-11.55, -0.55, 12.4]} rotation={[0.35, 0, 0]}>
        <boxGeometry args={[5.4, 0.28, 5.6]} />
        <meshStandardMaterial color="#2f3438" roughness={0.58} metalness={0.04} />
      </mesh>
      {SHEETS.map((sheet, index) => (
        <mesh key={index} position={sheet.position} rotation={sheet.rotation} material={material}>
          <planeGeometry args={[sheet.size[0], sheet.size[1], 8, 28]} />
        </mesh>
      ))}
      <mesh position={[-11.4, WATER_Y + 0.08, 16.8]} rotation={[-Math.PI / 2, 0, 0.06]}>
        <circleGeometry args={[2.6, 28]} />
        <meshStandardMaterial
          color={look === 'SYSTEM' ? '#8ec9d4' : '#d4894a'}
          transparent
          opacity={0.5}
          roughness={0.06}
          metalness={0.1}
          depthWrite={false}
        />
      </mesh>
      <mesh position={[-11.4, WATER_Y + 0.16, 16.6]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[2.05, 24]} />
        <meshBasicMaterial
          map={foam}
          transparent
          opacity={0.7}
          depthWrite={false}
          blending={AdditiveBlending}
        />
      </mesh>
      <mesh position={[-11.45, -0.35, 15.2]}>
        <planeGeometry args={[3.4, 1.6]} />
        <meshBasicMaterial
          map={foam}
          transparent
          opacity={0.45}
          depthWrite={false}
          blending={AdditiveBlending}
        />
      </mesh>
    </group>
  );
}
