import { createAnonymousSessionId } from '@/lib/ids';
import { createConsoleTelemetry } from '@/observability/telemetry/consoleTelemetry';
import { createNoopTelemetry } from '@/observability/telemetry/noopTelemetry';
import type { TelemetryService } from '@/observability/telemetry/types';
import { publicRuntimeConfig } from '@/app/config/appConfig';

let telemetry: TelemetryService | null = null;

export function getTelemetry(): TelemetryService {
  if (telemetry) {
    return telemetry;
  }
  const context = {
    appVersion: publicRuntimeConfig.appVersion,
    buildId: publicRuntimeConfig.buildId,
    assetManifestVersion: publicRuntimeConfig.assetManifestVersion,
    sessionId: createAnonymousSessionId(),
  };
  telemetry = import.meta.env.DEV ? createConsoleTelemetry(context) : createNoopTelemetry();
  return telemetry;
}

export function setTelemetryForTests(service: TelemetryService): void {
  telemetry = service;
}
