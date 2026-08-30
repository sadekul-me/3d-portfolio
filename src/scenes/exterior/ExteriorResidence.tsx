import { useMemo } from 'react';
import { useGLTF, useTexture } from '@react-three/drei';
import { SRGBColorSpace, type Mesh, type MeshStandardMaterial, type Object3D, type Texture } from 'three';

import { EXTERIOR_GLB_URL } from '@/assets/manifests/exteriorManifest';
import { VISUAL_LOOK_PROFILES, type VisualLook } from '@/experience/look/visualLook';

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
      node.name.includes('PROP_Ornamental') ||
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
    const matNames = materials.map((material) => (material as MeshStandardMaterial).name ?? '').join(' ');
    if (matNames.includes('Plant_')) {
      node.visible = false;
      return;
    }
    for (const material of materials) {
      const std = material as MeshStandardMaterial;
      const name = std.name ?? '';
      if (name.includes('Glass')) {
        std.transparent = true;
        std.opacity = Math.max(std.opacity || 0.2, 0.24);
        std.metalness = 0;
        std.roughness = Math.max(std.roughness || 0.04, 0.04);
        std.depthWrite = false;
        std.envMapIntensity = look === 'SYSTEM' ? 1.35 : 1.7;
      }
      if (name.includes('Metal_Bronze')) {
        std.metalness = Math.max(std.metalness, 0.82);
        std.roughness = Math.min(Math.max(std.roughness, 0.24), 0.34);
        std.envMapIntensity = 1.55;
      }
      if (name.includes('Sign_Champagne') || name.includes('Sign_Gold')) {
        std.metalness = Math.max(std.metalness, 0.82);
        std.roughness = Math.min(Math.max(std.roughness, 0.28), 0.38);
        std.envMapIntensity = 1.35;
        std.emissiveIntensity = Math.min(Math.max(std.emissiveIntensity || 0.08, 0.10), look === 'SYSTEM' ? 0.18 : 0.24);
      }
      if (name.includes('Sign_Zone')) {
        std.metalness = Math.max(std.metalness, 0.42);
        std.roughness = Math.min(Math.max(std.roughness, 0.34), 0.44);
        std.envMapIntensity = 1.1;
        std.emissiveIntensity = Math.min(Math.max(std.emissiveIntensity || 0.1, 0.12), 0.22);
      }
      if (name.includes('Sign_Cyan')) {
        std.metalness = Math.min(std.metalness, 0.32);
        std.roughness = Math.max(std.roughness, 0.32);
        std.envMapIntensity = 1.05;
        std.emissiveIntensity = Math.min(Math.max(std.emissiveIntensity || 0.4, 0.55), 0.75);
      }
      if (name.includes('Sign_Backlight')) {
        std.emissiveIntensity = Math.min(Math.max(std.emissiveIntensity || 0.4, 0.7), 1.0);
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
        std.envMapIntensity = 1.2;
        std.roughness = Math.min(Math.max(std.roughness || 0.58, 0.5), 0.72);
        if (name.includes('Rock')) {
          std.color.set(profile.stoneTint);
          std.map = maps.rock;
        }
      }
      if (name.includes('Concrete')) {
        std.metalness = 0;
        std.envMapIntensity = 1.15;
      }
      if (name.includes('Paving')) {
        std.metalness = 0;
        std.envMapIntensity = 1.05;
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
      if (name.includes('Water_Foam')) {
        std.map = maps.foam;
        std.alphaTest = 0.22;
        std.transparent = true;
        std.depthWrite = false;
        std.metalness = 0;
        std.opacity = 0.85;
      }
    }
  });
}

/**
 * Exterior GLB preview only. Full cinematic travel remains a later GSAP phase.
 */
export function ExteriorResidence({ look }: { look: VisualLook }) {
  const gltf = useGLTF(EXTERIOR_GLB_URL);
  const foam = useTexture(FOAM);
  const rock = useTexture(ROCK);
  const maps = useMemo(
    () => ({
      foam: prepAlpha(foam),
      rock: prepAlpha(rock),
    }),
    [foam, rock],
  );
  const scene = useMemo(() => {
    hardenPreviewMaterials(gltf.scene, look, maps);
    return gltf.scene;
  }, [gltf.scene, look, maps]);

  return <primitive object={scene} />;
}

useGLTF.preload(EXTERIOR_GLB_URL);
