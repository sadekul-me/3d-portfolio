import { Component, type ErrorInfo, type ReactNode } from 'react';

import { getTelemetry } from '@/observability/telemetry/createTelemetry';
import { GenericErrorFallback } from '@/app/boundaries/GenericErrorFallback';

type Props = {
  name: string;
  children: ReactNode;
  fallback?: ReactNode;
};

type State = {
  hasError: boolean;
};

export class AppErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    getTelemetry().reportError({
      code: 'BOUNDARY_CAUGHT',
      category: 'APP',
      severity: 'ERROR',
      recoverable: true,
      visitorMessageKey: 'errors.generic',
      technicalMessage: error.message,
      context: {
        boundary: this.props.name,
        componentStack: info.componentStack?.slice(0, 200) ?? '',
      },
    });
  }

  render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }
    if (this.props.fallback) {
      return this.props.fallback;
    }
    return <GenericErrorFallback />;
  }
}
