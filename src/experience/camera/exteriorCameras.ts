import { PerspectiveCamera, Vector3 } from 'three';

export const EXTERIOR_CAMERA_IDS = [
  'CAM_Hero_Exterior',
  'CAM_Front_Exterior',
  'CAM_ThreeQuarter_Left',
  'CAM_ThreeQuarter_Right',
  'CAM_Entrance_Closeup',
  'CAM_Elevated_Island',
] as const;

export type ExteriorCameraId = (typeof EXTERIOR_CAMERA_IDS)[number];

export const DEFAULT_EXTERIOR_CAMERA: ExteriorCameraId = 'CAM_Hero_Exterior';

export type Vec3Tuple = [number, number, number];

export type ExteriorCameraPose = {
  id: ExteriorCameraId;
  position: Vec3Tuple;
  target: Vec3Tuple;
  vfovDeg: number;
  focalMm: number;
  minDistance: number;
  maxDistance: number;
};

type WorldBox = {
  min: Vec3Tuple;
  max: Vec3Tuple;
};

type FrameInsets = {
  left: number;
  right: number;
  top: number;
  bottom: number;
};

type FittedPreset = {
  id: ExteriorCameraId;
  azimuthDeg: number;
  elevationDeg: number;
  vfovDeg: number;
  target: Vec3Tuple;
  box: WorldBox;
  frame: FrameInsets;
};

/**
 * Building + identity monolith AABB in Three.js space.
 * Monolith west ~-28.4 (4.4m wide); east wing ~+22; roofs ~14–17.5m; north massing ~-10 Z.
 */
export const ARCHITECTURE_BOUNDS: WorldBox = {
  min: [-31.0, 0.0, -10.0],
  max: [22.6, 17.6, 12.5],
};

/** Visible terraced island (not the full heightfield mesh). */
export const ISLAND_BOUNDS: WorldBox = {
  min: [-33.0, -1.62, -12.0],
  max: [28.0, 0.45, 24.5],
};

/** Points on actual massing — AABB corners over-estimate 3/4 projected width. */
const VISUAL_MASS_POINTS: Vec3Tuple[] = [
  [-30.6, 0.0, -2.0],
  [-30.6, 17.4, -2.0],
  [-26.2, 17.4, 0.4],
  [-22.0, 8.0, 8.0],
  [-8.0, 4.0, 10.0],
  [0.0, 6.2, 9.5],
  [0.0, 13.8, -1.5],
  [16.0, 8.0, 5.0],
  [22.0, 0.2, 3.5],
  [22.0, 11.5, 2.0],
  [4.0, 13.5, 1.5],
];
const GATE_POINTS: Vec3Tuple[] = [
  [-2.5, 0.0, 26.2],
  [2.5, 0.0, 26.2],
  [-2.5, 3.2, 26.2],
  [2.5, 3.2, 26.2],
];

const ISLAND_FIT_BOX: WorldBox = {
  min: [-34.0, -1.62, -20.0],
  max: [30.0, 17.6, 31.0],
};

/** Inner rect for campus fit: architecture 60–68% width with island/ocean context. */
const HERO_FRAME: FrameInsets = {
  left: 0.17,
  right: 0.15,
  top: 0.15,
  bottom: 0.17,
};

const FRONT_FRAME: FrameInsets = {
  left: 0.1,
  right: 0.1,
  top: 0.1,
  bottom: 0.13,
};

const ELEVATED_FRAME: FrameInsets = {
  left: 0.08,
  right: 0.08,
  top: 0.12,
  bottom: 0.14,
};

const GATE_FRAME: FrameInsets = {
  left: 0.05,
  right: 0.05,
  top: 0.08,
  bottom: 0.06,
};

const TARGET_BUILDING_WIDTH = 0.76;

const FAILED_ENTRANCE_CLOSEUP: ExteriorCameraPose = {
  id: 'CAM_Entrance_Closeup',
  position: [17.2, 8.35, 20.6],
  target: [-3.8, 5.4, -0.8],
  vfovDeg: 32,
  focalMm: focalMmFromVerticalFov(32),
  minDistance: 10,
  maxDistance: 28,
};

const FITTED_PRESETS: Record<Exclude<ExteriorCameraId, 'CAM_Entrance_Closeup'>, FittedPreset> = {
  CAM_Hero_Exterior: {
    id: 'CAM_Hero_Exterior',
    azimuthDeg: 28,
    elevationDeg: 9.6,
    vfovDeg: 32,
    target: [-4.8, 5.95, 3.0],
    box: ARCHITECTURE_BOUNDS,
    frame: HERO_FRAME,
  },
  CAM_Front_Exterior: {
    id: 'CAM_Front_Exterior',
    azimuthDeg: 0,
    elevationDeg: 10.8,
    vfovDeg: 31,
    target: [-4.4, 5.4, 3.6],
    box: ARCHITECTURE_BOUNDS,
    frame: FRONT_FRAME,
  },
  CAM_ThreeQuarter_Left: {
    id: 'CAM_ThreeQuarter_Left',
    azimuthDeg: -27,
    elevationDeg: 11.2,
    vfovDeg: 31,
    target: [-2.2, 5.7, 3.4],
    box: ARCHITECTURE_BOUNDS,
    frame: HERO_FRAME,
  },
  CAM_ThreeQuarter_Right: {
    id: 'CAM_ThreeQuarter_Right',
    azimuthDeg: 34,
    elevationDeg: 11.0,
    vfovDeg: 31,
    target: [-5.2, 5.6, 3.2],
    box: ARCHITECTURE_BOUNDS,
    frame: HERO_FRAME,
  },
  CAM_Elevated_Island: {
    id: 'CAM_Elevated_Island',
    azimuthDeg: 24,
    elevationDeg: 20,
    vfovDeg: 32,
    target: [-4.0, 4.0, 4.2],
    box: ISLAND_FIT_BOX,
    frame: ELEVATED_FRAME,
  },
};

const WORLD_UP = new Vector3(0, 1, 0);

export function focalMmFromVerticalFov(vfovDeg: number, filmHeightMm = 24): number {
  const half = (vfovDeg * Math.PI) / 360;
  return filmHeightMm / (2 * Math.tan(half));
}

export function cameraDirection(azimuthDeg: number, elevationDeg: number): Vector3 {
  const az = (azimuthDeg * Math.PI) / 180;
  const el = (elevationDeg * Math.PI) / 180;
  const cosEl = Math.cos(el);
  return new Vector3(Math.sin(az) * cosEl, Math.sin(el), Math.cos(az) * cosEl);
}

function boxCorners(box: WorldBox): Vector3[] {
  const [x0, y0, z0] = box.min;
  const [x1, y1, z1] = box.max;
  const corners: Vector3[] = [];
  for (const x of [x0, x1]) {
    for (const y of [y0, y1]) {
      for (const z of [z0, z1]) {
        corners.push(new Vector3(x, y, z));
      }
    }
  }
  return corners;
}

function requiredDistance(
  corners: Vector3[],
  target: Vector3,
  dirToCamera: Vector3,
  vfovDeg: number,
  aspect: number,
  frame: FrameInsets,
): number {
  const forward = dirToCamera.clone().negate().normalize();
  const right = new Vector3().crossVectors(forward, WORLD_UP).normalize();
  const up = new Vector3().crossVectors(right, forward).normalize();
  const tanHalfV = Math.tan(((vfovDeg * Math.PI) / 180) / 2);
  const tanHalfH = tanHalfV * aspect;
  const usableH = tanHalfH * (1 - frame.left - frame.right);
  const usableV = tanHalfV * (1 - frame.top - frame.bottom);
  const offset = new Vector3();
  let distance = 1;

  for (const corner of corners) {
    offset.copy(corner).sub(target);
    const x = offset.dot(right);
    const y = offset.dot(up);
    const depthOffset = -offset.dot(dirToCamera);
    distance = Math.max(distance, Math.abs(x) / usableH - depthOffset);
    distance = Math.max(distance, Math.abs(y) / usableV - depthOffset);
  }

  return distance * 1.03;
}

function poseAtDistance(
  preset: FittedPreset,
  dir: Vector3,
  target: Vector3,
  distance: number,
): ExteriorCameraPose {
  const position = target.clone().addScaledVector(dir, distance);
  return {
    id: preset.id,
    position: [position.x, position.y, position.z],
    target: preset.target,
    vfovDeg: preset.vfovDeg,
    focalMm: focalMmFromVerticalFov(preset.vfovDeg),
    minDistance: distance * 0.92,
    maxDistance: distance * 1.18,
  };
}

function pointsInFrame(
  camera: PerspectiveCamera,
  points: Vector3[],
  frame: FrameInsets,
): boolean {
  const ndc = new Vector3();
  const minX = -1 + 2 * frame.left;
  const maxX = 1 - 2 * frame.right;
  const minY = -1 + 2 * frame.bottom;
  const maxY = 1 - 2 * frame.top;
  for (const point of points) {
    ndc.copy(point).project(camera);
    if (ndc.z < -1 || ndc.z > 1) {
      return false;
    }
    if (ndc.x < minX || ndc.x > maxX || ndc.y < minY || ndc.y > maxY) {
      return false;
    }
  }
  return true;
}

function poseFromFitted(preset: FittedPreset, aspect: number): ExteriorCameraPose {
  const dir = cameraDirection(preset.azimuthDeg, preset.elevationDeg);
  const target = new Vector3(...preset.target);
  const massPoints = VISUAL_MASS_POINTS.map(([x, y, z]) => new Vector3(x, y, z));
  const safeAspect = Math.max(aspect, 0.5);
  const seeded = requiredDistance(
    massPoints,
    target,
    dir,
    preset.vfovDeg,
    safeAspect,
    preset.frame,
  );

  const includeGate =
    preset.id === 'CAM_Hero_Exterior' ||
    preset.id === 'CAM_Front_Exterior' ||
    preset.id === 'CAM_ThreeQuarter_Left' ||
    preset.id === 'CAM_ThreeQuarter_Right';
  const gateVectors = GATE_POINTS.map(([x, y, z]) => new Vector3(x, y, z));
  const massFrame: FrameInsets =
    preset.id === 'CAM_Hero_Exterior'
      ? { left: 0.155, right: 0.14, top: 0.13, bottom: 0.155 }
      : { left: 0.08, right: 0.08, top: 0.1, bottom: 0.12 };

  const evaluate = (distance: number) => {
    const pose = poseAtDistance(preset, dir, target, distance);
    const camera = makeFramedCamera(pose, safeAspect);
    const building = measureBoundsOccupancy(camera, ARCHITECTURE_BOUNDS);
    const island = measureBoundsOccupancy(camera, ISLAND_BOUNDS);
    const gateOk = !includeGate || pointsInFrame(camera, gateVectors, GATE_FRAME);
    const massOk = pointsInFrame(camera, massPoints, massFrame);
    const cropped = pose.position[2] <= 28 || !massOk || !gateOk;
    return { pose, building, island, cropped };
  };

  let lo = Math.max(32, seeded * 0.72);
  let hi = Math.max(seeded, 40);
  for (let i = 0; i < 10 && evaluate(hi).cropped; i += 1) {
    hi *= 1.05;
  }
  let best = hi;
  for (let i = 0; i < 20; i += 1) {
    const mid = (lo + hi) / 2;
    const { cropped } = evaluate(mid);
    if (cropped) {
      lo = mid;
    } else {
      best = mid;
      hi = mid;
    }
  }

  return poseAtDistance(preset, dir, target, preset.id === 'CAM_Hero_Exterior' ? best * 1.08 : best);
}

export function resolveExteriorCamera(
  id: ExteriorCameraId,
  viewportWidth: number,
  viewportHeight: number,
): ExteriorCameraPose {
  if (id === 'CAM_Entrance_Closeup') {
    return FAILED_ENTRANCE_CLOSEUP;
  }
  const aspect = viewportWidth / Math.max(viewportHeight, 1);
  return poseFromFitted(FITTED_PRESETS[id], aspect);
}

export function makeFramedCamera(pose: ExteriorCameraPose, aspect: number): PerspectiveCamera {
  const camera = new PerspectiveCamera(pose.vfovDeg, aspect, 0.15, 420);
  camera.position.set(...pose.position);
  camera.lookAt(...pose.target);
  camera.updateProjectionMatrix();
  camera.updateMatrixWorld();
  return camera;
}

export type BoundsOccupancy = {
  width: number;
  height: number;
  minNdcX: number;
  maxNdcX: number;
  minNdcY: number;
  maxNdcY: number;
};

export function measureBoundsOccupancy(
  camera: PerspectiveCamera,
  box: WorldBox,
): BoundsOccupancy {
  const ndc = new Vector3();
  let minNdcX = Infinity;
  let maxNdcX = -Infinity;
  let minNdcY = Infinity;
  let maxNdcY = -Infinity;
  for (const corner of boxCorners(box)) {
    ndc.copy(corner).project(camera);
    minNdcX = Math.min(minNdcX, ndc.x);
    maxNdcX = Math.max(maxNdcX, ndc.x);
    minNdcY = Math.min(minNdcY, ndc.y);
    maxNdcY = Math.max(maxNdcY, ndc.y);
  }
  return {
    width: (maxNdcX - minNdcX) / 2,
    height: (maxNdcY - minNdcY) / 2,
    minNdcX,
    maxNdcX,
    minNdcY,
    maxNdcY,
  };
}

export const CAM_HERO_EXTERIOR_16X9 = resolveExteriorCamera('CAM_Hero_Exterior', 1920, 1080);

const WATER_CLOSEUP_POSE: ExteriorCameraPose = {
  id: 'CAM_Entrance_Closeup',
  position: [-9.6, 2.85, 13.4],
  target: [-14.2, 1.35, 8.4],
  vfovDeg: 36,
  focalMm: focalMmFromVerticalFov(36),
  minDistance: 4,
  maxDistance: 18,
};

const WATER_TOP_POSE: ExteriorCameraPose = {
  id: 'CAM_Elevated_Island',
  position: [-4.0, 88.0, 8.0],
  target: [-4.0, 0.0, 8.0],
  vfovDeg: 28,
  focalMm: focalMmFromVerticalFov(28),
  minDistance: 40,
  maxDistance: 140,
};

export function resolveSessionCamera(
  viewportWidth: number,
  viewportHeight: number,
): ExteriorCameraPose {
  const cam =
    typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('cam') : null;
  if (cam === 'waterCloseup') {
    return WATER_CLOSEUP_POSE;
  }
  if (cam === 'waterTop') {
    return WATER_TOP_POSE;
  }
  if (cam === 'shore' || cam === 'threeQuarter') {
    return resolveExteriorCamera('CAM_ThreeQuarter_Right', viewportWidth, viewportHeight);
  }
  if (cam === 'front') {
    return resolveExteriorCamera('CAM_Front_Exterior', viewportWidth, viewportHeight);
  }
  if (cam === 'monolith') {
    return {
      id: 'CAM_Entrance_Closeup',
      position: [-22.2, 12.4, 16.8],
      target: [-28.4, 11.3, -1.1],
      vfovDeg: 24,
      focalMm: focalMmFromVerticalFov(24),
      minDistance: 10,
      maxDistance: 32,
    };
  }
  if (cam === 'entranceSign') {
    return {
      id: 'CAM_Entrance_Closeup',
      position: [0.2, 7.15, 22.4],
      target: [0.0, 6.85, 9.9],
      vfovDeg: 26,
      focalMm: focalMmFromVerticalFov(26),
      minDistance: 8,
      maxDistance: 28,
    };
  }
  if (cam === 'zone' || cam === 'zone02') {
    return {
      id: 'CAM_Entrance_Closeup',
      position: [-17.22, 7.15, 16.8],
      target: [-17.22, 7.05, 9.72],
      vfovDeg: 28,
      focalMm: focalMmFromVerticalFov(28),
      minDistance: 6,
      maxDistance: 24,
    };
  }
  if (cam === 'zone01') {
    return {
      id: 'CAM_Entrance_Closeup',
      position: [-6.4, 3.85, 12.4],
      target: [-8.05, 3.79, 4.20],
      vfovDeg: 28,
      focalMm: focalMmFromVerticalFov(28),
      minDistance: 5,
      maxDistance: 20,
    };
  }
  if (cam === 'zone03') {
    return {
      id: 'CAM_Entrance_Closeup',
      position: [15.85, 10.7, 10.8],
      target: [15.85, 10.65, 1.15],
      vfovDeg: 28,
      focalMm: focalMmFromVerticalFov(28),
      minDistance: 5,
      maxDistance: 22,
    };
  }
  if (cam === 'zone04') {
    return {
      id: 'CAM_Entrance_Closeup',
      position: [13.55, 4.85, 14.2],
      target: [13.55, 4.75, 4.55],
      vfovDeg: 28,
      focalMm: focalMmFromVerticalFov(28),
      minDistance: 5,
      maxDistance: 22,
    };
  }
  if (cam === 'zone05') {
    return {
      id: 'CAM_Entrance_Closeup',
      position: [-10.4, 3.65, 12.8],
      target: [-13.25, 3.55, 4.2],
      vfovDeg: 28,
      focalMm: focalMmFromVerticalFov(28),
      minDistance: 5,
      maxDistance: 22,
    };
  }
  if (cam === 'zone06') {
    return {
      id: 'CAM_Entrance_Closeup',
      position: [3.55, 10.75, 11.2],
      target: [3.55, 10.7, 1.35],
      vfovDeg: 28,
      focalMm: focalMmFromVerticalFov(28),
      minDistance: 5,
      maxDistance: 22,
    };
  }
  return resolveExteriorCamera(DEFAULT_EXTERIOR_CAMERA, viewportWidth, viewportHeight);
}
