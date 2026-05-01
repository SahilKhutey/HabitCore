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

import { useHaptics } from '../hooks/useHaptics';
import { Habit } from '../types/habit';

interface HabitCardProps {
  item: Habit;
  onComplete: (id: string) => void;
  onEdit?: (item: Habit) => void;
  onDelete?: (id: string) => void;
  onViewDetail?: (item: Habit) => void;
}


export const HabitCard: React.FC<HabitCardProps> = ({ item, onComplete, onEdit, onDelete, onViewDetail }) => {
  const [showXP, setShowXP] = useState(false);
  const { trigger } = useHaptics();
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: item.done ? 0.5 : 1,
  }));

  const handlePress = () => {
    if (item.done) return;
    
    // Tactile Feedback
    trigger('success');

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
            <Flame size={14} color={item.done ? COLORS.primary : COLORS.accent} />
            <Text style={[styles.streakText, { color: item.done ? COLORS.primary : COLORS.accent }]}>
              {item.streak?.current_streak || 0}
            </Text>
            <Info size={14} color={COLORS.surfaceLight} style={{ marginLeft: 8 }} />
          </View>
        </TouchableOpacity>
      </View>
      
      {!item.done && showXP && <FloatingXP amount={10} onAnimationComplete={() => setShowXP(false)} />}
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.surface,
    padding: 16,
    borderRadius: 20,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.glassBorder,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
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
    width: 28,
    height: 28,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: COLORS.surfaceLight,
    marginRight: 15,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
  checkboxActive: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(56, 189, 248, 0.1)',
  },
  cardText: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: '700',
    flex: 1,
  },
  completedTitle: {
    color: COLORS.textSecondary,
    textDecorationLine: 'line-through',
    opacity: 0.6,
  },
  streakBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.03)',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 14,
  },
  streakText: {
    fontSize: 14,
    fontWeight: '900',
    marginLeft: 6,
  },
  diffDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginTop: 6,
  }
});
