import { Audio } from 'expo-av';
import * as Haptics from 'expo-haptics';

class SoundEngine {
  private sounds: Record<string, Audio.Sound> = {};
  private isMuted: boolean = false;

  async initialize() {
    try {
      await Audio.setAudioModeAsync({
        playsInSilentModeIOS: true,
        staysActiveInBackground: false,
      });

      // Preload all sounds
      // Note: Assumes assets exist. Wrapped in try/catch to prevent crashes if files are missing.
      await this.loadSound('click', require('../../assets/sounds/click.mp3'));
      await this.loadSound('reward', require('../../assets/sounds/reward.mp3'));
      await this.loadSound('coin', require('../../assets/sounds/coin.mp3'));
      await this.loadSound('combo', require('../../assets/sounds/combo.mp3'));
      await this.loadSound('reveal', require('../../assets/sounds/reveal.mp3'));
      await this.loadSound('level_up', require('../../assets/sounds/level_up.mp3'));
      await this.loadSound('streak', require('../../assets/sounds/streak.mp3'));
      
      console.log('Sound engine initialized');
    } catch (error) {
      console.error('Failed to initialize sound engine:', error);
    }
  }

  private async loadSound(name: string, source: any) {
    try {
      const { sound } = await Audio.Sound.createAsync(source, { 
        volume: 0.7,
        shouldPlay: false 
      });
      this.sounds[name] = sound;
    } catch (error) {
      console.warn(`Failed to load sound ${name}: ${(error as any).message}`);
    }
  }

  async play(name: string, options: { volume?: number; haptic?: boolean } = {}) {
    if (this.isMuted) return;

    const sound = this.sounds[name];
    if (sound) {
      try {
        await sound.setVolumeAsync(options.volume ?? 0.7);
        await sound.replayAsync();
      } catch (error) {
        console.warn(`Failed to play sound ${name}:`, error);
      }
    }

    // Always attempt haptic if requested, even if sound fails or is muted
    if (options.haptic !== false) {
      this.playHaptic(name);
    }
  }

  private playHaptic(soundName: string) {
    const hapticMap: Record<string, Haptics.ImpactFeedbackStyle | Haptics.NotificationFeedbackType> = {
      click: Haptics.ImpactFeedbackStyle.Light,
      coin: Haptics.ImpactFeedbackStyle.Medium,
      reward: Haptics.ImpactFeedbackStyle.Heavy,
      combo: Haptics.ImpactFeedbackStyle.Heavy,
      reveal: Haptics.NotificationFeedbackType.Success,
      level_up: Haptics.NotificationFeedbackType.Success,
      streak: Haptics.NotificationFeedbackType.Warning,
    };

    const hapticType = hapticMap[soundName];
    if (hapticType === undefined) return;

    if (Object.values(Haptics.ImpactFeedbackStyle).includes(hapticType as Haptics.ImpactFeedbackStyle)) {
      Haptics.impactAsync(hapticType as Haptics.ImpactFeedbackStyle);
    } else {
      Haptics.notificationAsync(hapticType as Haptics.NotificationFeedbackType);
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    return this.isMuted;
  }

  async dispose() {
    await Promise.all(
      Object.values(this.sounds).map(sound => sound.unloadAsync())
    );
    this.sounds = {};
  }
}

export const soundEngine = new SoundEngine();
