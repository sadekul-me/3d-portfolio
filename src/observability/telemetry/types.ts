import type { AppError } from '@/observability/errors/appError';
import type { CorrelationId, SessionId } from '@/types/ids';

export type TelemetryTags = Record<string, string | number | boolean | undefined>;

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export type LogEntry = {
  level: LogLevel;
  message: string;
  module: string;
  correlationId?: CorrelationId;
  sessionId?: SessionId;
  tags?: TelemetryTags;
};

export type MetricEntry = {
  name: string;
  value: number;
  unit?: 'ms' | 'count' | 'fps' | 'bytes';
  tags?: TelemetryTags;
};

export type TraceAttributes = TelemetryTags & {
  module?: string;
  correlationId?: CorrelationId;
};

export interface TelemetryService {
  log(entry: LogEntry): void;
  metric(entry: MetricEntry): void;
  trace<T>(name: string, fn: () => T, attributes?: TraceAttributes): T;
  traceAsync<T>(name: string, fn: () => Promise<T>, attributes?: TraceAttributes): Promise<T>;
  reportError(error: AppError): void;
}

export type TelemetryContext = {
  appVersion: string;
  buildId: string;
  assetManifestVersion: string;
  sessionId: SessionId;
};
