import { translate } from '@/i18n/translate';
import { useAppStore } from '@/store/appStore';

export function GenericErrorFallback() {
  const locale = useAppStore((state) => state.preferences.locale);
  return (
    <section className="mx-auto max-w-xl px-6 py-16">
      <h1 className="text-2xl text-mist">{translate(locale, 'app.name')}</h1>
      <p className="mt-4 text-metal">{translate(locale, 'errors.generic')}</p>
    </section>
  );
}
