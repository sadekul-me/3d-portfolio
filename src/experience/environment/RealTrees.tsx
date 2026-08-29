import { useMemo } from 'react';
import { Clone, useGLTF } from '@react-three/drei';
import { DoubleSide, type Mesh, type MeshStandardMaterial, type Object3D } from 'three';

import { HERO_TREE_SITES, heightAt } from '@/experience/environment/islandHeight';

const LOD0 = '/assets/world/vegetation/tree-jacaranda-lod0.glb?v=271573';
const LOD1 = '/assets/world/vegetation/tree-jacaranda-lod1.glb?v=133147';
const LOD2 = '/assets/world/vegetation/tree-jacaranda-lod2.glb?v=66471';

function hardenTree(root: Object3D) {
  root.traverse((node) => {
    if (!(node as Mesh).isMesh) {
      return;
    }
    const mesh = node as Mesh;
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    for (const material of materials) {
      const std = material as MeshStandardMaterial;
      const name = (std.name ?? node.name).toLowerCase();
      std.metalness = 0;
      std.envMapIntensity = name.includes('leaf') ? 0.55 : 0.35;
      std.roughness = name.includes('leaf') ? 0.62 : 0.88;
      if (name.includes('leaf') || std.alphaMap || (std.map && std.transparent)) {
        std.transparent = false;
        std.alphaTest = 0.42;
        std.depthWrite = true;
        std.side = DoubleSide;
      }
    }
  });
}

export function RealTrees() {
  const lod0 = useGLTF(LOD0);
  const lod1 = useGLTF(LOD1);
  const lod2 = useGLTF(LOD2);
  const scenes = useMemo(() => {
    hardenTree(lod0.scene);
    hardenTree(lod1.scene);
    hardenTree(lod2.scene);
    return {
      0: lod0.scene,
      1: lod1.scene,
      2: lod2.scene,
    };
  }, [lod0.scene, lod1.scene, lod2.scene]);

  return (
    <group>
      {HERO_TREE_SITES.map((plant, index) => {
        const grounded: [number, number, number] = [
          plant.position[0],
          heightAt(plant.position[0], plant.position[2]) - 0.04,
          plant.position[2],
        ];
        return (
          <group key={index} position={grounded} rotation={[0, plant.yaw, 0]} scale={plant.scale}>
            <Clone object={scenes[plant.lod]} deep />
          </group>
        );
      })}
    </group>
  );
}

useGLTF.preload(LOD0);
useGLTF.preload(LOD1);
useGLTF.preload(LOD2);
