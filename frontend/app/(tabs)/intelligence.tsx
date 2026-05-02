import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, SafeAreaView,
  TouchableOpacity, RefreshControl, Modal, useWindowDimensions
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { HabitHeatmap } from '../../src/components/HabitHeatmap';
import DailyCheckin from '../../src/components/DailyCheckin';
import { MotiView, AnimatePresence } from 'moti';
import {
  Brain, TrendingUp, Zap, Activity, BarChart2,
  ChevronRight, Lightbulb, Target, AlertTriangle, CheckCircle
} from 'lucide-react-native';

const ARCHETYPES = [
  { id: 'warrior', emoji: '⚔️', color: '#33ffd6' },
  { id: 'monk', emoji: '🧘', color: '#a78bfa' },
  { id: 'builder', emoji: '🚀', color: '#38bdf8' },
  { id: 'explorer', emoji: '🌿', color: '#f472b6' },
];

export default function InsightsScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [pulseData, setPulseData] = useState<any>(null);
  const [weeklyData, setWeeklyData] = useState<any>(null);
  const [heatmapData, setHeatmapData] = useState<Record<string, number>>({});
  const [patterns, setPatterns] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [todayCheckin, setTodayCheckin] = useState<any>(null);
  const [showArchetypeSheet, setShowArchetypeSheet] = useState(false);
  const [showCheckin, setShowCheckin] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const { token, identityPulse, setUserInfo } = useUserStore();
  const { width: screenW } = useWindowDimensions();
  const barMaxW = screenW - 80; // for animated pixel-width bar

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [pulse, weekly, heatmap, patternRes, recRes, todayCheckinRes, stateRes] = await Promise.all([
        api('/analytics/pulse', 'GET', null, token),
        api('/analytics/weekly', 'GET', null, token),
        api('/analytics/heatmap', 'GET', null, token),
        api('/psychological/behavior/patterns', 'GET', null, token),
        api('/analytics/recommendations', 'GET', null, token),
        api('/psychological/today-checkin', 'GET', null, token),
        api('/habits/state', 'GET', null, token),
      ]);
      setPulseData(pulse);
      setWeeklyData(weekly);
      setHeatmapData(heatmap?.heatmap || {});
      setPatterns(patternRes);
      setRecommendations(recRes);
      setTodayCheckin(todayCheckinRes?.done ? todayCheckinRes.checkin : null);
      if (stateRes?.user_state) {
        setUserInfo({ identityPulse: pulse?.score || 0, level: stateRes.user_state.level });
      }
    } catch (e) { console.error('Insights fetch error:', e); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = async () => { setRefreshing(true); await fetchData(); setRefreshing(false); };

  const toast = (msg: string) => { setToastMsg(msg); setTimeout(() => setToastMsg(null), 3000); };

  const handleArchetypeChange = async (archetype: string) => {
    try {
      const res = await api('/users/set-archetype', 'POST', { archetype, seed_habits: false }, token!);
      setUserInfo({ identityGoal: res.identity_goal });
      setShowArchetypeSheet(false);
      toast(`✓ Archetype updated to ${archetype.charAt(0).toUpperCase() + archetype.slice(1)}`);
    } catch (e) { console.error('Archetype change failed:', e); }
  };

  const burnout = patterns?.burnout_score ?? 0;
  const burnoutColor = burnout > 0.7 ? '#f87171' : burnout > 0.4 ? COLORS.gold : COLORS.primary;
  const burnoutLabel = burnout > 0.7 ? 'HIGH' : burnout > 0.4 ? 'MEDIUM' : 'LOW';

  return (
    <SafeAreaView style={styles.safeArea}>
      <AnimatePresence>
        {toastMsg && (
          <MotiView key="t" from={{ opacity: 0, translateY: -10 }} animate={{ opacity: 1, translateY: 0 }} exit={{ opacity: 0 }} style={styles.toast}>
            <CheckCircle size={14} color={COLORS.primary} />
            <Text style={styles.toastText}>{toastMsg}</Text>
          </MotiView>
        )}
      </AnimatePresence>

      <ScrollView style={styles.container} contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />}>

        <View style={styles.header}>
          <View>
            <Text style={styles.title}>Insights</Text>
            <Text style={styles.subtitle}>Behavioral mapping & identity alignment.</Text>
          </View>
          <Brain size={28} color={COLORS.primary} />
        </View>

        {/* IDENTITY PULSE — clean flat card, no floating ring */}
        <MotiView from={{ opacity: 0, translateY: 12 }} animate={{ opacity: 1, translateY: 0 }} transition={{ type: 'spring', duration: 700 }}>
          <GlassCard style={styles.pulseCard}>
            {/* Top row: label + archetype button */}
            <View style={styles.pulseHeader}>
              <View>
                <Text style={styles.pulseSub}>IDENTITY PULSE</Text>
                <Text style={styles.pulseStatus}>{pulseData?.status?.toUpperCase() || 'CALIBRATING'}</Text>
              </View>
              <TouchableOpacity style={styles.archetypeBtn} onPress={() => setShowArchetypeSheet(true)}>
                <Text style={styles.archetypeEmoji}>
                  {ARCHETYPES.find(a => a.id === pulseData?.goal?.toLowerCase())?.emoji || '⚔️'}
                </Text>
                <Text style={styles.archetypeName}>{(pulseData?.goal || 'Warrior').toUpperCase()}</Text>
                <Text style={styles.archetypeChange}>Change →</Text>
              </TouchableOpacity>
            </View>

            {/* Big % number */}
            <Text style={styles.pulsePercent}>{identityPulse || 0}<Text style={styles.pulsePercentSuffix}>%</Text></Text>
            <Text style={styles.pulseAlignedLabel}>ALIGNED TO IDENTITY</Text>

            {/* Animated alignment bar */}
            <View style={styles.pulseBarBg}>
              <MotiView
                from={{ width: 0 }}
                animate={{ width: Math.round(((identityPulse || 0) / 100) * barMaxW) }}
                transition={{ type: 'timing', duration: 1200 }}
                style={[styles.pulseBarFill, {
                  backgroundColor: (identityPulse || 0) > 60 ? COLORS.primary : (identityPulse || 0) > 30 ? COLORS.gold : '#64748b'
                }]}
              />
            </View>

            {/* 3 stat chips */}
            <View style={styles.pulseChips}>
              <View style={styles.pulseChip}>
                <Text style={styles.pulseChipVal}>{pulseData?.total_completions || 0}</Text>
                <Text style={styles.pulseChipLabel}>COMPLETIONS</Text>
              </View>
              <View style={[styles.pulseChip, { borderColor: `${burnoutColor}40` }]}>
                <Text style={[styles.pulseChipVal, { color: burnoutColor }]}>{burnoutLabel}</Text>
                <Text style={styles.pulseChipLabel}>BURNOUT RISK</Text>
              </View>
              <View style={styles.pulseChip}>
                <Text style={styles.pulseChipVal}>{weeklyData?.total_completed || 0}</Text>
                <Text style={styles.pulseChipLabel}>THIS WEEK</Text>
              </View>
            </View>

            {pulseData?.recommendation && (
              <Text style={styles.pulseInsight}>{pulseData.recommendation}</Text>
            )}
          </GlassCard>
        </MotiView>

        {/* DAILY CHECKIN PROMPT */}
        {!todayCheckin && (
          <MotiView from={{ opacity: 0, translateY: 10 }} animate={{ opacity: 1, translateY: 0 }} transition={{ delay: 100 }}>
            <TouchableOpacity onPress={() => setShowCheckin(true)}>
              <GlassCard variant="ai" style={styles.checkinPrompt}>
                <View style={styles.checkinPromptRow}>
                  <Brain size={18} color={COLORS.secondary} />
                  <View style={{ flex: 1 }}>
                    <Text style={styles.checkinPromptTitle}>Calibrate your intelligence engine</Text>
                    <Text style={styles.checkinPromptSub}>Today's check-in pending — 30 seconds to log mood, energy & sleep.</Text>
                  </View>
                  <ChevronRight size={18} color={COLORS.secondary} />
                </View>
              </GlassCard>
            </TouchableOpacity>
          </MotiView>
        )}

        {/* WEEKLY STATS */}
        <View style={styles.statsGrid}>
          <GlassCard style={styles.statBox}>
            <BarChart2 size={18} color={COLORS.secondary} />
            <Text style={styles.statVal}>{weeklyData?.total_completed || 0}</Text>
            <Text style={styles.statLab}>This Week</Text>
          </GlassCard>
          <GlassCard style={styles.statBox}>
            <Zap size={18} color={COLORS.gold} />
            <Text style={styles.statVal}>{weeklyData?.completion_rate || 0}%</Text>
            <Text style={styles.statLab}>Success Rate</Text>
          </GlassCard>
          <GlassCard style={[styles.statBox, { borderColor: burnoutColor, borderWidth: 1 }]}>
            <Activity size={18} color={burnoutColor} />
            <Text style={[styles.statVal, { color: burnoutColor }]}>
              {burnout > 0.7 ? 'High' : burnout > 0.4 ? 'Med' : 'Low'}
            </Text>
            <Text style={styles.statLab}>Burnout</Text>
          </GlassCard>
        </View>

        {/* BEHAVIORAL STORY */}
        <Text style={styles.sectionTitle}>YOUR BEHAVIORAL STORY</Text>
        <GlassCard style={styles.storyCard}>
          {[
            { label: 'Best day of week', value: weeklyData?.best_day || 'Collecting data...', icon: <TrendingUp size={14} color={COLORS.primary} /> },
            { label: 'Coach suggestion', value: recommendations?.suggestion || 'Keep building consistency', icon: <Lightbulb size={14} color={COLORS.gold} /> },
            { label: 'Improvement area', value: weeklyData?.improvement_tip || 'Complete 7+ habits to unlock', icon: <Target size={14} color={COLORS.secondary} /> },
          ].map((row, i) => (
            <View key={i} style={[styles.storyRow, i < 2 && styles.storyRowBorder]}>
              <View style={styles.storyLeft}>{row.icon}<Text style={styles.storyLabel}>{row.label}</Text></View>
              <Text style={styles.storyVal}>{row.value}</Text>
            </View>
          ))}
        </GlassCard>

        {/* ACTIVITY CALENDAR */}
        <Text style={styles.sectionTitle}>ACTIVITY CALENDAR</Text>
        <GlassCard style={styles.heatmapCard}>
          <HabitHeatmap data={heatmapData} weeks={15} />
        </GlassCard>

        {/* BEHAVIOR PATTERNS */}
        {patterns && (
          <MotiView from={{ opacity: 0, translateY: 10 }} animate={{ opacity: 1, translateY: 0 }} transition={{ delay: 300 }}>
            <Text style={styles.sectionTitle}>PATTERN RECOGNITION</Text>
            <GlassCard style={styles.patternsCard}>
              <View style={styles.patternHeader}>
                <TrendingUp size={14} color={COLORS.primary} />
                <Text style={styles.patternHeaderText}>Machine-Learned Insights</Text>
                <View style={[styles.burnoutBadge, { borderColor: burnoutColor }]}>
                  <AlertTriangle size={10} color={burnoutColor} />
                  <Text style={[styles.burnoutBadgeText, { color: burnoutColor }]}>{burnoutLabel} RISK</Text>
                </View>
              </View>
              {patterns?.patterns?.length > 0 ? (
                patterns.patterns.slice(0, 5).map((p: any, i: number) => (
                  <View key={i} style={styles.patternRow}>
                    <View style={[styles.patternDot, { backgroundColor: COLORS.primary }]} />
                    <View style={{ flex: 1 }}>
                      <Text style={styles.patternKey}>{p.insight_key?.replace(/_/g, ' ').toUpperCase() || 'INSIGHT'}</Text>
                      <Text style={styles.patternVal}>{p.insight_value || '—'}</Text>
                    </View>
                    <Text style={styles.patternConf}>{Math.round((p.confidence_score || 0) * 100)}%</Text>
                  </View>
                ))
              ) : (
                <View style={styles.patternEmpty}>
                  <Text style={styles.patternEmptyText}>Complete 7+ habits to unlock pattern analysis.</Text>
                  <View style={styles.unlockBar}>
                    <View style={[styles.unlockFill, { width: `${Math.min((weeklyData?.total_completed || 0) / 7 * 100, 100)}%` }]} />
                  </View>
                  <Text style={styles.unlockCount}>{weeklyData?.total_completed || 0} / 7 completions</Text>
                </View>
              )}
            </GlassCard>
          </MotiView>
        )}

        {/* AI OPTIMIZATION */}
        {recommendations?.insights?.length > 0 && (
          <>
            <Text style={styles.sectionTitle}>AI OPTIMIZATION</Text>
            <GlassCard variant="ai" style={styles.aiCard}>
              {recommendations.insights.map((ins: string, i: number) => (
                <View key={i} style={styles.insightRow}>
                  <View style={styles.insightBullet} />
                  <Text style={styles.insightText}>{ins}</Text>
                </View>
              ))}
              {recommendations.suggestion && (
                <TouchableOpacity style={styles.actionBtn}>
                  <Text style={styles.actionText}>Try: {recommendations.suggestion}</Text>
                  <ChevronRight size={14} color={COLORS.secondary} />
                </TouchableOpacity>
              )}
            </GlassCard>
          </>
        )}
      </ScrollView>

      {/* Archetype Picker Sheet */}
      <Modal visible={showArchetypeSheet} animationType="slide" transparent onRequestClose={() => setShowArchetypeSheet(false)}>
        <View style={styles.sheetBg}>
          <View style={styles.sheet}>
            <View style={styles.sheetHandle} />
            <Text style={styles.sheetTitle}>Change Archetype</Text>
            <Text style={styles.sheetSub}>Changing your archetype reshapes your AI coaching and identity goals.</Text>
            {ARCHETYPES.map((arch) => (
              <TouchableOpacity key={arch.id} style={[styles.archCard, { borderColor: `${arch.color}40` }]} onPress={() => handleArchetypeChange(arch.id)}>
                <Text style={styles.archEmoji}>{arch.emoji}</Text>
                <Text style={[styles.archName, { color: arch.color }]}>{arch.id.charAt(0).toUpperCase() + arch.id.slice(1)}</Text>
                <ChevronRight size={16} color={arch.color} />
              </TouchableOpacity>
            ))}
            <TouchableOpacity style={styles.cancelBtn} onPress={() => setShowArchetypeSheet(false)}>
              <Text style={styles.cancelText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Daily Checkin Modal */}
      <Modal visible={showCheckin} animationType="slide" presentationStyle="pageSheet" onRequestClose={() => setShowCheckin(false)}>
        <View style={styles.modal}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Daily Check-In</Text>
            <TouchableOpacity onPress={() => setShowCheckin(false)}><Text style={styles.modalClose}>✕ Close</Text></TouchableOpacity>
          </View>
          <DailyCheckin onComplete={(res) => { setShowCheckin(false); setTodayCheckin(res?.checkin); toast('✓ Check-in saved. Intelligence engine updated.'); fetchData(); }} />
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  content: { padding: SPACING.margin, paddingBottom: 110 },
  toast: { position: 'absolute', top: 56, left: 16, right: 16, zIndex: 999, flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: 'rgba(15,23,42,0.97)', borderWidth: 1, borderColor: 'rgba(51,255,214,0.3)', borderRadius: 14, padding: 14, elevation: 8 },
  toastText: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 13, color: COLORS.text, flex: 1 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: SPACING.lg },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text },
  subtitle: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, marginTop: 4, fontSize: 13 },

  pulseCard: { padding: SPACING.lg, marginBottom: SPACING.lg },
  pulseHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: SPACING.md },
  pulseSub: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 9, color: COLORS.textDim, letterSpacing: 2 },
  pulseStatus: { ...TYPOGRAPHY.h3, color: COLORS.primary, marginTop: 4 },
  archetypeBtn: { alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 14, padding: 10, gap: 2 },
  archetypeEmoji: { fontSize: 24 },
  archetypeName: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 10, color: COLORS.text, letterSpacing: 1 },
  archetypeChange: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 9, color: COLORS.primary },
  pulsePercent: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 64, color: COLORS.text, lineHeight: 68 },
  pulsePercentSuffix: { fontSize: 28, color: COLORS.textDim },
  pulseAlignedLabel: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 9, color: COLORS.textDim, letterSpacing: 2, marginBottom: 14, marginTop: 2 },
  pulseBarBg: { height: 6, backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden', marginBottom: SPACING.lg },
  pulseBarFill: { height: '100%', borderRadius: 3 },
  pulseChips: { flexDirection: 'row', gap: 10, marginBottom: SPACING.md },
  pulseChip: {
    flex: 1, alignItems: 'center', paddingVertical: 10,
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 12, borderWidth: 1, borderColor: 'rgba(255,255,255,0.07)',
  },
  pulseChipVal: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 18, color: COLORS.text },
  pulseChipLabel: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 8, color: COLORS.textDim, letterSpacing: 1, marginTop: 2 },
  pulseInsight: { ...TYPOGRAPHY.body, fontSize: 13, color: COLORS.textSecondary, lineHeight: 19, textAlign: 'center', marginTop: 4 },

  checkinPrompt: { padding: SPACING.md, marginBottom: SPACING.md },
  checkinPromptRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  checkinPromptTitle: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 13, color: COLORS.text },
  checkinPromptSub: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 11, color: COLORS.textSecondary, marginTop: 2 },

  statsGrid: { flexDirection: 'row', gap: SPACING.sm, marginBottom: SPACING.lg },
  statBox: { flex: 1, padding: SPACING.md, alignItems: 'center', gap: 6 },
  statVal: { ...TYPOGRAPHY.h2, color: COLORS.text, fontSize: 20 },
  statLab: { ...TYPOGRAPHY.caption, color: COLORS.textDim },
  sectionTitle: { ...TYPOGRAPHY.label, color: COLORS.textDim, letterSpacing: 2, marginBottom: SPACING.md, marginTop: SPACING.md },

  storyCard: { padding: SPACING.lg, marginBottom: SPACING.sm },
  storyRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 12 },
  storyRowBorder: { borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)' },
  storyLeft: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  storyLabel: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 13, color: COLORS.textSecondary },
  storyVal: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 13, color: COLORS.text, flex: 1, textAlign: 'right', marginLeft: 12 },

  heatmapCard: { padding: SPACING.md, marginBottom: SPACING.sm },
  patternsCard: { padding: SPACING.lg, marginBottom: SPACING.sm },
  patternHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 14, paddingBottom: 14, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)' },
  patternHeaderText: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 12, color: COLORS.primary, flex: 1 },
  burnoutBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, borderWidth: 1, borderRadius: 8, paddingHorizontal: 8, paddingVertical: 3 },
  burnoutBadgeText: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 9, letterSpacing: 0.5 },
  patternRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.03)' },
  patternDot: { width: 6, height: 6, borderRadius: 3, marginRight: 10 },
  patternKey: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 9, color: COLORS.textDim, letterSpacing: 0.5 },
  patternVal: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 13, color: COLORS.text },
  patternConf: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 11, color: COLORS.textSecondary },
  patternEmpty: { paddingVertical: 8, alignItems: 'center' },
  patternEmptyText: { ...TYPOGRAPHY.body, fontSize: 13, color: COLORS.textDim, marginBottom: 12, textAlign: 'center' },
  unlockBar: { height: 4, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 2, width: '100%', overflow: 'hidden', marginBottom: 6 },
  unlockFill: { height: '100%', backgroundColor: COLORS.primary, borderRadius: 2 },
  unlockCount: { ...TYPOGRAPHY.caption, color: COLORS.textDim, fontSize: 10 },

  aiCard: { padding: SPACING.lg, marginBottom: SPACING.md },
  insightRow: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 10, gap: 8 },
  insightBullet: { width: 5, height: 5, borderRadius: 3, backgroundColor: COLORS.secondary, marginTop: 7 },
  insightText: { ...TYPOGRAPHY.body, fontSize: 13, color: COLORS.textSecondary, flex: 1, lineHeight: 19 },
  actionBtn: { flexDirection: 'row', alignItems: 'center', marginTop: 12, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)', paddingTop: 12 },
  actionText: { ...TYPOGRAPHY.label, color: COLORS.secondary, fontSize: 12, marginRight: 4, flex: 1 },

  sheetBg: { flex: 1, backgroundColor: 'rgba(0,0,0,0.6)', justifyContent: 'flex-end' },
  sheet: { backgroundColor: COLORS.surfaceLight, borderTopLeftRadius: 28, borderTopRightRadius: 28, padding: SPACING.lg, paddingBottom: 40 },
  sheetHandle: { width: 40, height: 4, backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: 2, alignSelf: 'center', marginBottom: 20 },
  sheetTitle: { ...TYPOGRAPHY.h3, color: COLORS.text, marginBottom: 6 },
  sheetSub: { ...TYPOGRAPHY.body, fontSize: 13, color: COLORS.textSecondary, marginBottom: 20 },
  archCard: { flexDirection: 'row', alignItems: 'center', gap: 16, padding: 16, borderWidth: 1, borderRadius: 16, marginBottom: 10, backgroundColor: 'rgba(255,255,255,0.03)' },
  archEmoji: { fontSize: 28 },
  archName: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 18, flex: 1 },
  cancelBtn: { marginTop: 8, padding: 16, alignItems: 'center' },
  cancelText: { ...TYPOGRAPHY.label, color: COLORS.textDim },

  modal: { flex: 1, backgroundColor: COLORS.background },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 24, paddingTop: 20, paddingBottom: 16, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.07)' },
  modalTitle: { ...TYPOGRAPHY.h3, color: COLORS.text },
  modalClose: { ...TYPOGRAPHY.label, color: COLORS.textDim },
});
