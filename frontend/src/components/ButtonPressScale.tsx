import React from 'react';
import { TouchableOpacity, TouchableOpacityProps } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring 
} from 'react-native-reanimated';

const AnimatedTouchable = Animated.createAnimatedComponent(TouchableOpacity);

interface ButtonPressScaleProps extends TouchableOpacityProps {
  children: React.ReactNode;
  scaleTo?: number;
}

export default function ButtonPressScale({ 
  children, 
  scaleTo = 0.95,
  onPressIn,
  onPressOut,
  ...props 
}: ButtonPressScaleProps) {
  const scale = useSharedValue(1);

  const handlePressIn = (e: any) => {
    scale.value = withSpring(scaleTo, { damping: 15 });
    onPressIn?.(e);
  };

  const handlePressOut = (e: any) => {
    scale.value = withSpring(1, { damping: 15 });
    onPressOut?.(e);
  };

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }]
  }));

  return (
    <AnimatedTouchable
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      style={[animatedStyle]}
      {...props}
    >
      {children}
    </AnimatedTouchable>
  );
}
