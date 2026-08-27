import { useMemo } from 'react';
import { useGLTF } from '@react-three/drei';
import type { Object3D } from 'three';

import { EXTERIOR_GLB_URL } from '@/assets/manifests/exteriorManifest';

function hideCollisionProxies(root: Object3D): void {
  root.traverse((node) => {
    if (node.name.startsWith('COL_')) {
      node.visible = false;
    }
  });
}

/**
 * Exterior GLB preview only. Full cinematic travel remains a later GSAP phase.
 */
export function ExteriorResidence() {
  const gltf = useGLTF(EXTERIOR_GLB_URL);
  const scene = useMemo(() => {
    hideCollisionProxies(gltf.scene);
    return gltf.scene;
  }, [gltf.scene]);

  return <primitive object={scene} />;
}

useGLTF.preload(EXTERIOR_GLB_URL);
