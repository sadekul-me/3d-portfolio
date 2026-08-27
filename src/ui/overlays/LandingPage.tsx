import { useEffect } from 'react';
import { motion } from 'motion/react';

import { LanguageToggle, TextButton } from '@/ui/primitives/Button';
import { translate } from '@/i18n/translate';
import { useAppStore } from '@/store/appStore';
import { dispatchCommand } from '@/app/commands/dispatcher';
import { applyDocumentMeta } from '@/seo/meta';
import { buildJsonLd, toJsonLdScript } from '@/seo/jsonLd';
import { loadCatalog } from '@/content/repositories/catalogRepository';
import { durationForMotion } from '@/animation/tokens/motionTokens';

export function LandingPage() {
  const locale = useAppStore((state) => state.preferences.locale);
  const soundEnabled = useAppStore((state) => state.preferences.soundEnabled);
  const reducedMotion = useAppStore((state) => state.preferences.reducedMotion);
  const catalog = loadCatalog();

  useEffect(() => {
    applyDocumentMeta({
      title: `${translate(locale, 'landing.title')} · ${translate(locale, 'landing.kicker')}`,
      description: translate(locale, 'landing.subtitle'),
      canonicalPath: '/',
      locale,
    });
  }, [locale]);

  const jsonLd = toJsonLdScript(buildJsonLd(locale, catalog));

  return (
    <motion.main
      id="main"
      className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16"
      initial={reducedMotion ? false : { opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: durationForMotion(reducedMotion, 'panelOpenMs') / 1000 }}
    >
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd }} />
      <p className="text-xs uppercase tracking-[0.3em] text-accent-cool">
        {translate(locale, 'landing.kicker')}
      </p>
      <h1 className="mt-4 max-w-3xl text-4xl font-light leading-tight text-mist sm:text-6xl">
        {translate(locale, 'landing.title')}
      </h1>
      <p className="mt-6 max-w-2xl text-base leading-relaxed text-metal sm:text-lg">
        {translate(locale, 'landing.subtitle')}
      </p>
      <p className="mt-4 max-w-2xl text-sm text-metal/80">
        {translate(locale, 'landing.placeholderNotice')}
      </p>
      <nav
        aria-label={translate(locale, 'a11y.primaryNav')}
        className="mt-10 flex flex-wrap items-center gap-3"
      >
        <TextButton labelKey="landing.enterExperience" to="/experience/exterior" />
        <TextButton labelKey="landing.quickPortfolio" to="/portfolio" />
        <TextButton labelKey="landing.resume" to="/resume" />
        <TextButton labelKey="landing.contact" to="/contact" />
        <LanguageToggle />
        <TextButton
          labelKey={soundEnabled ? 'landing.soundOn' : 'landing.soundOff'}
          onClick={() =>
            dispatchCommand({ type: 'SET_SOUND', enabled: !soundEnabled, source: 'user' })
          }
        />
      </nav>
    </motion.main>
  );
}
