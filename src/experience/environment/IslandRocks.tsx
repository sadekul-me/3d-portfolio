import { useTexture } from '@react-three/drei';
import { SRGBColorSpace } from 'three';

const ROCK_ALBEDO = '/assets/world/rocks/rock-basalt-albedo.png';

const ROCKS: Array<{
  position: [number, number, number];
  scale: [number, number, number];
  rotation: [number, number, number];
}> = [
  { position: [-32, -0.8, 18], scale: [7.2, 4.4, 5.1], rotation: [0.2, 0.4, 0.1] },
  { position: [34, -1.0, 16], scale: [6.4, 3.8, 4.6], rotation: [0.15, -0.6, 0.05] },
  { position: [-18, -1.4, 36], scale: [8.8, 5.2, 6.2], rotation: [0.3, 1.1, -0.1] },
  { position: [16, -1.2, 38], scale: [7.6, 4.6, 5.4], rotation: [0.1, -0.8, 0.2] },
  { position: [0, -1.8, 44], scale: [10.4, 3.2, 6.8], rotation: [0.05, 0.2, 0.0] },
  { position: [-38, -0.6, -6], scale: [5.8, 6.4, 4.2], rotation: [0.4, 0.7, 0.15] },
  { position: [40, -0.7, -4], scale: [6.1, 5.8, 4.4], rotation: [0.25, -0.4, 0.1] },
  { position: [-28, -1.1, -28], scale: [6.8, 4.1, 5.5], rotation: [0.18, 1.4, -0.08] },
  { position: [26, -1.0, -30], scale: [6.2, 3.7, 5.0], rotation: [0.22, -1.2, 0.12] },
  { position: [-8, -2.0, 48], scale: [5.4, 2.8, 4.2], rotation: [0.08, 0.5, 0.04] },
  { position: [22, -1.6, 32], scale: [4.2, 2.4, 3.1], rotation: [0.3, -0.3, 0.2] },
  { position: [-24, -1.5, 30], scale: [4.8, 2.6, 3.4], rotation: [0.12, 0.9, -0.1] },
];

export function IslandRocks() {
  const albedo = useTexture(ROCK_ALBEDO);
  albedo.colorSpace = SRGBColorSpace;

  return (
    <group>
      {ROCKS.map((rock, index) => (
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
            color="#6a6e72"
            roughness={0.86}
            metalness={0}
            envMapIntensity={0.7}
          />
        </mesh>
      ))}
    </group>
  );
}
