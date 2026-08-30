import { useLayoutEffect, useMemo, useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { PerspectiveCamera, Vector3 } from 'three';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';

import {
  resolveSessionCamera,
} from '@/experience/camera/exteriorCameras';

export function ExteriorHeroCamera() {
  const size = useThree((state) => state.size);
  const camera = useThree((state) => state.camera);
  const search = typeof window !== 'undefined' ? window.location.search : '';
  const topDown = search.includes('cam=waterTop');
  const framed = useMemo(
    () => resolveSessionCamera(size.width, size.height),
    [size.width, size.height, search],
  );
  const lookTarget = useMemo(
    () => new Vector3(...framed.target),
    [framed.target],
  );
  const controlsRef = useRef<OrbitControlsImpl>(null);
  const poseGeneration = useRef(0);
  const appliedGeneration = useRef(-1);

  const applyPose = () => {
    if (!(camera instanceof PerspectiveCamera)) {
      return false;
    }
    camera.position.set(...framed.position);
    camera.fov = framed.vfovDeg;
    camera.near = 0.15;
    camera.far = 420;
    camera.updateProjectionMatrix();
    camera.lookAt(lookTarget);
    const controls = controlsRef.current;
    if (!controls) {
      return false;
    }
    controls.target.copy(lookTarget);
    controls.minDistance = framed.minDistance;
    controls.maxDistance = framed.maxDistance;
    controls.update();
    return true;
  };

  useLayoutEffect(() => {
    poseGeneration.current += 1;
    applyPose();
  }, [camera, framed, lookTarget]);

  useFrame(() => {
    if (appliedGeneration.current === poseGeneration.current) {
      return;
    }
    if (applyPose()) {
      appliedGeneration.current = poseGeneration.current;
    }
  });

  return (
    <OrbitControls
      ref={controlsRef}
      makeDefault
      enablePan={false}
      target={lookTarget}
      minDistance={framed.minDistance}
      maxDistance={framed.maxDistance}
      maxPolarAngle={topDown ? Math.PI : Math.PI / 2.08}
      minPolarAngle={topDown ? 0 : 0}
      enableDamping
    />
  );
}
