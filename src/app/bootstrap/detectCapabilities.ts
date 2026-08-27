export function detectWebGL(): { webgl: boolean; webgl2: boolean } {
  if (typeof document === 'undefined') {
    return { webgl: false, webgl2: false };
  }
  const canvas = document.createElement('canvas');
  const gl2 = canvas.getContext('webgl2');
  if (gl2) {
    return { webgl: true, webgl2: true };
  }
  const gl = canvas.getContext('webgl') ?? canvas.getContext('experimental-webgl');
  return { webgl: Boolean(gl), webgl2: false };
}

export function detectReducedMotion(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return false;
  }
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export function detectDeviceCapabilities() {
  const webgl = detectWebGL();
  const hardwareConcurrency =
    typeof navigator === 'undefined' ? 8 : Math.max(1, navigator.hardwareConcurrency || 4);
  const saveData =
    typeof navigator !== 'undefined' && 'connection' in navigator
      ? Boolean(
          (navigator as Navigator & { connection?: { saveData?: boolean } }).connection?.saveData,
        )
      : false;
  const maxDpr = typeof window === 'undefined' ? 1 : Math.min(window.devicePixelRatio || 1, 3);

  return {
    ...webgl,
    maxDpr,
    saveData,
    hardwareConcurrency,
    prefersReducedMotion: detectReducedMotion(),
  };
}
