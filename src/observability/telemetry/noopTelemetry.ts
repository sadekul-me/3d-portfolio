import type { AppError } from '@/observability/errors/appError';
import type { TelemetryService } from '@/observability/telemetry/types';

export function createNoopTelemetry(): TelemetryService {
  return {
    log() {},
    metric() {},
    trace<T>(_name: string, fn: () => T): T {
      return fn();
    },
    async traceAsync<T>(_name: string, fn: () => Promise<T>): Promise<T> {
      return fn();
    },
    reportError(_error: AppError) {},
  };
}
