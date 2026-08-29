import { useMemo } from 'react';
import { useTexture } from '@react-three/drei';
import {
  BufferAttribute,
  Color,
  PlaneGeometry,
  RepeatWrapping,
  SRGBColorSpace,
  type Texture,
} from 'three';

import { heightAt, terrainColor, WATER_Y } from '@/experience/environment/islandHeight';

const ALBEDO = '/assets/world/rocks/rock-stratum-albedo.jpg';
const NORMAL = '/assets/world/rocks/rock-stratum-normal.jpg';
const ROUGH = '/assets/world/rocks/rock-stratum-rough.jpg';

function buildIslandGeometry() {
  const geo = new PlaneGeometry(72, 64, 160, 140);
  geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position;
  if (!(pos instanceof BufferAttribute)) {
    return geo;
  }
  const colors = new Float32Array(pos.count * 3);
  for (let i = 0; i < pos.count; i += 1) {
    const x = pos.getX(i);
    const z = pos.getZ(i);
    const y = heightAt(x, z);
    pos.setY(i, y);
    const [r, g, b] = terrainColor(x, z, y);
    colors[i * 3] = r;
    colors[i * 3 + 1] = g;
    colors[i * 3 + 2] = b;
  }
  pos.needsUpdate = true;
  geo.setAttribute('color', new BufferAttribute(colors, 3));
  geo.computeVertexNormals();
  return geo;
}

const RETAINING: Array<{
  position: [number, number, number];
  size: [number, number, number];
  yaw: number;
}> = [
  { position: [-11.2, -0.28, 8.9], size: [9.4, 0.95, 0.38], yaw: 0.08 },
  { position: [9.6, -0.22, 8.7], size: [8.8, 0.88, 0.36], yaw: -0.06 },
  { position: [-16.4, -0.72, 12.6], size: [7.2, 1.15, 0.42], yaw: 0.22 },
  { position: [14.8, -0.68, 12.8], size: [6.8, 1.05, 0.4], yaw: -0.18 },
  { position: [0.0, -0.18, 9.6], size: [8.2, 0.28, 6.4], yaw: 0 },
  { position: [-11.6, 0.15, 9.4], size: [6.6, 1.85, 0.55], yaw: 0.05 },
];

function hash(i: number) {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

function ShoreRocks({ albedo }: { albedo: Texture }) {
  const rocks = useMemo(() => {
    const list: Array<{
      position: [number, number, number];
      rotation: [number, number, number];
      scale: [number, number, number];
      wet: boolean;
    }> = [];
    for (let i = 0; i < 56; i += 1) {
      const theta = (i / 56) * Math.PI * 1.35 - 0.22;
      const radius = 20.4 + hash(i) * 5.8;
      const x = Math.cos(theta) * radius * 0.92 - 2.4;
      const z = 14.5 + Math.sin(theta) * 8.4 + hash(i + 9) * 3.2;
      const y = Math.min(heightAt(x, z), WATER_Y + 0.38) - 0.12 * hash(i + 3);
      const s = 0.28 + hash(i + 17) * 0.85;
      list.push({
        position: [x, y, z],
        rotation: [hash(i + 4) * 0.8, hash(i + 6) * 2.4, hash(i + 8) * 0.6],
        scale: [s * (0.7 + hash(i) * 0.6), s * (0.42 + hash(i + 2) * 0.4), s],
        wet: y < WATER_Y + 0.14,
      });
    }
    return list;
  }, []);

  return (
    <group>
      {rocks.map((rock, index) => (
        <mesh
          key={index}
          position={rock.position}
          rotation={rock.rotation}
          scale={rock.scale}
          castShadow
          receiveShadow
        >
          <icosahedronGeometry args={[1, 1]} />
          <meshStandardMaterial
            map={albedo}
            color={rock.wet ? '#2a3236' : '#5a5e62'}
            roughness={rock.wet ? 0.26 : 0.84}
            metalness={0}
            envMapIntensity={rock.wet ? 1.35 : 0.55}
          />
        </mesh>
      ))}
    </group>
  );
}

export function IslandTerrain() {
  const albedo = useTexture(ALBEDO);
  const normal = useTexture(NORMAL);
  const rough = useTexture(ROUGH);
  albedo.colorSpace = SRGBColorSpace;
  albedo.wrapS = albedo.wrapT = RepeatWrapping;
  normal.wrapS = normal.wrapT = RepeatWrapping;
  rough.wrapS = rough.wrapT = RepeatWrapping;
  albedo.repeat.set(4.2, 3.6);
  normal.repeat.set(4.2, 3.6);
  rough.repeat.set(4.2, 3.6);

  const geometry = useMemo(() => buildIslandGeometry(), []);

  return (
    <group>
      <mesh geometry={geometry} receiveShadow>
        <meshStandardMaterial
          map={albedo}
          normalMap={normal}
          roughnessMap={rough}
          vertexColors
          color={new Color('#9a9ea4')}
          roughness={0.86}
          metalness={0}
          envMapIntensity={0.58}
        />
      </mesh>
      {RETAINING.map((wall, index) => (
        <mesh key={index} position={wall.position} rotation={[0, wall.yaw, 0]}>
          <boxGeometry args={wall.size} />
          <meshStandardMaterial color="#3a3e42" roughness={0.62} metalness={0.04} />
        </mesh>
      ))}
      <ShoreRocks albedo={albedo} />
    </group>
  );
}
