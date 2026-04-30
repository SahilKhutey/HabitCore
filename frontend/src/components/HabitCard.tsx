import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { Flame, CheckCircle2, Info } from 'lucide-react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withTiming, 
  Layout
} from 'react-native-reanimated';
import { COLORS } from '../theme/theme';
import { FloatingXP } from './FloatingXP';

interface HabitCardProps {
  item: {
    id: string;
    title: string;
    done: boolean;
    name?: string;
    streak?: { current_streak: number };
    difficulty?: string;
  };
  onComplete: (id: string) => void;
  onEdit?: (item: any) => void;
  onDelete?: (id: string) => void;
  onViewDetail?: (item: any) => void;
}

export const HabitCard: React.FC<HabitCardProps> = ({ item, onComplete, onEdit, onDelete, onViewDetail }) => {
  const [showXP, setShowXP] = useState(false);
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: item.done ? 0.5 : 1,
  }));

  const handlePress = () => {
    if (item.done) return;
    scale.value = withTiming(0.95, { duration: 100 }, () => {
      scale.value = withTiming(1);
    });
    setShowXP(true);
    onComplete(item.id);
  };

  const handleLongPress = () => {
    Alert.alert("Manage Habit", `What would you like to do with "${item.title || item.name}"?`, [
      { text: "Edit", onPress: () => onEdit?.(item) },
      { text: "Delete", onPress: () => onDelete?.(item.id), style: "destructive" },
      { text: "Cancel", style: "cancel" },
    ]);
  };

  const getDifficultyColor = () => {
    switch (item.difficulty) {
      case "easy": return "#4caf50";
      case "hard": return "#f44336";
      default: return "#ffeb3b";
    }
  };

  return (
    <Animated.View style={[styles.card, animatedStyle]} layout={Layout.springify()}>
      <View style={styles.content}>
        <TouchableOpacity 
          style={styles.mainAction} 
          onPress={handlePress}
          onLongPress={handleLongPress}
          disabled={item.done}
          activeOpacity={0.7}
        >
          <View style={[styles.checkbox, item.done && styles.checkboxActive]}>
            {item.done && <CheckCircle2 size={16} color="#00ffcc" />}
          </View>
          <View style={{ flex: 1 }}>
            <Text style={[styles.cardText, item.done && styles.completedTitle]} numberOfLines={1}>
              {item.title || item.name}
            </Text>
            {item.difficulty && (
               <View style={[styles.diffDot, { backgroundColor: getDifficultyColor() }]} />
            )}
          </View>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.detailAction}
          onPress={() => onViewDetail?.(item)}
          activeOpacity={0.7}
        >
          <View style={styles.streakBadge}>
            <Flame size={14} color={item.done ? "#00ffcc" : "#ff5500"} />
            <Text style={[styles.streakText, { color: item.done ? "#00ffcc" : "#ff5500" }]}>
              {item.streak?.current_streak || 0}
            </Text>
            <Info size={14} color="#444" style={{ marginLeft: 8 }} />
          </View>
        </TouchableOpacity>
      </View>
      
      {!item.done && showXP && <FloatingXP amount={10} onAnimationComplete={() => setShowXP(false)} />}
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#111",
    padding: 16,
    borderRadius: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  content: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  mainAction: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  detailAction: {
    paddingLeft: 12,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#333',
    marginRight: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkboxActive: {
    borderColor: '#00ffcc',
    backgroundColor: 'rgba(0, 255, 204, 0.1)',
  },
  cardText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
  },
  completedTitle: {
    color: '#444',
    textDecorationLine: 'line-through',
  },
  streakBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.03)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
  },
  streakText: {
    fontSize: 12,
    fontWeight: '800',
    marginLeft: 4,
  },
  diffDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginTop: 4,
  }
});
