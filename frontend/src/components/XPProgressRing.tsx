import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { Circle, Defs, LinearGradient, Stop } from 'react-native-svg';
import Animated, { useAnimatedProps, withTiming } from 'react-native-reanimated';
import { COLORS, TYPOGRAPHY } from '../theme/theme';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

interface XPProgressRingProps {
  progress: number; // 0 to 1
  size?: number;
  strokeWidth?: number;
  showPercentage?: boolean;
}

export default function XPProgressRing({ 
  progress, 
  size = 120, 
  strokeWidth = 10,
  showPercentage = true 
}: XPProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  
  const animatedProps = useAnimatedProps(() => ({
    strokeDashoffset: withTiming(circumference * (1 - progress), { duration: 1500 })
  }));

  return (
    <View style={[styles.container, { width: size, height: size }]}>
      <View style={[styles.glow, { width: size, height: size, borderRadius: size / 2 }]} />
      <Svg width={size} height={size}>
        <Defs>
          <LinearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <Stop offset="0%" stopColor={COLORS.primaryGradient[0]} />
            <Stop offset="100%" stopColor={COLORS.primaryGradient[1]} />
          </LinearGradient>
        </Defs>
        
        {/* Background circle */}
        <Circle
          stroke="rgba(255, 255, 255, 0.05)"
          fill="none"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />
        
        {/* Progress circle */}
        <AnimatedCircle
          stroke="url(#grad)"
          fill="none"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          animatedProps={animatedProps}
          strokeLinecap="round"
          rotation="-90"
          origin={`${size / 2}, ${size / 2}`}
        />
      </Svg>
      
      {showPercentage && (
        <View style={styles.textContainer}>
          <Text style={[styles.percentageText]}>
            {Math.round(progress * 100)}%
          </Text>
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
    backgroundColor: COLORS.primary,
    opacity: 0.1,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.4,
    shadowRadius: 20,
  },
  textContainer: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  percentageText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 20,
    color: COLORS.primary,
  }
});
