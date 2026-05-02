import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { MotiView } from 'moti';
import { COLORS, TYPOGRAPHY, SPACING } from '../theme/theme';

interface CheckinDay {
  date: string;
  mood: string;
  mood_score: number;
  energy_morning?: string;
  sleep_quality?: number;
}

interface Props {
  data: CheckinDay[];
  days?: number;
}

const MOOD_COLORS: Record<string, string> = {
  happy: COLORS.primary,
  excited: COLORS.primary,
  neutral: '#64748b',
  tired: COLORS.gold,
  sad: '#38bdf8',
  angry: '#f87171',
};

const MOOD_EMOJIS: Record<string, string> = {
  happy: '😊', excited: '🤩', neutral: '😐', tired: '😴', sad: '😢', angry: '😤',
};

const DAY_LABELS = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

export default function MoodChart({ data, days = 7 }: Props) {
  // Build last `days` slots aligned to calendar
  const slots: (CheckinDay | null)[] = [];
  const today = new Date();

  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    const iso = d.toISOString().split('T')[0];
    const found = data.find(c => c.date === iso);
    slots.push(found || null);
  }

  const maxScore = 5;

  return (
    <View style={styles.container}>
      <View style={styles.bars}>
        {slots.map((slot, i) => {
          const score = slot?.mood_score ?? 0;
          const fillPct = (score / maxScore) * 100;
          const color = slot ? (MOOD_COLORS[slot.mood] || COLORS.primary) : 'rgba(255,255,255,0.05)';
          const d = new Date(today);
          d.setDate(today.getDate() - (days - 1 - i));
          const dayLabel = DAY_LABELS[d.getDay()];

          return (
            <View key={i} style={styles.barCol}>
              {/* Emoji */}
              <Text style={styles.emoji}>
                {slot ? (MOOD_EMOJIS[slot.mood] || '•') : ''}
              </Text>
              {/* Bar track */}
              <View style={styles.barTrack}>
                <MotiView
                  from={{ height: 0 }}
                  animate={{ height: Math.max(Math.round((Math.max(fillPct, slot ? 8 : 0) / 100) * 80), slot ? 4 : 0) }}
                  transition={{ type: 'spring', duration: 800, delay: i * 60 }}
                  style={[styles.barFill, { backgroundColor: color }]}
                />
              </View>
              {/* Day label */}
              <Text style={[styles.dayLabel, slot && styles.dayLabelActive]}>{dayLabel}</Text>
            </View>
          );
        })}
      </View>

      {/* Legend */}
      <View style={styles.legend}>
        {[
          { emoji: '😊', label: 'Happy', color: COLORS.primary },
          { emoji: '😐', label: 'Neutral', color: '#64748b' },
          { emoji: '😴', label: 'Tired', color: COLORS.gold },
          { emoji: '😢', label: 'Low', color: '#38bdf8' },
        ].map((l) => (
          <View key={l.label} style={styles.legendItem}>
            <Text style={styles.legendEmoji}>{l.emoji}</Text>
            <Text style={[styles.legendLabel, { color: l.color }]}>{l.label}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { paddingVertical: SPACING.md },
  bars: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 8,
    height: 120,
    paddingHorizontal: 4,
  },
  barCol: {
    flex: 1,
    alignItems: 'center',
    height: '100%',
    justifyContent: 'flex-end',
  },
  emoji: { fontSize: 14, marginBottom: 4 },
  barTrack: {
    width: '70%',
    height: 80,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 6,
    justifyContent: 'flex-end',
    overflow: 'hidden',
  },
  barFill: {
    width: '100%',
    borderRadius: 6,
    minHeight: 4,
  },
  dayLabel: {
    fontFamily: 'SpaceGrotesk_500Medium',
    fontSize: 10,
    color: COLORS.textDim,
    marginTop: 6,
  },
  dayLabelActive: { color: COLORS.textSecondary },
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 16,
    marginTop: 12,
    flexWrap: 'wrap',
  },
  legendItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  legendEmoji: { fontSize: 12 },
  legendLabel: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 10 },
});
