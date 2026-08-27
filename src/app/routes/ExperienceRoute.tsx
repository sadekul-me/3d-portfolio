import { lazy, Suspense, useEffect } from 'react';
import { Navigate, useNavigate, useParams } from 'react-router-dom';

import { isRoomId } from '@/types/ids';
import { detectWebGL } from '@/app/bootstrap/detectCapabilities';
import { dispatchCommand } from '@/app/commands/dispatcher';
import { FALLBACK_ROOM_ID } from '@/navigation/graph/resolvePath';
import { useAppStore } from '@/store/appStore';
import { translate } from '@/i18n/translate';
import { decideExperienceMode } from '@/experience/fallback/fallbackPolicy';

const ExperienceApp = lazy(() => import('@/experience/ExperienceApp'));

export function ExperienceRoute() {
  const params = useParams();
  const navigate = useNavigate();
  const locale = useAppStore((state) => state.preferences.locale);
  const override = useAppStore((state) => state.preferences.experienceModeOverride);
  const reducedMotion = useAppStore((state) => state.preferences.reducedMotion);
  const roomParam = params['roomId'];
  const webgl = detectWebGL();
  const fallbackInput = {
    webgl: webgl.webgl,
    contextLost: false,
    reducedMotion,
    ...(override ? { userOverride: override } : {}),
  };
  const mode = decideExperienceMode(fallbackInput);

  useEffect(() => {
    if (roomParam && isRoomId(roomParam)) {
      dispatchCommand({ type: 'NAVIGATE_TO_ROOM', roomId: roomParam, source: 'user' });
    }
    if (roomParam && !isRoomId(roomParam)) {
      void navigate(`/experience/${FALLBACK_ROOM_ID}`, { replace: true });
    }
  }, [roomParam, navigate]);

  if (mode === 'QUICK_PORTFOLIO' || mode === 'STATIC_CORE' || !webgl.webgl) {
    return <Navigate to="/portfolio" replace />;
  }

  if (roomParam && !isRoomId(roomParam)) {
    return <p className="px-6 py-10 text-metal">{translate(locale, 'errors.navigationInvalid')}</p>;
  }

  return (
    <Suspense
      fallback={<p className="px-6 py-10 text-metal">{translate(locale, 'experience.loading')}</p>}
    >
      <ExperienceApp />
    </Suspense>
  );
}
