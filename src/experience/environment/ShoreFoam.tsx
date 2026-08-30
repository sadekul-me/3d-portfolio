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

import { expandedShoreline, isOceanForbidden } from '@/experience/environment/waterContainment';
import { WATER_Y } from '@/experience/environment/islandHeight';

const FOAM_URL = '/assets/world/water/water-foam-shore.png';

function buildShoreRibbon(width = 2.2) {
  const samples = expandedShoreline(120).filter((sample) => !isOceanForbidden(sample.x, sample.z));
  const geo = new BufferGeometry();
  if (samples.length < 8) {
    geo.setAttribute('position', new BufferAttribute(new Float32Array(9), 3));
    return geo;
  }
  const positions: number[] = [];
  const uvs: number[] = [];
  const indices: number[] = [];
  for (let i = 0; i < samples.length; i += 1) {
    const a = samples[i];
    const b = samples[(i + 1) % samples.length];
    if (!a || !b) {
      continue;
    }
    const span = Math.hypot(a.x + 3.2, a.z - 6.8) || 1;
    const ox = (a.x + 3.2) / span;
    const oz = (a.z - 6.8) / span;
    const inner = i * 2;
    positions.push(a.x, WATER_Y + 0.03, a.z);
    positions.push(a.x + ox * width, WATER_Y + 0.025, a.z + oz * width);
    uvs.push(i / 18, 0, i / 18, 1);
    const next = ((i + 1) % samples.length) * 2;
    indices.push(inner, inner + 1, next + 1, inner, next + 1, next);
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
    <mesh geometry={geometry} frustumCulled={false} name="WATER_SHORE_FOAM">
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
