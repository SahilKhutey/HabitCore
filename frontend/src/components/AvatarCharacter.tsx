import React from 'react';
import { View, Image, Text, StyleSheet } from 'react-native';
import Animated, { 
  useAnimatedStyle, 
  withTiming,
  withSequence,
  withDelay 
} from 'react-native-reanimated';
import { COLORS, TYPOGRAPHY } from '../theme/theme';

interface AvatarCharacterProps {
  avatar?: {
    archetype: string;
    evolution_stage: number;
    appearance: {
      skin: string;
      outfit: string;
      aura: string;
      accessory: string;
      emote: string;
    }
  };
  size?: number;
  showLevel?: boolean;
  animate?: boolean;
}

export default function AvatarCharacter({ 
  avatar, 
  size = 120, 
  showLevel = true,
  animate = false 
}: AvatarCharacterProps) {
  const animatedScale = useAnimatedStyle(() => ({
    transform: [
      { 
        scale: animate ? withSequence(
          withTiming(1.2, { duration: 300 }),
          withTiming(1, { duration: 200 })
        ) : 1 
      }
    ]
  }));

  // Fallback data if avatar is missing
  const data = avatar || {
    archetype: 'beginner',
    evolution_stage: 1,
    appearance: {
      skin: 'default',
      outfit: 'basic',
      aura: 'none',
      accessory: 'none',
      emote: 'default'
    }
  };

  const getAssetPath = (type: string, value: string) => {
    // In production, these would be real asset paths or URLs
    // Using a mock return for now as the actual files don't exist
    return { uri: `https://habitcore.app/assets/avatar/${type}/${value}.png` };
  };

  const getEvolutionGlow = (stage: number) => {
    const glowColors: Record<number, string> = {
      1: 'rgba(0, 255, 204, 0.3)',
      2: 'rgba(0, 200, 255, 0.4)',
      3: 'rgba(148, 0, 255, 0.5)',
      4: 'rgba(255, 215, 0, 0.6)',
      5: 'rgba(255, 50, 50, 0.7)'
    };
    return glowColors[stage] || glowColors[1];
  };

  return (
    <View style={[styles.container, { width: size, height: size }]}>
      {/* Aura/Glow Effect */}
      {data.appearance.aura !== 'none' && (
        <Animated.View
          style={[
            styles.glow,
            { 
              backgroundColor: getEvolutionGlow(data.evolution_stage),
              width: size * 1.5,
              height: size * 1.5,
              borderRadius: size * 0.75
            }
          ]}
        />
      )}

      {/* Avatar Image Layering */}
      <Animated.View style={[styles.avatarContainer, animatedScale]}>
        {/* Base Archetype */}
        <Image
          source={getAssetPath('archetypes', data.archetype)}
          style={[styles.avatar, { width: size, height: size }]}
          resizeMode="contain"
        />
        
        {/* Outfit Layer */}
        {data.appearance.outfit !== 'basic' && (
          <Image
            source={getAssetPath('outfits', data.appearance.outfit)}
            style={[styles.layer, { width: size, height: size }]}
            resizeMode="contain"
          />
        )}
        
        {/* Accessory Layer */}
        {data.appearance.accessory !== 'none' && (
          <Image
            source={getAssetPath('accessories', data.appearance.accessory)}
            style={[styles.layer, { width: size, height: size }]}
            resizeMode="contain"
          />
        )}
      </Animated.View>

      {/* Level Badge */}
      {showLevel && (
        <View style={styles.levelBadge}>
          <Text style={styles.levelText}>Lv. {data.evolution_stage}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  glow: {
    position: 'absolute',
    opacity: 0.6,
  },
  avatarContainer: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatar: {
    position: 'absolute',
  },
  layer: {
    position: 'absolute',
  },
  levelBadge: {
    position: 'absolute',
    bottom: -10,
    backgroundColor: COLORS.primary,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: COLORS.bg,
    zIndex: 10,
  },
  levelText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.bg,
    fontWeight: 'bold',
    fontSize: 12,
  }
});
