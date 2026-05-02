import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  TouchableOpacity,
  RefreshControl,
  Modal,
  Alert,
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import DailyCheckin from '../../src/components/DailyCheckin';
import {
  Brain,
  TrendingUp,
  Lightbulb,
  Zap,
  ChevronRight,
  Heart,
  CheckCircle,
  Calendar,
  AlertTriangle,
} from 'lucide-react-native';
import { MotiView } from 'moti';

export default function CoachScreen() {
  const { token } = useUserStore();
  const [refreshing, setRefreshing] = useState(false);
  const [showCheckin, setShowCheckin] = useState(false);
  const [checkinDone, setCheckinDone] = useState(false);
  const [checkinInsights, setCheckinInsights] = useState<any>(null);
  const [patterns, setPatterns] = useState<any>(null);
  const [challenge, setChallenge] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [patternRes, challengeRes, recRes] = await Promise.all([
        api('/psychological/behavior/patterns', 'GET', null, token),
        api('/psychological/daily-challenge', 'GET', null, token),
        api('/analytics/recommendations', 'GET', null, token),
      ]);
      setPatterns(patternRes);
      setChallenge(challengeRes?.challenge);
      setRecommendations(recRes);
    } catch (e) {
      console.error('Coach fetch error:', e);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const handleCheckinComplete = (response: any) => {
    setCheckinDone(true);
    setCheckinInsights(response?.insights);
    setShowCheckin(false);
    Alert.alert('✅ Check-In Saved', response?.message || 'Your daily pulse is recorded.');
  };

  const burnout = patterns?.burnout_score ?? 0;
  const burnoutLevel = burnout > 0.7 ? 'High' : burnout > 0.4 ? 'Medium' : 'Low';
  const burnoutColor = burnout > 0.7 ? COLORS.danger : burnout > 0.4 ? COLORS.gold : COLORS.primary;

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>AI Coach</Text>
            <Text style={styles.subtitle}>Live cognitive analysis and optimization.</Text>
          </View>
          <Brain size={28} color={COLORS.secondary} />
        </View>

        {/* LIFE CHECK-IN CARD */}
        <MotiView
          from={{ opacity: 0, translateY: 16 }}
          animate={{ opacity: 1, translateY: 0 }}
          transition={{ type: 'spring', delay: 50 }}
        >
          <GlassCard style={styles.checkinCard}>
            <View style={styles.checkinHeader}>
              <View style={styles.checkinLeft}>
                <Heart size={20} color={checkinDone ? COLORS.primary : COLORS.secondary} />
                <Text style={styles.checkinTitle}>DAILY LIFE CHECK-IN</Text>
              </View>
              {checkinDone ? (
                <View style={styles.doneBadge}>
                  <CheckCircle size={14} color={COLORS.primary} />
                  <Text style={styles.doneText}>DONE</Text>
                </View>
              ) : (
                <View style={styles.pendingBadge}>
                  <Text style={styles.pendingText}>PENDING</Text>
                </View>
              )}
            </View>
            <Text style={styles.checkinDesc}>
              Log your mood, energy, and sleep to calibrate your behavioral intelligence engine.
            </Text>

            {checkinInsights && (
              <View style={styles.insightChips}>
                {Object.entries(checkinInsights).slice(0, 3).map(([k, v]: any) => (
                  <View key={k} style={styles.insightChip}>
                    <Text style={styles.insightChipKey}>{k.replace(/_/g, ' ').toUpperCase()}</Text>
                    <Text style={styles.insightChipVal}>{String(v).toUpperCase()}</Text>
                  </View>
                ))}
              </View>
            )}

            <TouchableOpacity
              style={[styles.checkinBtn, checkinDone && styles.checkinBtnDone]}
              onPress={() => setShowCheckin(true)}
            >
              <Text style={[styles.checkinBtnText, checkinDone && styles.checkinBtnTextDone]}>
                {checkinDone ? 'Update Check-In' : 'Start Check-In →'}
              </Text>
            </TouchableOpacity>
          </GlassCard>
        </MotiView>

        {/* DAILY CHALLENGE */}
        {challenge && (
          <MotiView
            from={{ opacity: 0, translateY: 16 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: 'spring', delay: 150 }}
          >
            <GlassCard variant="ai" style={styles.card}>
              <View style={styles.cardHeader}>
                <Zap size={18} color={COLORS.secondary} fill={COLORS.secondary} />
                <Text style={[styles.cardTitle, { color: COLORS.secondary }]}>DAILY CHALLENGE</Text>
                <View style={styles.xpPill}>
                  <Text style={styles.xpPillText}>+{challenge.xp_reward || 50} XP</Text>
                </View>
              </View>
              <Text style={styles.challengeName}>{challenge.challenge || 'Complete 3 habits before noon'}</Text>
              <Text style={styles.challengeDesc}>{challenge.description || 'A focused morning builds an unstoppable day.'}</Text>
              <TouchableOpacity style={styles.actionBtn}>
                <Text style={styles.actionText}>Accept Challenge</Text>
                <ChevronRight size={14} color={COLORS.secondary} />
              </TouchableOpacity>
            </GlassCard>
          </MotiView>
        )}

        {/* BEHAVIOR PATTERNS */}
        {patterns && (
          <MotiView
            from={{ opacity: 0, translateY: 16 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ type: 'spring', delay: 250 }}
          >
            <Text style={styles.sectionTitle}>BEHAVIORAL ANALYSIS</Text>
            <GlassCard style={styles.card}>
              <View style={styles.cardHeader}>
                <TrendingUp size={18} color={COLORS.primary} />
                <Text style={styles.cardTitle}>Pattern Recognition</Text>
              </View>

              {/* Burnout Risk */}
              <View style={styles.metricRow}>
                <View style={styles.metricLeft}>
                  <AlertTriangle size={14} color={burnoutColor} />
                  <Text style={styles.metricLabel}>Burnout Risk</Text>
                </View>
                <View style={[styles.burnoutBadge, { borderColor: burnoutColor }]}>
                  <Text style={[styles.burnoutText, { color: burnoutColor }]}>{burnoutLevel}</Text>
                </View>
              </View>

              {/* Patterns list */}
              {patterns?.patterns?.slice(0, 4).map((p: any, i: number) => (
                <View key={i} style={styles.patternRow}>
                  <Text style={styles.patternKey}>{p.insight_key?.replace(/_/g, ' ').toUpperCase() || 'INSIGHT'}</Text>
                  <Text style={styles.patternVal}>{p.insight_value || '—'}</Text>
                </View>
              ))}

              {(!patterns?.patterns || patterns.patterns.length === 0) && (
                <Text style={styles.emptyPatterns}>
                  Complete more habits to unlock pattern insights.
                </Text>
              )}
            </GlassCard>
          </MotiView>
        )}

        {/* AI RECOMMENDATIONS */}
        <MotiView
          from={{ opacity: 0, translateY: 16 }}
          animate={{ opacity: 1, translateY: 0 }}
          transition={{ type: 'spring', delay: 350 }}
        >
          <Text style={styles.sectionTitle}>AI OPTIMIZATION</Text>
          <GlassCard variant="ai" style={styles.card}>
            <View style={styles.cardHeader}>
              <Lightbulb size={18} color={COLORS.secondary} />
              <Text style={[styles.cardTitle, { color: COLORS.secondary }]}>System Insights</Text>
            </View>
            {recommendations?.insights?.map((ins: string, i: number) => (
              <View key={i} style={styles.insightRow}>
                <View style={styles.insightBullet} />
                <Text style={styles.insightText}>{ins}</Text>
              </View>
            ))}
            {recommendations?.suggestion && (
              <TouchableOpacity style={styles.actionBtn}>
                <Text style={styles.actionText}>Try: {recommendations.suggestion}</Text>
                <ChevronRight size={14} color={COLORS.secondary} />
              </TouchableOpacity>
            )}
          </GlassCard>
        </MotiView>
      </ScrollView>

      {/* CHECKIN MODAL */}
      <Modal
        visible={showCheckin}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowCheckin(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Daily Life Check-In</Text>
            <TouchableOpacity onPress={() => setShowCheckin(false)}>
              <Text style={styles.modalClose}>✕ Close</Text>
            </TouchableOpacity>
          </View>
          <DailyCheckin onComplete={handleCheckinComplete} />
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  content: { padding: SPACING.margin, paddingBottom: 100 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.lg,
  },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text },
  subtitle: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, marginTop: 4, fontSize: 13 },

  // Check-in card
  checkinCard: {
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
    borderColor: 'rgba(167, 139, 250, 0.25)',
    borderWidth: 1,
  },
  checkinHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  checkinLeft: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  checkinTitle: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 11,
    color: COLORS.secondary,
    letterSpacing: 1.5,
  },
  doneBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(51, 255, 214, 0.1)',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 3,
    gap: 4,
  },
  doneText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 9,
    color: COLORS.primary,
    letterSpacing: 1,
  },
  pendingBadge: {
    backgroundColor: 'rgba(251, 191, 36, 0.1)',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  pendingText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 9,
    color: COLORS.gold,
    letterSpacing: 1,
  },
  checkinDesc: {
    ...TYPOGRAPHY.body,
    fontSize: 13,
    color: COLORS.textSecondary,
    marginBottom: 12,
    lineHeight: 19,
  },
  insightChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 12,
  },
  insightChip: {
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  insightChipKey: {
    fontFamily: 'SpaceGrotesk_500Medium',
    fontSize: 8,
    color: COLORS.textDim,
    letterSpacing: 0.5,
  },
  insightChipVal: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 11,
    color: COLORS.text,
    marginTop: 1,
  },
  checkinBtn: {
    backgroundColor: COLORS.secondary,
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 4,
  },
  checkinBtnDone: {
    backgroundColor: 'rgba(167, 139, 250, 0.12)',
    borderWidth: 1,
    borderColor: COLORS.secondary,
  },
  checkinBtnText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 13,
    color: '#fff',
    letterSpacing: 0.5,
  },
  checkinBtnTextDone: { color: COLORS.secondary },

  card: { padding: SPACING.lg, marginBottom: SPACING.md },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  cardTitle: {
    ...TYPOGRAPHY.label,
    color: COLORS.primary,
    letterSpacing: 1,
    flex: 1,
  },
  xpPill: {
    backgroundColor: 'rgba(167, 139, 250, 0.15)',
    borderRadius: 20,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  xpPillText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 11,
    color: COLORS.secondary,
  },
  challengeName: {
    fontFamily: 'SpaceGrotesk_600SemiBold',
    fontSize: 16,
    color: COLORS.text,
    marginBottom: 6,
  },
  challengeDesc: {
    ...TYPOGRAPHY.body,
    fontSize: 13,
    color: COLORS.textSecondary,
    lineHeight: 19,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 16,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
    paddingTop: 14,
  },
  actionText: {
    ...TYPOGRAPHY.label,
    color: COLORS.secondary,
    fontSize: 12,
    marginRight: 4,
    flex: 1,
  },

  sectionTitle: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textDim,
    letterSpacing: 2,
    marginBottom: 12,
    marginTop: 8,
  },

  // Patterns
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
    paddingBottom: 14,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  metricLeft: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  metricLabel: { ...TYPOGRAPHY.body, fontSize: 14, color: COLORS.text },
  burnoutBadge: {
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  burnoutText: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 12 },
  patternRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.03)',
  },
  patternKey: {
    fontFamily: 'SpaceGrotesk_500Medium',
    fontSize: 10,
    color: COLORS.textDim,
    letterSpacing: 0.5,
    flex: 1,
  },
  patternVal: {
    fontFamily: 'SpaceGrotesk_600SemiBold',
    fontSize: 12,
    color: COLORS.primary,
  },
  emptyPatterns: {
    ...TYPOGRAPHY.body,
    fontSize: 13,
    color: COLORS.textDim,
    textAlign: 'center',
    paddingVertical: 12,
  },

  // Recommendations
  insightRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
    gap: 8,
  },
  insightBullet: {
    width: 5,
    height: 5,
    borderRadius: 3,
    backgroundColor: COLORS.secondary,
    marginTop: 7,
  },
  insightText: {
    ...TYPOGRAPHY.body,
    fontSize: 13,
    color: COLORS.textSecondary,
    flex: 1,
    lineHeight: 19,
  },

  // Modal
  modalContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.07)',
  },
  modalTitle: {
    ...TYPOGRAPHY.h3,
    color: COLORS.text,
  },
  modalClose: {
    ...TYPOGRAPHY.label,
    color: COLORS.textDim,
  },
});
