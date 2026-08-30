import { Suspense, useLayoutEffect, useMemo } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { ContactShadows } from '@react-three/drei';
import {
  ACESFilmicToneMapping,
  BackSide,
  Color,
  HemisphereLight,
  Mesh,
  MeshBasicMaterial,
  PMREMGenerator,
  Scene,
  ShaderMaterial,
  SphereGeometry,
  Vector3,
} from 'three';

import { useAppStore } from '@/store/appStore';
import { detectDeviceCapabilities } from '@/app/bootstrap/detectCapabilities';
import { resolveQuality } from '@/experience/quality/qualityModel';
import { ExteriorResidence } from '@/scenes/exterior/ExteriorResidence';
import { IslandOcean } from '@/experience/environment/IslandOcean';
import { IslandTerrain } from '@/experience/environment/IslandTerrain';
import { ShoreFoam } from '@/experience/environment/ShoreFoam';
import { RealTrees } from '@/experience/environment/RealTrees';
import { WaterFeature } from '@/experience/environment/WaterFeature';
import { WaterDebugOverlay } from '@/experience/environment/WaterDebugOverlay';
import { useVisualLook } from '@/experience/look/VisualLookContext';
import { VISUAL_LOOK_PROFILES, type VisualLookProfile } from '@/experience/look/visualLook';
import { CAM_HERO_EXTERIOR_16X9 } from '@/experience/camera/exteriorCameras';
import { ExteriorHeroCamera } from '@/experience/camera/ExteriorHeroCamera';

function ApplyExposure({ exposure }: { exposure: number }) {
  const gl = useThree((state) => state.gl);
  useLayoutEffect(() => {
    gl.toneMappingExposure = exposure;
  }, [gl, exposure]);
  return null;
}

function LookSky({ profile }: { profile: VisualLookProfile }) {
  const material = useMemo(() => {
    return new ShaderMaterial({
      side: BackSide,
      depthWrite: false,
      uniforms: {
        uHorizon: { value: new Vector3(...profile.skyHorizon) },
        uMid: { value: new Vector3(...profile.skyMid) },
        uZenith: { value: new Vector3(...profile.skyZenith) },
        uSunDir: { value: new Vector3(...profile.sunDir).normalize() },
        uSunGlow: { value: new Vector3(...profile.sunGlow) },
        uSunPower: { value: profile.sunPower },
      },
      vertexShader: `
        varying vec3 vPos;
        void main() {
          vPos = normalize(position);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec3 uHorizon;
        uniform vec3 uMid;
        uniform vec3 uZenith;
        uniform vec3 uSunDir;
        uniform vec3 uSunGlow;
        uniform float uSunPower;
        varying vec3 vPos;
        void main() {
          float h = clamp(vPos.y * 0.5 + 0.42, 0.0, 1.0);
          vec3 col = mix(uHorizon, uMid, smoothstep(0.0, 0.34, h));
          col = mix(col, uZenith, smoothstep(0.34, 1.0, h));
          float sun = pow(max(dot(normalize(vPos), normalize(uSunDir)), 0.0), uSunPower);
          col += uSunGlow * sun * 1.35;
          float haze = pow(1.0 - abs(vPos.y), 3.0);
          col += uSunGlow * haze * 0.18;
          gl_FragColor = vec4(col, 1.0);
        }
      `,
    });
  }, [profile]);

  return (
    <mesh frustumCulled={false}>
      <sphereGeometry args={[260, 32, 24]} />
      <primitive object={material} attach="material" />
    </mesh>
  );
}

function LookEnvironment({ profile }: { profile: VisualLookProfile }) {
  const gl = useThree((state) => state.gl);
  const scene = useThree((state) => state.scene);

  useLayoutEffect(() => {
    const envScene = new Scene();
    envScene.background = new Color(profile.fog);
    envScene.add(new HemisphereLight(profile.envHemisphere, profile.envGround, 1.05));
    const sky = new Mesh(
      new SphereGeometry(8, 16, 12),
      new MeshBasicMaterial({ color: profile.background, side: BackSide }),
    );
    envScene.add(sky);
    const pmrem = new PMREMGenerator(gl);
    const envMap = pmrem.fromScene(envScene, 0.08).texture;
    scene.environment = envMap;
    scene.environmentIntensity = profile.envIntensity;
    sky.geometry.dispose();
    sky.material.dispose();
    return () => {
      scene.environment = null;
      envMap.dispose();
      pmrem.dispose();
    };
  }, [gl, scene, profile]);

  return null;
}

export function ExperienceCanvas() {
  const qualityPreset = useAppStore((state) => state.preferences.qualityPreset);
  const capabilities = detectDeviceCapabilities();
  const quality = resolveQuality(qualityPreset, capabilities);
  const { look } = useVisualLook();
  const profile = VISUAL_LOOK_PROFILES[look];

  return (
    <Canvas
      aria-hidden
      dpr={[1, quality.dprCap]}
      gl={{
        antialias: quality.tier !== 'LOW',
        powerPreference: 'high-performance',
        toneMapping: ACESFilmicToneMapping,
        toneMappingExposure: profile.exposure,
      }}
      camera={{
        position: CAM_HERO_EXTERIOR_16X9.position,
        fov: CAM_HERO_EXTERIOR_16X9.vfovDeg,
        near: 0.15,
        far: 420,
      }}
    >
      <color attach="background" args={[profile.background]} />
      <fog attach="fog" args={[profile.fog, profile.fogNear, profile.fogFar]} />
      <ApplyExposure exposure={profile.exposure} />
      <LookSky profile={profile} />
      <LookEnvironment profile={profile} />
      <hemisphereLight
        color={profile.hemisphereSky}
        groundColor={profile.hemisphereGround}
        intensity={profile.hemisphereIntensity}
      />
      <ambientLight intensity={profile.ambientIntensity} color={profile.ambient} />
      <directionalLight
        position={profile.sunPosition}
        intensity={profile.sunIntensity}
        color={profile.sunColor}
      />
      <directionalLight
        position={profile.fillPosition}
        intensity={profile.fillIntensity}
        color={profile.fillColor}
      />
      <directionalLight
        position={profile.rimPosition}
        intensity={profile.rimIntensity}
        color={profile.rimColor}
      />
      <directionalLight
        position={profile.warmKeyPosition}
        intensity={profile.warmKeyIntensity}
        color={profile.warmKeyColor}
      />
      <spotLight
        position={[0, 12, 16]}
        angle={0.55}
        penumbra={0.72}
        intensity={look === 'SYSTEM' ? 8 : 16}
        color="#ffd4a8"
        distance={48}
        decay={2}
      />
      <pointLight position={[0, 6.2, 10]} color="#ffb070" intensity={7.2} distance={48} decay={2} />
      <pointLight
        position={[-28.4, 9.2, -1.5]}
        color="#ffd4a0"
        intensity={6.2}
        distance={22}
        decay={2}
      />
      <Suspense fallback={null}>
        <ExteriorResidence look={look} />
        <IslandTerrain />
        <IslandOcean look={look} />
        <ShoreFoam />
        <RealTrees />
        <WaterFeature look={look} />
        <WaterDebugOverlay />
      </Suspense>
      {quality.shadows ? (
        <ContactShadows position={[0, 0.02, 0]} opacity={0.18} scale={48} blur={2.4} far={14} />
      ) : null}
      <ExteriorHeroCamera />
    </Canvas>
  );
}
