import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';
import { GlassCard } from './GlassCard';
import { Target, Eye, Zap, ShieldCheck } from 'lucide-react-native';
import { MotiView } from 'moti';

interface JourneyPhaseCardProps {
  phase: string;
  day: number;
  label: string;
}

export const JourneyPhaseCard = ({ phase, day, label }: JourneyPhaseCardProps) => {
  const getPhaseConfig = () => {
    switch (phase.toLowerCase()) {
      case 'hook':
        return {
          title: 'PHASE 1: HOOK',
          desc: 'Building the neurological association between action and reward.',
          icon: <Zap size={20} color={COLORS.secondary} />,
          color: COLORS.secondary,
        };
      case 'awareness':
        return {
          title: 'PHASE 2: AWARENESS',
          desc: 'Identifying subconscious patterns and friction points.',
          icon: <Eye size={20} color={COLORS.primary} />,
          color: COLORS.primary,
        };
      case 'intervention':
        return {
          title: 'PHASE 3: INTERVENTION',
          desc: 'Actively disrupting negative loops with high-agency choices.',
          icon: <Target size={20} color={COLORS.gold} />,
          color: COLORS.gold,
        };
      case 'identity':
        return {
          title: 'PHASE 4: IDENTITY',
          desc: 'Consistency has solidified into a new version of yourself.',
          icon: <ShieldCheck size={20} color="#f472b6" />,
          color: '#f472b6',
        };
      default:
        return {
          title: 'CALIBRATING',
          desc: 'The intelligence engine is mapping your behavioral baseline.',
          icon: <Zap size={20} color={COLORS.textDim} />,
          color: COLORS.textDim,
        };
    }
  };

  const config = getPhaseConfig();

  return (
    <MotiView
      from={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring' }}
    >
      <GlassCard style={[styles.card, { borderColor: `${config.color}30` }]}>
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            {config.icon}
            <Text style={[styles.phaseTitle, { color: config.color }]}>{config.title}</Text>
          </View>
          <View style={styles.dayBadge}>
            <Text style={styles.dayText}>DAY {day}</Text>
          </View>
        </View>
        
        <Text style={styles.label}>{label}</Text>
        <Text style={styles.desc}>{config.desc}</Text>

        <View style={styles.progressContainer}>
          <View style={styles.progressBarBg}>
            <View style={[styles.progressBarFill, { width: `${(day / 30) * 100}%`, backgroundColor: config.color }]} />
          </View>
          <Text style={styles.progressText}>30-Day Journey Progress</Text>
        </View>
      </GlassCard>
    </MotiView>
  );
};

const styles = StyleSheet.create({
  card: {
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
    borderWidth: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  phaseTitle: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 12,
    letterSpacing: 2,
  },
  dayBadge: {
    backgroundColor: 'rgba(255,255,255,0.06)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  dayText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 10,
    color: COLORS.text,
  },
  label: {
    fontFamily: 'SpaceGrotesk_600SemiBold',
    fontSize: 18,
    color: COLORS.text,
    marginBottom: 6,
  },
  desc: {
    fontFamily: 'SpaceGrotesk_400Regular',
    fontSize: 13,
    color: COLORS.textSecondary,
    lineHeight: 18,
    marginBottom: 16,
  },
  progressContainer: {
    marginTop: 4,
  },
  progressBarBg: {
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderRadius: 2,
    overflow: 'hidden',
    marginBottom: 6,
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 2,
  },
  progressText: {
    fontFamily: 'SpaceGrotesk_500Medium',
    fontSize: 9,
    color: COLORS.textDim,
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
});
