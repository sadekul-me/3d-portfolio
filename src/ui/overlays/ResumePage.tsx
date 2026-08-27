import { translate } from '@/i18n/translate';
import { useAppStore } from '@/store/appStore';
import { LanguageToggle } from '@/ui/primitives/Button';

export function ResumePage() {
  const locale = useAppStore((state) => state.preferences.locale);
  return (
    <main id="main" className="mx-auto max-w-3xl px-6 py-16">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl text-mist">{translate(locale, 'resume.title')}</h1>
        <LanguageToggle />
      </div>
      <p className="mt-6 text-metal">{translate(locale, 'resume.unavailable')}</p>
    </main>
  );
}

export function ContactPage() {
  const locale = useAppStore((state) => state.preferences.locale);
  return (
    <main id="main" className="mx-auto max-w-3xl px-6 py-16">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl text-mist">{translate(locale, 'contact.title')}</h1>
        <LanguageToggle />
      </div>
      <p className="mt-6 text-metal">{translate(locale, 'contact.unavailable')}</p>
    </main>
  );
}
