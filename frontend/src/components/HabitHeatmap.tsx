import React, { useMemo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { COLORS, TYPOGRAPHY, SPACING } from '../theme/theme';

interface DayCell {
  date: string;
  count: number;
}

interface HabitHeatmapProps {
  data: Record<string, number>; // { '2024-04-01': 2, '2024-04-02': 0, ... }
  weeks?: number;
}

const WEEK_LABELS = ['Mon', 'Wed', 'Fri'];
const MONTH_LABELS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

function getCellColor(count: number): string {
  if (count === 0) return 'rgba(255,255,255,0.04)';
  if (count === 1) return 'rgba(51, 255, 214, 0.25)';
  if (count === 2) return 'rgba(51, 255, 214, 0.55)';
  return COLORS.primary; // 3+
}

export const HabitHeatmap: React.FC<HabitHeatmapProps> = ({ data = {}, weeks = 15 }) => {
  const cells = useMemo(() => {
    const today = new Date();
    const result: DayCell[][] = [];
    // Work backwards: weeks × 7 days
    const totalDays = weeks * 7;
    const start = new Date(today);
    start.setDate(start.getDate() - totalDays + 1);

    // Build week columns
    let currentWeek: DayCell[] = [];
    for (let i = 0; i < totalDays; i++) {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      const key = d.toISOString().split('T')[0];
      currentWeek.push({ date: key, count: data[key] || 0 });
      if (currentWeek.length === 7) {
        result.push(currentWeek);
        currentWeek = [];
      }
    }
    if (currentWeek.length > 0) result.push(currentWeek);
    return result;
  }, [data, weeks]);

  // Get month labels for header
  const monthLabels = useMemo(() => {
    const labels: { label: string; col: number }[] = [];
    let lastMonth = -1;
    cells.forEach((week, i) => {
      const month = new Date(week[0].date).getMonth();
      if (month !== lastMonth) {
        labels.push({ label: MONTH_LABELS[month], col: i });
        lastMonth = month;
      }
    });
    return labels;
  }, [cells]);

  const totalCompletions = useMemo(() =>
    Object.values(data).reduce((sum, v) => sum + v, 0), [data]);

  const activeDays = useMemo(() =>
    Object.values(data).filter(v => v > 0).length, [data]);

  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>ACTIVITY MAP</Text>
        <View style={styles.legend}>
          {[0, 1, 2, 3].map(v => (
            <View key={v} style={[styles.legendCell, { backgroundColor: getCellColor(v) }]} />
          ))}
          <Text style={styles.legendText}>Less → More</Text>
        </View>
      </View>

      {/* Stats row */}
      <View style={styles.statsRow}>
        <View style={styles.statItem}>
          <Text style={styles.statNum}>{totalCompletions}</Text>
          <Text style={styles.statLabel}>Total</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNum}>{activeDays}</Text>
          <Text style={styles.statLabel}>Active Days</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNum}>
            {activeDays > 0 ? Math.round((activeDays / (weeks * 7)) * 100) : 0}%
          </Text>
          <Text style={styles.statLabel}>Consistency</Text>
        </View>
      </View>

      {/* Month labels */}
      <View style={styles.monthRow}>
        {monthLabels.map(({ label, col }) => (
          <Text
            key={`${label}-${col}`}
            style={[styles.monthLabel, { marginLeft: col === 0 ? 0 : col * 13 }]}
          >
            {label}
          </Text>
        ))}
      </View>

      {/* Grid */}
      <View style={styles.grid}>
        {/* Day-of-week labels */}
        <View style={styles.dayLabels}>
          {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => (
            <Text key={i} style={styles.dayLabel}>{d}</Text>
          ))}
        </View>

        {/* Week columns */}
        <View style={styles.weekColumns}>
          {cells.map((week, wi) => (
            <View key={wi} style={styles.weekColumn}>
              {week.map((cell, di) => (
                <View
                  key={cell.date}
                  style={[
                    styles.cell,
                    { backgroundColor: getCellColor(cell.count) },
                    cell.count > 0 && styles.cellActive,
                  ]}
                />
              ))}
            </View>
          ))}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 16,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textDim,
    letterSpacing: 2,
  },
  legend: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  legendCell: {
    width: 10,
    height: 10,
    borderRadius: 2,
  },
  legendText: {
    ...TYPOGRAPHY.caption,
    fontSize: 9,
    color: COLORS.textDim,
    marginLeft: 4,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 14,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  statItem: {
    alignItems: 'center',
  },
  statNum: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 20,
    color: COLORS.primary,
  },
  statLabel: {
    ...TYPOGRAPHY.caption,
    fontSize: 10,
    color: COLORS.textDim,
    marginTop: 2,
  },
  monthRow: {
    flexDirection: 'row',
    marginLeft: 22,
    marginBottom: 4,
    height: 14,
    position: 'relative',
  },
  monthLabel: {
    ...TYPOGRAPHY.caption,
    fontSize: 9,
    color: COLORS.textSecondary,
    position: 'absolute',
  },
  grid: {
    flexDirection: 'row',
  },
  dayLabels: {
    width: 16,
    marginRight: 4,
  },
  dayLabel: {
    height: 11,
    fontSize: 8,
    fontFamily: 'SpaceGrotesk_500Medium',
    color: COLORS.textDim,
    lineHeight: 11,
    marginBottom: 2,
  },
  weekColumns: {
    flexDirection: 'row',
    flex: 1,
    gap: 2,
  },
  weekColumn: {
    flex: 1,
    gap: 2,
  },
  cell: {
    flex: 1,
    aspectRatio: 1,
    borderRadius: 2,
    maxHeight: 11,
  },
  cellActive: {
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowRadius: 3,
    shadowOpacity: 0.4,
    elevation: 2,
  },
});
