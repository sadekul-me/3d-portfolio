import { useMemo } from 'react';
import { CanvasTexture, SRGBColorSpace } from 'three';

import type { VisualLook } from '@/experience/look/visualLook';

type Display = {
  id: string;
  title: string;
  subtitle: string;
  position: [number, number, number];
  rotation: [number, number, number];
  size: [number, number];
};

const DISPLAYS: Display[] = [
  {
    id: '02',
    title: 'ENGINEERING WING',
    subtitle: 'SYSTEMS / PLATFORM',
    position: [-16.8, 7.725, 7.27],
    rotation: [0, 0, 0],
    size: [2.48, 1.18],
  },
  {
    id: '03',
    title: 'AI LAB',
    subtitle: 'MODELS / AGENTS',
    position: [16.6, 10.29, 6.52],
    rotation: [0, 0, 0],
    size: [2.38, 1.12],
  },
  {
    id: '04',
    title: 'PROJECTS GALLERY',
    subtitle: 'SELECTED WORK',
    position: [8.8, 7.125, 7.71],
    rotation: [0, 0, 0],
    size: [2.18, 0.96],
  },
  {
    id: '05',
    title: 'ARCHITECTURE CORE',
    subtitle: 'SPACES / STRUCTURE',
    position: [-8.4, 5.91, 7.61],
    rotation: [0, 0, 0],
    size: [2.18, 0.94],
  },
  {
    id: '06',
    title: 'COMMAND CENTER',
    subtitle: 'LIVE STATE',
    position: [2.4, 13.16, 4.32],
    rotation: [0, 0, 0],
    size: [2.62, 1.02],
  },
];

function makeScreen(display: Display, cinematic: boolean): CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    return new CanvasTexture(canvas);
  }
  ctx.fillStyle = cinematic ? '#120e0c' : '#070b0e';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = cinematic ? 'rgba(255,150,70,0.16)' : 'rgba(70,200,220,0.22)';
  ctx.lineWidth = 1;
  for (let x = 64; x < canvas.width; x += 64) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }
  ctx.fillStyle = cinematic ? '#c07038' : '#3aa8b8';
  ctx.fillRect(40, 48, 8, 72);
  ctx.fillStyle = cinematic ? '#ffb070' : '#7ee7f2';
  ctx.font = '700 64px Segoe UI, sans-serif';
  ctx.fillText(display.id, 64, 110);
  ctx.font = '600 44px Segoe UI, sans-serif';
  ctx.fillStyle = cinematic ? '#f2d4b4' : '#e8f7fb';
  ctx.fillText(display.title, 64, 178);
  ctx.font = '500 22px Segoe UI, sans-serif';
  ctx.fillStyle = cinematic ? '#c09070' : '#8ecad4';
  ctx.fillText(display.subtitle, 64, 228);
  ctx.font = '400 18px Segoe UI, sans-serif';
  ctx.fillStyle = cinematic ? '#8a6050' : '#5a9aaa';
  ctx.fillText(cinematic ? 'GOLDEN HOUR LINK' : 'PORTFOLIO NODE  ·  LIVE', 64, 290);
  const texture = new CanvasTexture(canvas);
  texture.colorSpace = SRGBColorSpace;
  texture.needsUpdate = true;
  return texture;
}

export function PortfolioDisplays({ look }: { look: VisualLook }) {
  const textures = useMemo(
    () => DISPLAYS.map((display) => makeScreen(display, look === 'CINEMATIC')),
    [look],
  );
  const accent = look === 'SYSTEM' ? '#4ec8d8' : '#e09050';

  return (
    <group>
      {DISPLAYS.map((display, index) => (
        <group key={display.id} position={display.position} rotation={display.rotation}>
          <mesh>
            <planeGeometry args={display.size} />
            <meshStandardMaterial
              map={textures[index] ?? null}
              emissive="#ffffff"
              emissiveMap={textures[index] ?? null}
              emissiveIntensity={look === 'SYSTEM' ? 0.92 : 0.32}
              roughness={0.18}
              metalness={0.04}
            />
          </mesh>
          <mesh position={[0, display.size[1] * 0.5 - 0.02, 0.01]}>
            <boxGeometry args={[display.size[0], 0.018, 0.018]} />
            <meshStandardMaterial
              color={accent}
              emissive={accent}
              emissiveIntensity={look === 'SYSTEM' ? 1.8 : 0.8}
            />
          </mesh>
        </group>
      ))}
    </group>
  );
}
