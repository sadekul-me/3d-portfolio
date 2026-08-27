import { translate } from '@/i18n/translate';
import { useAppStore } from '@/store/appStore';

export function SkipLink() {
  const locale = useAppStore((state) => state.preferences.locale);
  return (
    <a className="skip-link" href="#main">
      {translate(locale, 'app.skipToContent')}
    </a>
  );
}
