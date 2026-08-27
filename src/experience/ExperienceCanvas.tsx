import { Canvas } from '@react-three/fiber';

import { useAppStore } from '@/store/appStore';
import { detectDeviceCapabilities } from '@/app/bootstrap/detectCapabilities';
import { resolveQuality } from '@/experience/quality/qualityModel';
import { selectRoomTitle } from '@/content/selectors/contentSelectors';

function ResidenceProbe() {
  const roomId = useAppStore((state) => state.navigation.currentRoomId);
  const locale = useAppStore((state) => state.preferences.locale);
  const title = selectRoomTitle(roomId, locale);

  return (
    <group>
      <ambientLight intensity={0.35} />
      <directionalLight position={[4, 8, 3]} intensity={0.8} />
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1.4, 0.08, 1.4]} />
        <meshStandardMaterial color="#1c222c" metalness={0.35} roughness={0.4} />
      </mesh>
      <mesh position={[0, 0.6, 0]}>
        <sphereGeometry args={[0.18, 24, 24]} />
        <meshStandardMaterial color="#7aa2c4" emissive="#7aa2c4" emissiveIntensity={0.35} />
      </mesh>
      {/* Room title remains in HUD/HTML so it is never canvas-only. */}
      <group userData={{ roomId, title }} />
    </group>
  );
}

export function ExperienceCanvas() {
  const qualityPreset = useAppStore((state) => state.preferences.qualityPreset);
  const capabilities = detectDeviceCapabilities();
  const quality = resolveQuality(qualityPreset, capabilities);

  return (
    <Canvas
      aria-hidden
      dpr={[1, quality.dprCap]}
      gl={{ antialias: quality.tier !== 'LOW', powerPreference: 'high-performance' }}
      camera={{ position: [2.4, 1.6, 2.8], fov: 42 }}
    >
      <color attach="background" args={['#0b0c10']} />
      <ResidenceProbe />
    </Canvas>
  );
}
