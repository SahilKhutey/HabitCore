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
  ActivityIndicator,
  TextInput
} from 'react-native';
import { useRouter } from 'expo-router';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS, SHADOWS } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { Brain, Activity, ChevronRight, Sparkles, Check, Flame, Zap, Plus, X } from 'lucide-react-native';
import { MotiView, AnimatePresence } from 'moti';
import { triggerHaptic } from '../../src/utils/animationManager';

const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);
  const [journeySummary, setJourneySummary] = useState<any>(null);
  const [habits, setHabits] = useState<any[]>([]);
  const [patterns, setPatterns] = useState<any>(null);
  const [userState, setUserState] = useState<any>({});
  const { token, email, setUserInfo, level, xp, coins } = useUserStore();
  
  const [showAddModal, setShowAddModal] = useState(false);
  const [newHabitName, setNewHabitName] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [conditionText, setConditionText] = useState('');
  const [freq, setFreq] = useState('7');
  const [streakTarget, setStreakTarget] = useState('30');
  const [domain, setDomain] = useState('mental');

  const userName = email ? email.split('@')[0] : 'Sahil';

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [journey, patternRes, habitRes, stateRes] = await Promise.all([
        api('/identity/summary', 'GET', null, token),
        api('/psychological/behavior/patterns', 'GET', null, token),
        api('/habits/today/status', 'GET', null, token),
        api('/habits/state', 'GET', null, token)
      ]);
      setJourneySummary(journey);
      setPatterns(patternRes);
      setHabits(habitRes?.habits || []);
      
      if (stateRes?.user_state) {
        setUserState(stateRes.user_state);
        setUserInfo({
          level: stateRes.user_state.level,
          xp: stateRes.user_state.xp,
          coins: stateRes.user_state.coins || 0
        });
      }
    } catch (e) { console.error('Fetch error:', e); }
  }, [token, setUserInfo]);

  const handleCreateHabit = async () => {
    if (!newHabitName) return;
    try {
      setRefreshing(true);
      const res = await api('/habits/create', 'POST', { 
        name: newHabitName,
        difficulty: difficulty,
        frequency: parseInt(freq),
        condition: conditionText,
        streak_target: parseInt(streakTarget),
        domain: domain
      }, token!);
      
      if (res.id) {
        triggerHaptic('success');
        setNewHabitName('');
        setConditionText('');
        setFreq('7');
        setStreakTarget('30');
        setShowAddModal(false);
        fetchData();
      }
    } catch (e) {
      console.error(e);
      triggerHaptic('error');
    } finally {
      setRefreshing(false);
    }
  };

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
            {...({
              whileHover: { scale: 1.02 },
              whileTap: { scale: 0.98 }
            } as any)}
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

        {/* Journey Progress */}
        <View style={styles.statsSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionLabel}>YOUR JOURNEY</Text>
            <TouchableOpacity onPress={() => router.push('/intelligence' as any)}>
              <Text style={styles.seeAll}>Full Analysis</Text>
            </TouchableOpacity>
          </View>
          <GlassCard style={styles.pulseCard}>
            <View style={styles.journeyHeader}>
              <View>
                <Text style={styles.archetypeTitle}>{userState.archetype || 'Seeker'}</Text>
                <Text style={styles.rankTitle}>{userState.identity_level || 'Beginner'}</Text>
              </View>
              <View style={styles.xpBox}>
                <Text style={styles.xpText}>{xp} / {level * 500} XP</Text>
              </View>
            </View>
            
            <View style={styles.progressBarBg}>
              <MotiView 
                from={{ width: 0 }}
                animate={{ width: `${(xp / (level * 500)) * 100}%` }}
                style={styles.progressBarFill}
              />
            </View>

            <Text style={styles.archetypeSubtext}>
              {userState.archetype === 'monk' ? 'Mastering the art of internal stillness and cognitive clarity.' : 
               userState.archetype === 'warrior' ? 'Forging a path of relentless discipline and physiological peak.' : 
               'Developing the foundations of behavioral mastery.'}
            </Text>

            <View style={styles.pulseGrid}>
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
            </View>
          </GlassCard>
        </View>

        {/* Routines & Journeys Preview */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>ACTIVE JOURNEYS</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.journeyScroll}>
            <GlassCard style={styles.journeyMiniCard}>
              <View style={styles.miniIconBg}><Sparkles size={16} color={COLORS.primary}/></View>
              <Text style={styles.miniTitle}>Morning Ritual</Text>
              <Text style={styles.miniStatus}>3/4 Complete</Text>
            </GlassCard>
            <GlassCard style={styles.journeyMiniCard}>
              <View style={[styles.miniIconBg, { backgroundColor: 'rgba(139, 164, 208, 0.1)' }]}><Brain size={16} color="#8BA4D0"/></View>
              <Text style={styles.miniTitle}>Deep Focus</Text>
              <Text style={styles.miniStatus}>Locked</Text>
            </GlassCard>
          </ScrollView>
        </View>
      </ScrollView>

      {/* Quick Add FAB */}
      <TouchableOpacity 
        style={styles.fab}
        onPress={() => setShowAddModal(true)}
      >
        <Plus size={24} color="#FFF" />
      </TouchableOpacity>

      {/* Add Habit Modal */}
      <AnimatePresence>
        {showAddModal && (
          <View style={styles.modalOverlay}>
            <MotiView 
              from={{ opacity: 0, scale: 0.9, translateY: 20 }}
              animate={{ opacity: 1, scale: 1, translateY: 0 }}
              exit={{ opacity: 0, scale: 0.9, translateY: 20 }}
              style={styles.modalCard}
            >
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>New Action</Text>
                <TouchableOpacity onPress={() => setShowAddModal(false)}>
                  <X size={20} color={COLORS.textDim} />
                </TouchableOpacity>
              </View>

              <TextInput 
                placeholder="What is the behavior?"
                placeholderTextColor={COLORS.textDim}
                style={styles.modalInput}
                value={newHabitName}
                onChangeText={setNewHabitName}
                autoFocus
              />

              <View style={styles.modalSubSection}>
                <Text style={styles.modalLabel}>IMPLEMENTATION INTENTION</Text>
                <TextInput 
                  placeholder="If [situation]..."
                  placeholderTextColor={COLORS.textDim}
                  style={styles.modalInputSmall}
                  value={conditionText}
                  onChangeText={setConditionText}
                />
              </View>

              <View style={styles.modalRow}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.modalLabel}>FREQUENCY (DAYS/WK)</Text>
                  <TextInput 
                    placeholder="7"
                    keyboardType="numeric"
                    placeholderTextColor={COLORS.textDim}
                    style={styles.modalInputSmall}
                    value={freq}
                    onChangeText={setFreq}
                  />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.modalLabel}>MASTERY TARGET (STREAK)</Text>
                  <TextInput 
                    placeholder="30"
                    keyboardType="numeric"
                    placeholderTextColor={COLORS.textDim}
                    style={styles.modalInputSmall}
                    value={streakTarget}
                    onChangeText={setStreakTarget}
                  />
                </View>
              </View>

              <View style={styles.modalSubSection}>
                <Text style={styles.modalLabel}>LIFE DOMAIN</Text>
                <View style={styles.difficultyPicker}>
                  {['physical', 'mental', 'work', 'social', 'sleep'].map((d) => (
                    <TouchableOpacity 
                      key={d}
                      onPress={() => setDomain(d)}
                      style={[styles.diffBtn, domain === d && styles.diffBtnActive]}
                    >
                      <Text style={[styles.diffText, domain === d && styles.diffTextActive]}>
                        {d === 'physical' ? '💪' : d === 'mental' ? '🧠' : d === 'work' ? '💼' : d === 'social' ? '💞' : '😴'}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              <View style={styles.modalSubSection}>
                <Text style={styles.modalLabel}>DIFFICULTY</Text>
                <View style={styles.difficultyPicker}>
                  {['easy', 'medium', 'hard'].map((d) => (
                    <TouchableOpacity 
                      key={d}
                      onPress={() => setDifficulty(d)}
                      style={[styles.diffBtn, difficulty === d && styles.diffBtnActive]}
                    >
                      <Text style={[styles.diffText, difficulty === d && styles.diffTextActive]}>{d}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              <TouchableOpacity 
                style={styles.saveBtn}
                onPress={handleCreateHabit}
              >
                <Text style={styles.saveBtnText}>Activate Anchor</Text>
              </TouchableOpacity>
            </MotiView>
          </View>
        )}
      </AnimatePresence>
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
  sectionHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    marginBottom: SPACING[3] 
  },
  seeAll: { ...TYPOGRAPHY.label, color: COLORS.primary, fontSize: 10 },
  pulseCard: {
    padding: SPACING[6],
    borderRadius: RADIUS.xl,
    gap: SPACING[6],
    backgroundColor: COLORS.surface
  },
  journeyHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'flex-end',
    marginBottom: SPACING[2]
  },
  archetypeTitle: { ...TYPOGRAPHY.h2, color: COLORS.text, fontSize: 22, letterSpacing: -0.5 },
  rankTitle: { ...TYPOGRAPHY.caption, color: COLORS.primary, fontSize: 12, fontWeight: '700', letterSpacing: 1 },
  archetypeSubtext: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, fontSize: 13, marginTop: SPACING[2], lineHeight: 20 },
  xpBox: { alignItems: 'flex-end' },
  xpText: { ...TYPOGRAPHY.caption, color: COLORS.textDim, fontSize: 10 },
  progressBarBg: { 
    height: 8, 
    backgroundColor: '#F3F4F6', 
    borderRadius: 4, 
    overflow: 'hidden',
    marginBottom: SPACING[4]
  },
  progressBarFill: { 
    height: '100%', 
    backgroundColor: COLORS.primary,
    borderRadius: 4
  },
  pulseGrid: { gap: SPACING[4] },
  pulseRow: { gap: SPACING[2] },
  pulseHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  pulseLabel: { ...TYPOGRAPHY.caption, color: COLORS.textSecondary, fontSize: 12 },
  pulsePercentage: { ...TYPOGRAPHY.caption, color: COLORS.text, fontWeight: '600', fontSize: 12 },
  pulseBarBg: { 
    height: 4, 
    backgroundColor: 'rgba(0,0,0,0.03)', 
    borderRadius: RADIUS.full, 
    overflow: 'hidden' 
  },
  pulseBarFill: { height: '100%', borderRadius: RADIUS.full },

  journeyScroll: { paddingLeft: 0, marginTop: SPACING[2] },
  journeyMiniCard: {
    width: 140,
    padding: SPACING[4],
    borderRadius: RADIUS.lg,
    marginRight: SPACING[4],
    backgroundColor: COLORS.surface,
    gap: 8
  },
  miniIconBg: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: 'rgba(109, 186, 157, 0.1)',
    alignItems: 'center',
    justifyContent: 'center'
  },
  miniTitle: { ...TYPOGRAPHY.label, fontSize: 12, color: COLORS.text },
  miniStatus: { ...TYPOGRAPHY.caption, fontSize: 10, color: COLORS.textDim },

  fab: {
    position: 'absolute',
    bottom: 100,
    right: SPACING[6],
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center',
    ...SHADOWS.card,
    elevation: 8
  },

  modalOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: SPACING[6],
    zIndex: 1000
  },
  modalCard: {
    width: '100%',
    backgroundColor: COLORS.surface,
    borderRadius: RADIUS.xl,
    padding: SPACING[6],
    ...SHADOWS.card
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING[6]
  },
  modalTitle: { ...TYPOGRAPHY.h2, fontSize: 20, color: COLORS.text },
  modalInput: {
    backgroundColor: '#F3F4F6',
    borderRadius: RADIUS.lg,
    padding: SPACING[4],
    color: COLORS.text,
    fontSize: 16,
    marginBottom: SPACING[4],
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  modalSubSection: { marginBottom: SPACING[4] },
  modalLabel: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 10, marginBottom: 8, letterSpacing: 1 },
  modalInputSmall: {
    backgroundColor: '#F3F4F6',
    borderRadius: RADIUS.md,
    padding: SPACING[3],
    color: COLORS.text,
    fontSize: 14,
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  modalRow: { flexDirection: 'row', gap: SPACING[4], marginBottom: SPACING[6] },
  difficultyPicker: {
    flexDirection: 'row',
    gap: SPACING[3],
  },
  diffBtn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: RADIUS.md,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    alignItems: 'center'
  },
  diffBtnActive: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary
  },
  diffText: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 12 },
  diffTextActive: { color: '#FFF' },
  saveBtn: {
    backgroundColor: COLORS.primary,
    height: 54,
    borderRadius: RADIUS.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: SPACING[4],
    ...SHADOWS.card
  },
  saveBtnText: { ...TYPOGRAPHY.label, color: '#FFF', fontSize: 16, fontWeight: '700' },
});
