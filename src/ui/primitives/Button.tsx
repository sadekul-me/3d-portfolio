import { Link } from 'react-router-dom';

import { translate, type MessageKey } from '@/i18n/translate';
import { useAppStore } from '@/store/appStore';
import { dispatchCommand } from '@/app/commands/dispatcher';
import type { Locale } from '@/types/locale';

type ButtonProps = {
  labelKey: MessageKey;
  onClick?: () => void;
  to?: string;
};

export function TextButton({ labelKey, onClick, to }: ButtonProps) {
  const locale = useAppStore((state) => state.preferences.locale);
  const className =
    'rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm tracking-wide text-mist transition hover:border-accent-cool/50 hover:text-white';

  if (to) {
    return (
      <Link className={className} to={to}>
        {translate(locale, labelKey)}
      </Link>
    );
  }

  return (
    <button type="button" className={className} onClick={onClick}>
      {translate(locale, labelKey)}
    </button>
  );
}

export function LanguageToggle() {
  const locale = useAppStore((state) => state.preferences.locale);
  const next: Locale = locale === 'en' ? 'zh-CN' : 'en';
  return (
    <button
      type="button"
      className="text-sm text-metal underline-offset-4 hover:text-mist hover:underline"
      onClick={() => dispatchCommand({ type: 'SET_LANGUAGE', locale: next, source: 'user' })}
      aria-label={translate(locale, 'app.language')}
    >
      {locale === 'en' ? translate(locale, 'app.chinese') : translate(locale, 'app.english')}
    </button>
  );
}
