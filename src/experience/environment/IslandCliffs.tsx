import { useTexture } from '@react-three/drei';
import { RepeatWrapping, SRGBColorSpace } from 'three';

const ALBEDO = '/assets/world/rocks/rock-stratum-albedo.jpg';
const NORMAL = '/assets/world/rocks/rock-stratum-normal.jpg';
const ROUGH = '/assets/world/rocks/rock-stratum-rough.jpg';

type Slab = {
  position: [number, number, number];
  scale: [number, number, number];
  rotation: [number, number, number];
  wet?: boolean;
};

const SLABS: Slab[] = [
  { position: [0, -2.35, 17.4], scale: [20.0, 3.6, 7.2], rotation: [0.06, 0.04, 0.0] },
  { position: [-11.5, -1.85, 15.2], scale: [9.4, 4.8, 5.6], rotation: [0.08, 0.35, 0.05] },
  { position: [11.8, -1.9, 15.6], scale: [9.0, 4.6, 5.4], rotation: [0.07, -0.32, -0.04] },
  { position: [-18.5, -1.4, 10.2], scale: [7.2, 5.4, 6.8], rotation: [0.04, 0.7, 0.06] },
  { position: [18.8, -1.5, 10.6], scale: [7.0, 5.2, 6.4], rotation: [0.05, -0.62, -0.05] },
  { position: [-16.2, -2.5, 18.8], scale: [6.2, 2.8, 4.4], rotation: [0.12, 0.5, 0.08], wet: true },
  {
    position: [15.6, -2.55, 19.2],
    scale: [5.8, 2.6, 4.2],
    rotation: [0.14, -0.4, -0.06],
    wet: true,
  },
  { position: [0.0, -2.85, 21.6], scale: [12.4, 2.2, 4.8], rotation: [0.16, 0.02, 0.0], wet: true },
  { position: [-8.4, -3.05, 22.4], scale: [5.2, 1.8, 3.4], rotation: [0.2, 0.25, 0.05], wet: true },
  {
    position: [8.2, -3.1, 22.6],
    scale: [5.0, 1.7, 3.2],
    rotation: [0.18, -0.22, -0.04],
    wet: true,
  },
  { position: [-22.4, -1.2, 2.4], scale: [6.6, 6.2, 5.8], rotation: [0.03, 1.15, 0.04] },
  { position: [22.8, -1.15, 2.8], scale: [6.4, 6.0, 5.6], rotation: [0.03, -1.05, -0.03] },
  { position: [-20.6, -1.7, -8.4], scale: [5.8, 4.8, 6.2], rotation: [0.05, 2.4, 0.05] },
  { position: [20.4, -1.65, -8.0], scale: [5.6, 4.6, 6.0], rotation: [0.04, -2.3, -0.04] },
  { position: [0.0, -1.35, -14.5], scale: [16.0, 4.2, 5.0], rotation: [0.02, 3.12, 0.0] },
  { position: [-6.2, 0.15, 12.6], scale: [3.4, 1.15, 2.6], rotation: [0.0, 0.2, 0.0] },
  { position: [6.4, 0.12, 12.8], scale: [3.2, 1.05, 2.4], rotation: [0.0, -0.18, 0.0] },
];

export function IslandCliffs() {
  const albedo = useTexture(ALBEDO);
  const normal = useTexture(NORMAL);
  const rough = useTexture(ROUGH);
  albedo.colorSpace = SRGBColorSpace;
  albedo.wrapS = albedo.wrapT = RepeatWrapping;
  normal.wrapS = normal.wrapT = RepeatWrapping;
  rough.wrapS = rough.wrapT = RepeatWrapping;
  albedo.repeat.set(2.2, 1.6);
  normal.repeat.set(2.2, 1.6);
  rough.repeat.set(2.2, 1.6);

  return (
    <group>
      {SLABS.map((slab, index) => (
        <mesh
          key={index}
          position={slab.position}
          rotation={slab.rotation}
          scale={slab.scale}
          receiveShadow
        >
          <boxGeometry args={[1, 1, 1, 2, 2, 2]} />
          <meshStandardMaterial
            map={albedo}
            normalMap={normal}
            roughnessMap={rough}
            color={slab.wet ? '#2a3034' : '#4a4e52'}
            roughness={slab.wet ? 0.42 : 0.88}
            metalness={0}
            envMapIntensity={slab.wet ? 1.15 : 0.55}
          />
        </mesh>
      ))}
    </group>
  );
}
