import type { AppError } from '@/observability/errors/appError';
import type {
  LogEntry,
  MetricEntry,
  TelemetryContext,
  TelemetryService,
  TraceAttributes,
} from '@/observability/telemetry/types';

const FORBIDDEN = [
  'authorization',
  'api_key',
  'apikey',
  'password',
  'smtp_password',
  'private_key',
];

function containsForbidden(value: unknown): boolean {
  try {
    const serialized = JSON.stringify(value).toLowerCase();
    return FORBIDDEN.some((token) => serialized.includes(token));
  } catch {
    return false;
  }
}

function withContext(context: TelemetryContext, extra: Record<string, unknown>) {
  return {
    appVersion: context.appVersion,
    buildId: context.buildId,
    assetManifestVersion: context.assetManifestVersion,
    sessionId: context.sessionId,
    ...extra,
  };
}

export function createConsoleTelemetry(context: TelemetryContext): TelemetryService {
  return {
    log(entry: LogEntry) {
      if (containsForbidden(entry)) {
        console.warn({ type: 'telemetry-redacted', module: entry.module });
        return;
      }
      const payload = withContext(context, { ...entry });
      if (entry.level === 'error') {
        console.error(payload);
        return;
      }
      if (entry.level === 'warn') {
        console.warn(payload);
        return;
      }
      if (import.meta.env.DEV) {
        console.info(payload);
      }
    },
    metric(entry: MetricEntry) {
      if (containsForbidden(entry)) {
        return;
      }
      if (import.meta.env.DEV) {
        console.info(withContext(context, { type: 'metric', ...entry }));
      }
    },
    trace<T>(name: string, fn: () => T, attributes?: TraceAttributes): T {
      const started = performance.now();
      try {
        return fn();
      } finally {
        const latencyMs = performance.now() - started;
        if (import.meta.env.DEV) {
          console.info(
            withContext(context, { type: 'trace', name, latencyMs, ...(attributes ?? {}) }),
          );
        }
      }
    },
    async traceAsync<T>(
      name: string,
      fn: () => Promise<T>,
      attributes?: TraceAttributes,
    ): Promise<T> {
      const started = performance.now();
      try {
        return await fn();
      } finally {
        const latencyMs = performance.now() - started;
        if (import.meta.env.DEV) {
          console.info(
            withContext(context, { type: 'trace', name, latencyMs, ...(attributes ?? {}) }),
          );
        }
      }
    },
    reportError(error: AppError) {
      if (containsForbidden(error)) {
        console.error({ type: 'error-redacted', code: error.code, category: error.category });
        return;
      }
      console.error(withContext(context, { type: 'error', ...error }));
    },
  };
}
