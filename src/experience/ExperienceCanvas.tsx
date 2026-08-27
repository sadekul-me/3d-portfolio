import { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { ContactShadows, OrbitControls } from '@react-three/drei';

import { useAppStore } from '@/store/appStore';
import { detectDeviceCapabilities } from '@/app/bootstrap/detectCapabilities';
import { resolveQuality } from '@/experience/quality/qualityModel';
import { ExteriorResidence } from '@/scenes/exterior/ExteriorResidence';

export function ExperienceCanvas() {
  const qualityPreset = useAppStore((state) => state.preferences.qualityPreset);
  const capabilities = detectDeviceCapabilities();
  const quality = resolveQuality(qualityPreset, capabilities);

  return (
    <Canvas
      aria-hidden
      dpr={[1, quality.dprCap]}
      gl={{ antialias: quality.tier !== 'LOW', powerPreference: 'high-performance' }}
      camera={{ position: [1.8, 12.4, 62], fov: 32, near: 0.1, far: 280 }}
    >
      <color attach="background" args={['#07080c']} />
      <hemisphereLight color="#8aa0b8" groundColor="#0b0c10" intensity={0.32} />
      <ambientLight intensity={0.12} />
      <directionalLight position={[-22, 28, 18]} intensity={0.7} color="#9bb4c8" />
      <directionalLight position={[16, 12, 8]} intensity={0.28} color="#f0c49a" />
      <Suspense fallback={null}>
        <ExteriorResidence />
      </Suspense>
      <ContactShadows position={[0, 0.02, 0]} opacity={0.45} scale={90} blur={2.4} far={20} />
      <OrbitControls
        enablePan={false}
        target={[1.2, 5.2, -3.5]}
        minDistance={16}
        maxDistance={90}
        maxPolarAngle={Math.PI / 2.08}
        enableDamping
      />
    </Canvas>
  );
}
