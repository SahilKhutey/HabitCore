import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
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
  strokeWidth = 8,
  showPercentage = true 
}: XPProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  
  const animatedProps = useAnimatedProps(() => ({
    strokeDashoffset: withTiming(circumference * (1 - progress), { duration: 1200 })
  }));

  return (
    <View style={[styles.container, { width: size, height: size }]}>
      <Svg width={size} height={size}>
        {/* Background circle */}
        <Circle
          stroke={COLORS.card}
          fill="none"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />
        
        {/* Progress circle */}
        <AnimatedCircle
          stroke={COLORS.primary}
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
          <Text style={[TYPOGRAPHY.h2, styles.percentageText]}>
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
  },
  textContainer: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  percentageText: {
    color: COLORS.primary,
    fontWeight: 'bold',
  }
});
