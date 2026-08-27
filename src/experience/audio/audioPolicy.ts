export type AudioChannel = 'ambience' | 'ui' | 'voice';

export type AudioPolicy = {
  enabled: boolean;
  duckOnVoice: boolean;
};

export function resolveAudioPolicy(soundEnabled: boolean): AudioPolicy {
  return {
    enabled: soundEnabled,
    duckOnVoice: true,
  };
}
