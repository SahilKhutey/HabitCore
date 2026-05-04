import React, { useState, useEffect, useCallback } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  RefreshControl, 
  SafeAreaView,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator
} from 'react-native';
import { useRouter } from 'expo-router';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS, SHADOWS } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { Brain, Activity, ChevronRight, Sparkles, Check, Flame, Zap } from 'lucide-react-native';
import { MotiView, AnimatePresence } from 'moti';
import { triggerHaptic } from '../../src/utils/animationManager';

const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);
  const [journeySummary, setJourneySummary] = useState<any>(null);
  const [habits, setHabits] = useState<any[]>([]);
  const [patterns, setPatterns] = useState<any>(null);
  const { token, email, setUserInfo, level, xp, coins } = useUserStore();
  
  const userName = email ? email.split('@')[0] : 'Sahil';

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [journey, patternRes, habitRes] = await Promise.all([
        api('/identity/summary', 'GET', null, token),
        api('/psychological/behavior/patterns', 'GET', null, token),
        api('/habits/today/status', 'GET', null, token),
      ]);
      setJourneySummary(journey);
      setPatterns(patternRes);
      setHabits(habitRes?.habits || []);
      
      // Update global store if needed
      const stateRes = await api('/habits/state', 'GET', null, token);
      if (stateRes?.user_state) {
        setUserInfo({
          level: stateRes.user_state.level,
          xp: stateRes.user_state.xp,
          coins: stateRes.user_state.coins || 0
        });
      }
    } catch (e) { console.error('Fetch error:', e); }
  }, [token, setUserInfo]);

  useEffect(() => {
    if (token) fetchData();
  }, [token, fetchData]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const handleCompleteHabit = async (habitId: string) => {
    try {
      triggerHaptic('success');
      const res = await api('/habits/complete', 'POST', { habit_id: habitId }, token!);
      if (res.success) {
        // Refresh habits list and state
        fetchData();
      }
    } catch (e) {
      triggerHaptic('error');
      console.error(e);
    }
  };

  const handleStartCheckin = () => {
    triggerHaptic('impactLight');
    router.push('/reflection' as any);
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const IdentityPulseBar = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <View style={styles.pulseRow}>
      <View style={styles.pulseHeader}>
        <Text style={styles.pulseLabel}>{label}</Text>
        <Text style={styles.pulsePercentage}>{Math.round(value * 100)}%</Text>
      </View>
      <View style={styles.pulseBarBg}>
        <MotiView 
          from={{ width: 0 }}
          animate={{ width: `${value * 100}%` }}
          transition={{ type: 'spring', damping: 20 }}
          style={[styles.pulseBarFill, { backgroundColor: color }]} 
        />
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView 
        style={styles.container} 
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />
        }
      >
        {/* Header Section */}
        <MotiView 
          from={{ opacity: 0, translateY: -20 }}
          animate={{ opacity: 1, translateY: 0 }}
          style={styles.header}
        >
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.greeting}>{getGreeting()}, {userName}</Text>
              <Text style={styles.insightHighlight}>
                {journeySummary?.instant_insight || "Observe your resistance without judgment."}
              </Text>
            </View>
            <TouchableOpacity style={styles.statsBadge} onPress={() => router.push('/(tabs)/profile')}>
               <Zap size={14} color={COLORS.primary} />
               <Text style={styles.statsBadgeText}>{level}</Text>
            </TouchableOpacity>
          </View>
        </MotiView>

        {/* Action Card */}
        <TouchableOpacity 
          activeOpacity={0.9}
          onPress={handleStartCheckin}
          style={styles.ctaWrapper}
        >
          <MotiView 
            animate={{ scale: 1 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            style={styles.ctaCard}
          >
            <View style={styles.ctaIconBg}>
              <Sparkles color={COLORS.primary} size={24} />
            </View>
            <View style={styles.ctaContent}>
              <Text style={styles.ctaTitle}>Today's Reflection</Text>
              <Text style={styles.ctaSubtitle}>Takes less than 1 minute</Text>
            </View>
            <ChevronRight color={COLORS.textDim} size={20} />
          </MotiView>
        </TouchableOpacity>

        {/* Habits Section */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>Actions for Today</Text>
          {habits.length === 0 ? (
            <GlassCard style={styles.emptyCard}>
              <Text style={styles.emptyText}>No actions defined for today.</Text>
              <TouchableOpacity onPress={() => router.push('/(tabs)/studio')}>
                <Text style={styles.emptyCta}>Define actions in Studio</Text>
              </TouchableOpacity>
            </GlassCard>
          ) : (
            habits.map((habit, i) => (
              <MotiView 
                key={habit.id}
                from={{ opacity: 0, translateX: -10 }}
                animate={{ opacity: 1, translateX: 0 }}
                transition={{ delay: i * 100 }}
              >
                <GlassCard style={styles.habitCard}>
                  <View style={styles.habitMain}>
                    <Text style={[styles.habitName, habit.completed && styles.habitNameCompleted]}>
                      {habit.name}
                    </Text>
                    <Text style={styles.habitTime}>{habit.time || 'Anytime'}</Text>
                  </View>
                  <TouchableOpacity 
                    style={[styles.checkCircle, habit.completed && styles.checkCircleCompleted]}
                    onPress={() => !habit.completed && handleCompleteHabit(habit.id)}
                    disabled={habit.completed}
                  >
                    {habit.completed && <Check size={16} color="#fff" />}
                  </TouchableOpacity>
                </GlassCard>
              </MotiView>
            ))
          )}
        </View>

        {/* Stats Grid */}
        <View style={styles.statsSection}>
          <Text style={styles.sectionLabel}>Identity Pulse</Text>
          <GlassCard style={styles.pulseCard}>
            <IdentityPulseBar 
              label="Discipline" 
              value={(journeySummary?.discipline_score || 30) / 100} 
              color={COLORS.identity.discipline} 
            />
            <IdentityPulseBar 
              label="Awareness" 
              value={0.8} 
              color={COLORS.identity.awareness} 
            />
            <IdentityPulseBar 
              label="Avoidance" 
              value={patterns?.burnout_score || 0.2} 
              color={COLORS.identity.avoidance} 
            />
          </GlassCard>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  content: { padding: SPACING[5], paddingBottom: SPACING[12] },
  header: { marginBottom: SPACING[10] },
  headerTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  greeting: { 
    ...TYPOGRAPHY.caption, 
    color: COLORS.textSecondary, 
    textTransform: 'uppercase',
    letterSpacing: 1.5,
    marginBottom: SPACING[2]
  },
  insightHighlight: { 
    ...TYPOGRAPHY.h1, 
    color: COLORS.text, 
    lineHeight: 42,
    letterSpacing: -0.5,
    maxWidth: width * 0.75
  },
  statsBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: 'rgba(124, 140, 255, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: RADIUS.full,
    borderWidth: 1,
    borderColor: 'rgba(124, 140, 255, 0.2)'
  },
  statsBadgeText: { ...TYPOGRAPHY.label, color: COLORS.primary, fontSize: 12 },
  ctaWrapper: { marginBottom: SPACING[8] },
  ctaCard: {
    backgroundColor: COLORS.surface,
    borderRadius: RADIUS.xl,
    padding: SPACING[5],
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
    ...SHADOWS.card
  },
  ctaIconBg: {
    width: 48,
    height: 48,
    borderRadius: RADIUS.lg,
    backgroundColor: 'rgba(124, 140, 255, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: SPACING[4]
  },
  ctaContent: { flex: 1 },
  ctaTitle: { ...TYPOGRAPHY.h3, color: COLORS.text },
  ctaSubtitle: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 2 },
  
  section: { marginBottom: SPACING[8] },
  sectionLabel: { 
    ...TYPOGRAPHY.label, 
    color: COLORS.textDim, 
    fontSize: 10, 
    marginBottom: SPACING[3],
    letterSpacing: 2
  },
  habitCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: SPACING[4],
    borderRadius: RADIUS.lg,
    marginBottom: SPACING[3],
    backgroundColor: COLORS.surface
  },
  habitMain: { flex: 1 },
  habitName: { ...TYPOGRAPHY.h3, fontSize: 16, color: COLORS.text },
  habitNameCompleted: { color: COLORS.textDim, textDecorationLine: 'line-through' },
  habitTime: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 2 },
  checkCircle: {
    width: 28,
    height: 28,
    borderRadius: 14,
    borderWidth: 2,
    borderColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center'
  },
  checkCircleCompleted: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary
  },
  emptyCard: { padding: SPACING[6], alignItems: 'center', gap: SPACING[2] },
  emptyText: { ...TYPOGRAPHY.body, color: COLORS.textDim, textAlign: 'center' },
  emptyCta: { ...TYPOGRAPHY.label, color: COLORS.primary, fontSize: 12, marginTop: 4 },

  statsSection: { marginBottom: SPACING[8] },
  pulseCard: {
    padding: SPACING[6],
    borderRadius: RADIUS.xl,
    gap: SPACING[6]
  },
  pulseRow: { gap: SPACING[2] },
  pulseHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  pulseLabel: { ...TYPOGRAPHY.caption, color: COLORS.textSecondary, fontSize: 13 },
  pulsePercentage: { ...TYPOGRAPHY.caption, color: COLORS.text, fontWeight: '600' },
  pulseBarBg: { 
    height: 6, 
    backgroundColor: 'rgba(255,255,255,0.03)', 
    borderRadius: RADIUS.full, 
    overflow: 'hidden' 
  },
  pulseBarFill: { height: '100%', borderRadius: RADIUS.full },
});
