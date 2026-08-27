import { BrowserRouter } from 'react-router-dom';
import { useEffect } from 'react';

import { AppRoutes } from '@/app/routes/AppRoutes';
import { AppErrorBoundary } from '@/app/boundaries/ErrorBoundaries';
import { hydratePreferences } from '@/app/bootstrap/hydratePreferences';
import { attachDevelopmentEventDebug } from '@/events/index';
import { SkipLink } from '@/ui/accessibility/SkipLink';
import { loadCatalog } from '@/content/repositories/catalogRepository';
import { registerDefaultAssets } from '@/assets/registerDefaultAssets';

hydratePreferences();
attachDevelopmentEventDebug();
loadCatalog();
registerDefaultAssets();

export function App() {
  useEffect(() => {
    document.documentElement.dataset.foundation = 'digital-residence';
  }, []);

  return (
    <AppErrorBoundary name="app">
      <SkipLink />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AppErrorBoundary>
  );
}
