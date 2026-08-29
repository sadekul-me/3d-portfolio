import { useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { useTexture } from '@react-three/drei';
import {
  AdditiveBlending,
  BufferAttribute,
  BufferGeometry,
  DoubleSide,
  RepeatWrapping,
} from 'three';

import { sampleShoreline, WATER_Y } from '@/experience/environment/islandHeight';

const FOAM_URL = '/assets/world/water/water-foam-shore.png';

function buildShoreRibbon(width = 2.8) {
  const samples = sampleShoreline(120);
  const geo = new BufferGeometry();
  const positions: number[] = [];
  const uvs: number[] = [];
  const indices: number[] = [];
  for (let i = 0; i < samples.length; i += 1) {
    const a = samples[i];
    const b = samples[(i + 1) % samples.length];
    if (!a || !b) {
      continue;
    }
    const dx = b.x - a.x;
    const dz = b.z - a.z;
    const len = Math.hypot(dx, dz) || 1;
    const nx = -dz / len;
    const nz = dx / len;
    const inner = i * 2;
    positions.push(a.x - nx * 0.2, WATER_Y + 0.03, a.z - nz * 0.2);
    positions.push(a.x + nx * width, WATER_Y + 0.025, a.z + nz * width);
    uvs.push(i / 18, 0, i / 18, 1);
    if (i < samples.length) {
      const next = ((i + 1) % samples.length) * 2;
      indices.push(inner, inner + 1, next + 1, inner, next + 1, next);
    }
  }
  geo.setAttribute('position', new BufferAttribute(new Float32Array(positions), 3));
  geo.setAttribute('uv', new BufferAttribute(new Float32Array(uvs), 2));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  return geo;
}

export function ShoreFoam() {
  const texture = useTexture(FOAM_URL);
  const geometry = useMemo(() => buildShoreRibbon(), []);
  useMemo(() => {
    texture.wrapS = RepeatWrapping;
    texture.wrapT = RepeatWrapping;
    texture.repeat.set(8, 1);
    return texture;
  }, [texture]);

  useFrame((_, delta) => {
    texture.offset.x += delta * 0.05;
  });

  return (
    <mesh geometry={geometry} frustumCulled={false}>
      <meshBasicMaterial
        map={texture}
        transparent
        opacity={0.62}
        depthWrite={false}
        side={DoubleSide}
        blending={AdditiveBlending}
      />
    </mesh>
  );
}
