import React, { useEffect } from "react";
import { StyleSheet, Text } from "react-native";
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withTiming, 
  withSequence, 
  withDelay,
  runOnJS
} from "react-native-reanimated";

interface RewardPopupProps {
  text: string;
  onComplete: () => void;
  color?: string;
}

export const RewardPopup: React.FC<RewardPopupProps> = ({ text, onComplete, color = "#00ffcc" }) => {
  const opacity = useSharedValue(0);
  const translateY = useSharedValue(0);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateY: translateY.value }]
  }));

  useEffect(() => {
    opacity.value = withSequence(
      withTiming(1, { duration: 200 }),
      withDelay(1000, withTiming(0, { duration: 500 }, (finished) => {
        if (finished) runOnJS(onComplete)();
      }))
    );
    translateY.value = withTiming(-50, { duration: 1500 });
  }, []);

  return (
    <Animated.View style={[styles.container, animatedStyle]}>
      <Text style={[styles.text, { color }]}>{text}</Text>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    alignSelf: "center",
    top: "40%",
    zIndex: 1000,
  },
  text: {
    fontSize: 24,
    fontWeight: "900",
    textShadowColor: "rgba(0,0,0,0.5)",
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  }
});
