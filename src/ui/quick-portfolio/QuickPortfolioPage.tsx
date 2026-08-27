import { Link } from 'react-router-dom';

import { loadCatalog } from '@/content/repositories/catalogRepository';
import { isPubliclyListed } from '@/types/visibility';
import { localizedValue } from '@/types/locale';
import { translate } from '@/i18n/translate';
import { useAppStore } from '@/store/appStore';
import { LanguageToggle } from '@/ui/primitives/Button';
import { applyDocumentMeta } from '@/seo/meta';
import { useEffect } from 'react';

type Section = 'about' | 'experience' | 'skills' | 'projects' | 'architecture';

type Props = {
  section?: Section;
};

export function QuickPortfolioPage({ section = 'about' }: Props) {
  const locale = useAppStore((state) => state.preferences.locale);
  const catalog = loadCatalog();

  useEffect(() => {
    applyDocumentMeta({
      title: `${translate(locale, 'portfolio.title')} · Digital Residence`,
      description: translate(locale, 'portfolio.intro'),
      canonicalPath: '/portfolio',
      locale,
    });
  }, [locale]);

  const publishedProjects = catalog.projects.filter((item) =>
    isPubliclyListed(item.visibility, item.publicationStatus),
  );
  const publishedSkills = catalog.skills.filter((item) =>
    isPubliclyListed(item.visibility, item.publicationStatus),
  );
  const publishedExperience = catalog.experiences.filter((item) =>
    isPubliclyListed(item.visibility, item.publicationStatus),
  );
  const publishedArchitecture = catalog.architectureCases.filter((item) =>
    isPubliclyListed(item.visibility, item.publicationStatus),
  );

  return (
    <main id="main" className="mx-auto max-w-4xl px-6 py-16">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-accent-cool">
            {translate(locale, 'portfolio.title')}
          </p>
          <h1 className="mt-3 text-3xl text-mist">{translate(locale, 'app.name')}</h1>
          <p className="mt-4 max-w-2xl text-metal">{translate(locale, 'portfolio.intro')}</p>
        </div>
        <LanguageToggle />
      </header>
      <nav
        aria-label={translate(locale, 'a11y.primaryNav')}
        className="mt-8 flex flex-wrap gap-4 text-sm"
      >
        <Link to="/portfolio/about">{translate(locale, 'portfolio.about')}</Link>
        <Link to="/portfolio/experience">{translate(locale, 'portfolio.experience')}</Link>
        <Link to="/portfolio/skills">{translate(locale, 'portfolio.skills')}</Link>
        <Link to="/portfolio/projects">{translate(locale, 'portfolio.projects')}</Link>
        <Link to="/portfolio/architecture">{translate(locale, 'portfolio.architecture')}</Link>
        <Link to="/">{translate(locale, 'landing.title')}</Link>
      </nav>
      <section className="mt-10 space-y-6" aria-live="polite">
        {section === 'about' ? (
          <article>
            <h2 className="text-xl text-mist">{catalog.profile.displayName}</h2>
            <p className="mt-3 text-metal">{localizedValue(catalog.profile.summary, locale)}</p>
          </article>
        ) : null}
        {section === 'projects' ? (
          publishedProjects.length === 0 ? (
            <Empty />
          ) : (
            publishedProjects.map((project) => (
              <article key={project.id}>
                <h2 className="text-xl text-mist">{localizedValue(project.title, locale)}</h2>
                <p className="mt-2 text-metal">{localizedValue(project.summary, locale)}</p>
              </article>
            ))
          )
        ) : null}
        {section === 'skills' ? publishedSkills.length === 0 ? <Empty /> : null : null}
        {section === 'experience' ? publishedExperience.length === 0 ? <Empty /> : null : null}
        {section === 'architecture' ? publishedArchitecture.length === 0 ? <Empty /> : null : null}
      </section>
    </main>
  );
}

function Empty() {
  const locale = useAppStore((state) => state.preferences.locale);
  return <p className="text-metal">{translate(locale, 'portfolio.empty')}</p>;
}
