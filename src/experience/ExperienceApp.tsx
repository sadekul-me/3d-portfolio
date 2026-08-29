import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { ExperienceCanvas } from '@/experience/ExperienceCanvas';
import { VisualLookContext } from '@/experience/look/VisualLookContext';
import type { VisualLook } from '@/experience/look/visualLook';
import { ExperienceHud } from '@/ui/hud/ExperienceHud';
import { DiagnosticsHud } from '@/observability/diagnostics/DiagnosticsHud';
import { AppErrorBoundary } from '@/app/boundaries/ErrorBoundaries';
import { translate } from '@/i18n/translate';
import { useAppStore } from '@/store/appStore';

export default function ExperienceApp() {
  const locale = useAppStore((state) => state.preferences.locale);
  const [look, setLook] = useState<VisualLook>('SYSTEM');
  const lookValue = useMemo(() => ({ look, setLook }), [look]);

  return (
    <main id="main" className="relative h-screen w-screen overflow-hidden bg-obsidian">
      <h1 className="sr-only">{translate(locale, 'a11y.experienceCanvas')}</h1>
      <AppErrorBoundary
        name="experience"
        fallback={
          <section className="px-6 py-16">
            <p className="text-metal">{translate(locale, 'experience.webglUnavailable')}</p>
            <Link to="/portfolio">{translate(locale, 'landing.quickPortfolio')}</Link>
          </section>
        }
      >
        <VisualLookContext.Provider value={lookValue}>
          <ExperienceCanvas />
          <ExperienceHud />
          <DiagnosticsHud />
        </VisualLookContext.Provider>
      </AppErrorBoundary>
    </main>
  );
}
