import type { CorrelationId } from '@/types/ids';
import type { ExperienceMode } from '@/types/experience';
import type { ErrorCategory, ErrorSeverity } from '@/observability/errors/taxonomy';

export type AppError = {
  code: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  recoverable: boolean;
  visitorMessageKey: string;
  technicalMessage: string;
  correlationId?: CorrelationId;
  context?: Readonly<Record<string, string | number | boolean>>;
  fallbackStatus?: ExperienceMode;
};

export function createAppError(input: AppError): AppError {
  return input;
}
