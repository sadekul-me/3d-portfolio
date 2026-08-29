import { useMemo } from 'react';
import { useGLTF, useTexture } from '@react-three/drei';
import {
  DoubleSide,
  SRGBColorSpace,
  type Mesh,
  type MeshStandardMaterial,
  type Object3D,
  type Texture,
} from 'three';

import { EXTERIOR_GLB_URL } from '@/assets/manifests/exteriorManifest';
import { VISUAL_LOOK_PROFILES, type VisualLook } from '@/experience/look/visualLook';

const CANOPY_A = '/assets/world/vegetation/foliage-cluster-side-a.png';
const CANOPY_B = '/assets/world/vegetation/foliage-cluster-side-b.png';
const PALM = '/assets/world/vegetation/foliage-cluster-palm.png';
const PALM_FAR = '/assets/world/vegetation/tree-palm-distant.png';
const FOAM = '/assets/world/water/water-foam-shore.png';
const ROCK = '/assets/world/rocks/rock-basalt-albedo.png';

function isMesh(node: Object3D): node is Mesh {
  return (node as Mesh).isMesh === true;
}

function prepAlpha(texture: Texture): Texture {
  texture.colorSpace = SRGBColorSpace;
  texture.needsUpdate = true;
  return texture;
}

function hardenPreviewMaterials(
  root: Object3D,
  look: VisualLook,
  maps: {
    canopyA: Texture;
    canopyB: Texture;
    palm: Texture;
    palmFar: Texture;
    foam: Texture;
    rock: Texture;
  },
): void {
  const profile = VISUAL_LOOK_PROFILES[look];
  root.traverse((node) => {
    if (node.name.startsWith('COL_')) {
      node.visible = false;
    }
    if (
      node.name.includes('Site_Ground') ||
      node.name.includes('PROP_Tree') ||
      node.name.includes('PROP_Palm') ||
      node.name.includes('PROP_Shrub') ||
      node.name.includes('PROP_Hedge') ||
      node.name.includes('Island_Rock') ||
      node.name.includes('Island_Cliff') ||
      node.name.includes('FX_Waterfall') ||
      node.name.includes('FX_Water_Reflecting') ||
      node.name.includes('FX_Shore') ||
      node.name.includes('FX_Water_Foam')
    ) {
      node.visible = false;
    }
    if (!isMesh(node)) {
      return;
    }
    const materials = Array.isArray(node.material) ? node.material : [node.material];
    for (const material of materials) {
      const std = material as MeshStandardMaterial;
      const name = std.name ?? '';
      if (name.includes('Glass')) {
        std.transparent = true;
        std.opacity = profile.glassOpacity;
        std.metalness = 0;
        std.roughness = 0.04;
        std.depthWrite = false;
        std.color.set(profile.glassColor);
        std.envMapIntensity = look === 'SYSTEM' ? 2.1 : 2.5;
      }
      if (name.includes('Metal_Bronze')) {
        std.metalness = Math.max(std.metalness, 0.82);
        std.roughness = Math.min(Math.max(std.roughness, 0.24), 0.34);
        std.envMapIntensity = 1.55;
      }
      if (name.includes('Sign_Champagne') || name.includes('Sign_Gold') || name.includes('Sign_Zone')) {
        std.metalness = Math.max(std.metalness, 0.62);
        std.roughness = Math.min(Math.max(std.roughness, 0.24), 0.34);
        std.envMapIntensity = 1.55;
        std.emissiveIntensity = Math.max(std.emissiveIntensity || 0.4, look === 'SYSTEM' ? 1.15 : 1.45);
      }
      if (name.includes('Sign_Backlight')) {
        std.emissiveIntensity = Math.max(std.emissiveIntensity || 1, 2.8);
      }
      if (name.includes('Metal_Dark')) {
        std.metalness = Math.min(std.metalness, 0.24);
        std.roughness = Math.max(std.roughness, 0.4);
        std.envMapIntensity = 0.8;
      }
      if (name.includes('Metal_Brushed')) {
        std.metalness = Math.min(std.metalness, 0.65);
        std.roughness = Math.max(std.roughness, 0.28);
        std.envMapIntensity = 1.05;
      }
      if (name.includes('Stone') || name.includes('Rock')) {
        std.metalness = 0;
        std.color.set(profile.stoneTint);
        std.envMapIntensity = 1.35;
        std.roughness = Math.min(Math.max(std.roughness || 0.6, 0.52), 0.78);
        if (name.includes('Rock')) {
          std.map = maps.rock;
        }
      }
      if (name.includes('Concrete')) {
        std.metalness = 0;
        std.color.set(look === 'SYSTEM' ? '#686c72' : '#5e6268');
        std.envMapIntensity = 1.22;
      }
      if (name.includes('Paving')) {
        std.metalness = 0;
        std.color.set('#6e7074');
        std.envMapIntensity = 1.15;
      }
      if (name.includes('LED_Cool')) {
        std.emissiveIntensity = Math.max(std.emissiveIntensity || 1, look === 'SYSTEM' ? 4.4 : 2.2);
      }
      if (name.includes('LED') && !name.includes('LED_Cool')) {
        std.emissiveIntensity = Math.max(std.emissiveIntensity || 1, look === 'SYSTEM' ? 3.8 : 5.2);
      }
      if (name.includes('Interior_Warm')) {
        std.emissiveIntensity = Math.max(std.emissiveIntensity || 1, profile.interiorBoost);
      }
      if (name.includes('Plant_Palm_Distant')) {
        std.map = maps.palmFar;
        std.alphaTest = 0.48;
        std.transparent = false;
        std.metalness = 0;
        std.roughness = 0.74;
        std.color.set(profile.plantTint);
        std.side = DoubleSide;
      } else if (name.includes('Plant_Palm')) {
        std.map = maps.palm;
        std.alphaTest = 0.46;
        std.transparent = false;
        std.metalness = 0;
        std.roughness = 0.76;
        std.color.set(profile.plantTint);
        std.side = DoubleSide;
      } else if (name.includes('Water_Foam')) {
        std.map = maps.foam;
        std.alphaTest = 0.22;
        std.transparent = true;
        std.depthWrite = false;
        std.metalness = 0;
        std.opacity = 0.85;
      } else if (
        name.includes('Plant_Canopy') ||
        name.includes('Plant_Hedge') ||
        name.includes('Plant_Grass') ||
        name.includes('Plant_Foliage')
      ) {
        std.map = name.includes('Canopy_B') ? maps.canopyB : maps.canopyA;
        std.alphaTest = 0.46;
        std.transparent = false;
        std.metalness = 0;
        std.roughness = 0.78;
        std.color.set(profile.plantTint);
        std.side = DoubleSide;
      }
    }
  });
}

/**
 * Exterior GLB preview only. Full cinematic travel remains a later GSAP phase.
 */
export function ExteriorResidence({ look }: { look: VisualLook }) {
  const gltf = useGLTF(EXTERIOR_GLB_URL);
  const canopyA = useTexture(CANOPY_A);
  const canopyB = useTexture(CANOPY_B);
  const palm = useTexture(PALM);
  const palmFar = useTexture(PALM_FAR);
  const foam = useTexture(FOAM);
  const rock = useTexture(ROCK);
  const maps = useMemo(
    () => ({
      canopyA: prepAlpha(canopyA),
      canopyB: prepAlpha(canopyB),
      palm: prepAlpha(palm),
      palmFar: prepAlpha(palmFar),
      foam: prepAlpha(foam),
      rock: prepAlpha(rock),
    }),
    [canopyA, canopyB, palm, palmFar, foam, rock],
  );
  const scene = useMemo(() => {
    hardenPreviewMaterials(gltf.scene, look, maps);
    return gltf.scene;
  }, [gltf.scene, look, maps]);

  return <primitive object={scene} />;
}

useGLTF.preload(EXTERIOR_GLB_URL);
