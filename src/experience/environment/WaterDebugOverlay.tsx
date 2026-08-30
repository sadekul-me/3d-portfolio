import { DoubleSide } from 'three';

import { WATER_CHANNEL } from '@/experience/environment/waterContainment';

function debugEnabled(): boolean {
  return typeof window !== 'undefined' && new URLSearchParams(window.location.search).has('debugWater');
}

/**
 * Temporary exclusion visualisation. Off unless ?debugWater=1.
 * OCEAN = blue (IslandOcean uDebug). WATERFALL channel = orange.
 * Do not draw circular proxies through the building — they are not the ocean mesh.
 */
export function WaterDebugOverlay() {
  if (!debugEnabled()) {
    return null;
  }

  const z = (WATER_CHANNEL.zStart + WATER_CHANNEL.zEnd) * 0.5;
  const depth = WATER_CHANNEL.zEnd - WATER_CHANNEL.zStart;

  return (
    <group name="WATER_DEBUG">
      <mesh position={[WATER_CHANNEL.x, 2.6, z]}>
        <boxGeometry args={[WATER_CHANNEL.width, 5.4, depth]} />
        <meshBasicMaterial color="#ff7a18" transparent opacity={0.28} depthWrite={false} side={DoubleSide} />
      </mesh>
    </group>
  );
}
