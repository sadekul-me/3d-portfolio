import { useMemo } from 'react';
import { useTexture } from '@react-three/drei';
import { DoubleSide, RepeatWrapping, SRGBColorSpace, type Texture } from 'three';

const BARK = '/assets/world/vegetation/bark-albedo.jpg';
const BARK_N = '/assets/world/vegetation/bark-normal.jpg';
const BARK_R = '/assets/world/vegetation/bark-rough.jpg';
const LEAF_A = '/assets/world/vegetation/foliage-hero-a.png';
const LEAF_B = '/assets/world/vegetation/foliage-hero-b.png';
const PALM = '/assets/world/vegetation/foliage-palm-frond.png';
const SHRUB = '/assets/world/vegetation/foliage-shrub.png';

type Family = 'broadleaf' | 'palm' | 'ornamental';

type TreeSpec = {
  position: [number, number, number];
  scale: number;
  yaw: number;
  family: Family;
  seed: number;
};

const TREES: TreeSpec[] = [
  { position: [-7.6, 0, 13.4], scale: 1.08, yaw: 0.3, family: 'broadleaf', seed: 11 },
  { position: [7.2, 0, 12.6], scale: 1.12, yaw: 1.1, family: 'broadleaf', seed: 23 },
  { position: [-11.4, 0, 9.2], scale: 0.94, yaw: 2.2, family: 'ornamental', seed: 37 },
  { position: [10.8, 0, 8.6], scale: 0.9, yaw: 4.0, family: 'ornamental', seed: 41 },
  { position: [-16.8, 0, 12.8], scale: 1.08, yaw: 0.7, family: 'palm', seed: 53 },
  { position: [16.2, 0, 13.2], scale: 1.04, yaw: 5.1, family: 'palm', seed: 67 },
  { position: [-5.4, 0, 16.8], scale: 0.82, yaw: 1.8, family: 'ornamental', seed: 71 },
  { position: [5.8, 0, 17.2], scale: 0.78, yaw: 3.4, family: 'ornamental', seed: 83 },
];

function rng(seed: number) {
  let a = seed + 1;
  return () => {
    a = (a * 16807) % 2147483647;
    return (a - 1) / 2147483646;
  };
}

function prep(texture: Texture, repeat = 1): Texture {
  texture.colorSpace = SRGBColorSpace;
  if (repeat !== 1) {
    texture.wrapS = texture.wrapT = RepeatWrapping;
    texture.repeat.set(repeat, repeat);
  }
  texture.needsUpdate = true;
  return texture;
}

function Trunk({
  height,
  radius,
  bark,
  barkN,
  barkR,
}: {
  height: number;
  radius: number;
  bark: Texture;
  barkN: Texture;
  barkR: Texture;
}) {
  return (
    <group>
      <mesh position={[0, height * 0.38, 0]} castShadow>
        <cylinderGeometry args={[radius * 0.42, radius, height * 0.76, 8]} />
        <meshStandardMaterial
          map={bark}
          normalMap={barkN}
          roughnessMap={barkR}
          roughness={0.92}
          metalness={0}
        />
      </mesh>
      <mesh position={[0.12, height * 0.72, -0.08]} rotation={[0.45, 0.4, 0.15]} castShadow>
        <cylinderGeometry args={[radius * 0.16, radius * 0.28, height * 0.42, 6]} />
        <meshStandardMaterial map={bark} roughness={0.9} metalness={0} />
      </mesh>
      <mesh position={[-0.16, height * 0.68, 0.1]} rotation={[0.5, -0.7, -0.2]} castShadow>
        <cylinderGeometry args={[radius * 0.14, radius * 0.24, height * 0.36, 6]} />
        <meshStandardMaterial map={bark} roughness={0.9} metalness={0} />
      </mesh>
      <mesh position={[0.04, 0.06, 0.04]}>
        <cylinderGeometry args={[radius * 1.45, radius * 1.7, 0.14, 8]} />
        <meshStandardMaterial color="#2a241c" roughness={1} metalness={0} />
      </mesh>
    </group>
  );
}

function FoliageCards({
  count,
  radius,
  lift,
  map,
  seed,
  size,
}: {
  count: number;
  radius: number;
  lift: number;
  map: Texture;
  seed: number;
  size: [number, number];
}) {
  const cards = useMemo(() => {
    const rand = rng(seed);
    return Array.from({ length: count }, (_, i) => {
      const yaw = (i / count) * Math.PI * 2 + rand() * 0.45;
      const pitch = 0.95 + rand() * 0.55;
      const r = radius * (0.35 + rand() * 0.7);
      return {
        position: [Math.cos(yaw) * r, lift + rand() * 0.85, Math.sin(yaw) * r] as [
          number,
          number,
          number,
        ],
        rotation: [pitch, yaw + rand() * 0.4, (rand() - 0.5) * 0.35] as [number, number, number],
        scale: 0.78 + rand() * 0.45,
      };
    });
  }, [count, radius, lift, seed]);

  return (
    <group>
      {cards.map((card, index) => (
        <mesh
          key={index}
          position={card.position}
          rotation={card.rotation}
          scale={card.scale}
          castShadow
        >
          <planeGeometry args={size} />
          <meshStandardMaterial
            map={map}
            alphaTest={0.52}
            transparent={false}
            side={DoubleSide}
            roughness={0.78}
            metalness={0}
            depthWrite
          />
        </mesh>
      ))}
    </group>
  );
}

export function HybridVegetation() {
  const bark = prep(useTexture(BARK), 2.4);
  const barkN = prep(useTexture(BARK_N), 2.4);
  const barkR = prep(useTexture(BARK_R), 2.4);
  const leafA = prep(useTexture(LEAF_A));
  const leafB = prep(useTexture(LEAF_B));
  const palm = prep(useTexture(PALM));
  const shrub = prep(useTexture(SHRUB));

  return (
    <group>
      {TREES.map((tree) => (
        <group
          key={tree.seed}
          position={tree.position}
          rotation={[0, tree.yaw, 0]}
          scale={tree.scale}
        >
          {tree.family === 'palm' ? (
            <>
              <Trunk height={6.4} radius={0.16} bark={bark} barkN={barkN} barkR={barkR} />
              <FoliageCards
                count={7}
                radius={1.15}
                lift={5.1}
                map={palm}
                seed={tree.seed}
                size={[2.3, 2.7]}
              />
            </>
          ) : tree.family === 'ornamental' ? (
            <>
              <Trunk height={3.4} radius={0.1} bark={bark} barkN={barkN} barkR={barkR} />
              <FoliageCards
                count={8}
                radius={1.05}
                lift={2.5}
                map={shrub}
                seed={tree.seed}
                size={[1.35, 1.45]}
              />
            </>
          ) : (
            <>
              <Trunk height={5.6} radius={0.2} bark={bark} barkN={barkN} barkR={barkR} />
              <FoliageCards
                count={12}
                radius={1.55}
                lift={3.7}
                map={tree.seed % 2 === 0 ? leafA : leafB}
                seed={tree.seed}
                size={[1.7, 1.95]}
              />
            </>
          )}
        </group>
      ))}
      {[
        [-3.6, 0.15, 11.4],
        [3.8, 0.15, 11.6],
        [-9.2, 0.12, 14.8],
        [9.0, 0.12, 15.0],
      ].map((pos, i) => (
        <mesh
          key={`shrub-${i}`}
          position={pos as [number, number, number]}
          rotation={[0, i * 0.7, 0]}
        >
          <planeGeometry args={[1.4, 1.15]} />
          <meshStandardMaterial
            map={shrub}
            alphaTest={0.4}
            side={DoubleSide}
            roughness={0.8}
            metalness={0}
          />
        </mesh>
      ))}
    </group>
  );
}
