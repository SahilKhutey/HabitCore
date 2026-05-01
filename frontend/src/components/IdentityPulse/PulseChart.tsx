import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withRepeat, 
  withTiming, 
  withSequence,
  interpolateColor
} from 'react-native-reanimated';
import { Activity } from 'lucide-react-native';

interface PulseChartProps {
  score: number;
  goal: string;
  status: string;
}

const PulseChart = ({ score, goal, status }: PulseChartProps) => {
  const pulse = useSharedValue(1);

  useEffect(() => {
    // Pulse faster if score is high
    const duration = Math.max(500, 2000 - (score * 15));
    pulse.value = withRepeat(
      withSequence(
        withTiming(1.2, { duration: duration / 2 }),
        withTiming(1, { duration: duration / 2 })
      ),
      -1,
      true
    );
  }, [score]);

  const animatedStyle = useAnimatedStyle(() => {
    const color = interpolateColor(
      score,
      [0, 50, 100],
      ['#FF3B30', '#FFCC00', '#00ffcc']
    );
    
    return {
      transform: [{ scale: pulse.value }],
      borderColor: color,
      shadowColor: color,
    };
  });

  return (
    <View style={styles.container}>
      <View style={styles.pulseWrapper}>
        <Animated.View style={[styles.pulseCircle, animatedStyle]}>
          <Activity color="#fff" size={40} />
        </Animated.View>
        <Text style={styles.scoreText}>{score}%</Text>
      </View>
      <View style={styles.info}>
        <Text style={styles.goalText}>Identity: {goal}</Text>
        <Text style={[styles.statusText, { color: score > 70 ? '#00ffcc' : '#FF3B30' }]}>
          {status}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#111',
    padding: 30,
    borderRadius: 24,
    alignItems: 'center',
    marginVertical: 20,
    borderWidth: 1,
    borderColor: '#222',
  },
  pulseWrapper: {
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20
  },
  pulseCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 4,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 15,
    elevation: 10
  },
  scoreText: {
    position: 'absolute',
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    bottom: -10,
    backgroundColor: '#000',
    paddingHorizontal: 8,
    borderRadius: 10
  },
  info: {
    alignItems: 'center'
  },
  goalText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  statusText: {
    fontSize: 14,
    marginTop: 4,
    textTransform: 'uppercase',
    letterSpacing: 1
  }
});

export default PulseChart;
