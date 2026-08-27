import { ROOM_IDS, type RoomId } from '@/types/ids';
import { dispatchCommand } from '@/app/commands/dispatcher';
import { useAppStore } from '@/store/appStore';
import { translate, type MessageKey } from '@/i18n/translate';
import { selectRoomTitle } from '@/content/selectors/contentSelectors';

const ROOM_LABEL_KEYS: Record<RoomId, MessageKey> = {
  exterior: 'nav.exterior',
  identity: 'nav.identity',
  engineering: 'nav.engineering',
  'ai-lab': 'nav.aiLab',
  projects: 'nav.projects',
  architecture: 'nav.architecture',
  'command-center': 'nav.commandCenter',
};

export function ExperienceHud() {
  const locale = useAppStore((state) => state.preferences.locale);
  const currentRoomId = useAppStore((state) => state.navigation.currentRoomId);
  const phase = useAppStore((state) => state.navigation.phase);
  const reducedMotion = useAppStore((state) => state.preferences.reducedMotion);

  return (
    <div className="pointer-events-none absolute inset-0 z-10 flex flex-col justify-between p-4 sm:p-6">
      <header className="pointer-events-auto flex items-center justify-between gap-4">
        <p className="text-sm text-mist">
          {translate(locale, 'nav.currentLocation')}: {selectRoomTitle(currentRoomId, locale)}
        </p>
        {phase === 'TRANSITIONING' || phase === 'REQUESTED' ? (
          <button
            type="button"
            className="rounded-full border border-white/20 px-3 py-1 text-xs"
            onClick={() => dispatchCommand({ type: 'SKIP_CINEMATIC', source: 'user' })}
          >
            {translate(locale, 'app.skipCinematic')}
          </button>
        ) : null}
      </header>
      <nav
        aria-label={translate(locale, 'nav.map')}
        className="pointer-events-auto flex max-w-full flex-wrap gap-2 rounded-2xl border border-white/10 bg-black/30 p-3 backdrop-blur"
      >
        {ROOM_IDS.map((roomId) => (
          <button
            key={roomId}
            type="button"
            className={`rounded-full px-3 py-1 text-xs ${
              roomId === currentRoomId ? 'bg-white/15 text-white' : 'text-metal hover:text-mist'
            }`}
            onClick={() => dispatchCommand({ type: 'NAVIGATE_TO_ROOM', roomId, source: 'user' })}
          >
            {translate(locale, ROOM_LABEL_KEYS[roomId])}
          </button>
        ))}
      </nav>
      {reducedMotion ? <p className="sr-only">{translate(locale, 'a11y.reducedMotion')}</p> : null}
    </div>
  );
}
