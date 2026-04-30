import React from "react";
import { Pressable, StyleSheet } from "react-native";
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring, 
  withTiming 
} from "react-native-reanimated";

interface AnimatedButtonProps {
  children: React.ReactNode;
  onPress?: () => void;
  style?: any;
  disabled?: boolean;
}

export const AnimatedButton: React.FC<AnimatedButtonProps> = ({ 
  children, 
  onPress, 
  style,
  disabled 
}) => {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }]
  }));

  const onPressIn = () => {
    if (disabled) return;
    scale.value = withTiming(0.95, { duration: 100 });
  };

  const onPressOut = () => {
    if (disabled) return;
    scale.value = withSpring(1, { damping: 10, stiffness: 300 });
  };

  return (
    <Pressable
      onPress={onPress}
      onPressIn={onPressIn}
      onPressOut={onPressOut}
      disabled={disabled}
    >
      <Animated.View style={[style, animatedStyle]}>
        {children}
      </Animated.View>
    </Pressable>
  );
};
