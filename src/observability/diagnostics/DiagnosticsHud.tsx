import { publicRuntimeConfig } from '@/app/config/appConfig';
import { shouldExposeDiagnostics } from '@/observability/diagnostics/diagnosticsModel';
import { useAppStore } from '@/store/appStore';

export function DiagnosticsHud() {
  const visible = shouldExposeDiagnostics(
    publicRuntimeConfig.enableDiagnostics,
    import.meta.env.DEV,
  );
  const roomId = useAppStore((state) => state.navigation.currentRoomId);
  const quality = useAppStore((state) => state.preferences.qualityPreset);

  if (!visible) {
    return null;
  }

  return (
    <aside className="fixed right-4 bottom-4 z-50 rounded-lg border border-white/10 bg-black/70 p-3 font-mono text-xs text-mist">
      <p>Room: {roomId}</p>
      <p>Quality: {quality}</p>
    </aside>
  );
}
