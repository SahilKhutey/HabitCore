import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, SafeAreaView,
  TouchableOpacity, RefreshControl, Modal, useWindowDimensions
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import MoodChart from '../../src/components/MoodChart';
import DailyCheckin from '../../src/components/DailyCheckin';
import { AnimatePresence, MotiView } from 'moti';
import { Heart, Wind, Coffee, Moon, ChevronRight, CheckCircle, Plus } from 'lucide-react-native';

const DOMAIN_ICONS: Record<string, string> = { physical: '💪', mental: '🧠', work: '💼', social: '💞', sleep: '😴' };
const MOOD_EMOJIS: Record<string, string> = { happy: '😊', excited: '🤩', neutral: '😐', tired: '😴', sad: '😢', angry: '😤' };
const ENERGY_COLORS: Record<string, string> = { high: COLORS.primary, medium: COLORS.gold, low: '#f87171' };

export default function LifeScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [domains, setDomains] = useState<any[]>([]);
  const [overallScore, setOverallScore] = useState(0);
  const [checkinHistory, setCheckinHistory] = useState<any[]>([]);
  const [todayCheckin, setTodayCheckin] = useState<any>(null);
  const [showCheckin, setShowCheckin] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const { token, burnoutScore, setUserInfo } = useUserStore();
  const { width: screenW } = useWindowDimensions();
  const barWidth = screenW - 160; // approx content width minus padding + emoji

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [domainsRes, historyRes, todayRes, stateRes] = await Promise.all([
        api('/psychological/life-domains', 'GET', null, token),
        api('/psychological/checkin/history', 'GET', null, token),
        api('/psychological/today-checkin', 'GET', null, token),
        api('/habits/state', 'GET', null, token),
      ]);
      setDomains(domainsRes?.domains || []);
      setOverallScore(domainsRes?.overall_score || 0);
      setCheckinHistory(historyRes?.checkins || []);
      setTodayCheckin(todayRes?.done ? todayRes.checkin : null);
      if (stateRes?.user_state) {
        setUserInfo({ burnoutScore: stateRes.user_state.burnout_score, recoveryMode: stateRes.user_state.mode });
      }
    } catch (e) { console.error('Life fetch error:', e); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = async () => { setRefreshing(true); await fetchData(); setRefreshing(false); };

  const toast = (msg: string) => { setToastMsg(msg); setTimeout(() => setToastMsg(null), 3000); };

  const handleCheckinComplete = (response: any) => {
    setShowCheckin(false);
    setTodayCheckin(response?.checkin);
    toast('✓ Daily pulse recorded. Life score updated.');
    fetchData();
  };

  const burnoutCapacity = Math.round((1 - burnoutScore) * 100);
  const burnoutColor = burnoutScore < 0.3 ? COLORS.primary : burnoutScore < 0.7 ? COLORS.gold : '#f87171';

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
            <Text style={styles.title}>Life</Text>
            <Text style={styles.subtitle}>Your full-spectrum wellbeing dashboard.</Text>
          </View>
          <Heart size={28} color="#f472b6" />
        </View>

        {/* TODAY'S PULSE */}
        <MotiView from={{ opacity: 0, translateY: 16 }} animate={{ opacity: 1, translateY: 0 }}>
          <GlassCard style={[styles.pulseCard, todayCheckin && styles.pulseCardDone]}>
            <View style={styles.pulseRow}>
              <View style={{ flex: 1, marginRight: 12 }}>
                <Text style={styles.pulseLabel}>TODAY'S PULSE</Text>
                {todayCheckin ? (
                  <View style={styles.pulseData}>
                    <Text style={styles.moodEmoji}>{MOOD_EMOJIS[todayCheckin.mood] || '😐'}</Text>
                    <View>
                      <Text style={styles.moodText}>{todayCheckin.mood?.toUpperCase()}</Text>
                      <Text style={styles.energyText}>
                        Energy: <Text style={{ color: ENERGY_COLORS[todayCheckin.energy_morning] }}>{todayCheckin.energy_morning?.toUpperCase()}</Text>
                        {'  '}Sleep: <Text style={{ color: COLORS.gold }}>{todayCheckin.sleep_quality}/5</Text>
                      </Text>
                    </View>
                  </View>
                ) : (
                  <Text style={styles.pulsePrompt}>How are you feeling today?</Text>
                )}
              </View>
              <TouchableOpacity style={[styles.checkinBtn, todayCheckin && styles.checkinBtnDone]} onPress={() => setShowCheckin(true)}>
                {todayCheckin
                  ? <><CheckCircle size={14} color={COLORS.primary} /><Text style={styles.checkinBtnText}> Update</Text></>
                  : <><Plus size={14} color="#000" /><Text style={[styles.checkinBtnText, { color: '#000' }]}> Check In</Text></>}
              </TouchableOpacity>
            </View>
          </GlassCard>
        </MotiView>

        {/* OVERALL LIFE SCORE */}
        <GlassCard style={styles.scoreCard}>
          <View style={styles.scoreRow}>
            <View>
              <Text style={styles.scoreSub}>LIFE SCORE</Text>
              <Text style={styles.scoreValue}>{overallScore}<Text style={styles.scoreMax}>/100</Text></Text>
            </View>
            <View style={styles.recoveryPill}>
              <View style={[styles.recoveryDot, { backgroundColor: burnoutColor }]} />
              <Text style={[styles.recoveryLabel, { color: burnoutColor }]}>{burnoutCapacity}% RECOVERY</Text>
            </View>
          </View>
          <View style={styles.miniBarBg}>
            <MotiView from={{ width: 0 }} animate={{ width: Math.round((overallScore / 100) * (screenW - 80)) }}
              transition={{ type: 'timing', duration: 1200 }}
              style={[styles.miniBarFill, { backgroundColor: overallScore > 70 ? COLORS.primary : overallScore > 40 ? COLORS.gold : '#f87171' }]} />
          </View>
        </GlassCard>

        {/* LIFE DOMAINS */}
        <Text style={styles.sectionTitle}>LIFE DOMAINS</Text>
        {domains.length === 0 ? (
          <GlassCard style={styles.emptyCard}>
            <Text style={styles.emptyText}>Complete habits and check in to unlock life domain scores.</Text>
          </GlassCard>
        ) : (
          domains.map((domain, i) => (
            <MotiView key={domain.domain} from={{ opacity: 0, translateX: -20 }} animate={{ opacity: 1, translateX: 0 }} transition={{ delay: i * 80 }}>
              <GlassCard style={styles.domainCard}>
                <View style={styles.domainRow}>
                  <Text style={styles.domainEmoji}>{DOMAIN_ICONS[domain.domain]}</Text>
                  <View style={{ flex: 1 }}>
                    <View style={styles.domainHeader}>
                      <Text style={styles.domainLabel}>{domain.label}</Text>
                      <Text style={[styles.domainScore, { color: domain.color }]}>{domain.score}%</Text>
                    </View>
                    <View style={styles.domainBarBg}>
                      <MotiView from={{ width: 0 }} animate={{ width: Math.round((domain.score / 100) * barWidth) }}
                        transition={{ type: 'timing', duration: 900, delay: i * 80 }}
                        style={[styles.domainBarFill, { backgroundColor: domain.color }]} />
                    </View>
                    {domain.habits.length > 0 && (
                      <Text style={styles.domainHabits}>From: {domain.habits.slice(0, 2).join(', ')}{domain.habits.length > 2 ? ` +${domain.habits.length - 2}` : ''}</Text>
                    )}
                  </View>
                </View>
              </GlassCard>
            </MotiView>
          ))
        )}

        {/* 7-DAY MOOD TREND */}
        {checkinHistory.length > 0 && (
          <>
            <Text style={styles.sectionTitle}>7-DAY MOOD TREND</Text>
            <GlassCard style={styles.chartCard}><MoodChart data={checkinHistory} days={7} /></GlassCard>
          </>
        )}

        {/* RESTORATION */}
        <Text style={styles.sectionTitle}>RESTORATION STRATEGIES</Text>
        {[
          { icon: <Wind size={20} color={COLORS.primary} />, bg: 'rgba(51,255,214,0.1)', title: 'Neural Reset', desc: '10-min non-sleep deep rest protocol.', msg: 'Neural Reset initiated. Find a quiet space.' },
          { icon: <Coffee size={20} color={COLORS.gold} />, bg: 'rgba(251,191,36,0.1)', title: 'Dopamine Detox', desc: 'No social media or screens for 4 hours.', msg: 'Detox mode active — 4h low-stimulation protocol.' },
          { icon: <Moon size={20} color={COLORS.secondary} />, bg: 'rgba(167,139,250,0.1)', title: 'Sleep Optimiser', desc: 'Consistent bedtime for peak recovery.', msg: 'Sleep target set: Aim for 10:30 PM tonight.' },
        ].map((s, i) => (
          <TouchableOpacity key={i} onPress={() => toast(s.msg)} style={{ marginBottom: 10 }}>
            <GlassCard style={styles.stratCard}>
              <View style={[styles.stratIcon, { backgroundColor: s.bg }]}>{s.icon}</View>
              <View style={{ flex: 1 }}>
                <Text style={styles.stratTitle}>{s.title}</Text>
                <Text style={styles.stratDesc}>{s.desc}</Text>
              </View>
              <ChevronRight size={16} color={COLORS.textDim} />
            </GlassCard>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <Modal visible={showCheckin} animationType="slide" presentationStyle="pageSheet" onRequestClose={() => setShowCheckin(false)}>
        <View style={styles.modal}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Daily Life Check-In</Text>
            <TouchableOpacity onPress={() => setShowCheckin(false)}><Text style={styles.modalClose}>✕ Close</Text></TouchableOpacity>
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
  content: { padding: SPACING.margin, paddingBottom: 110 },
  toast: { position: 'absolute', top: 56, left: 16, right: 16, zIndex: 999, flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: 'rgba(15,23,42,0.97)', borderWidth: 1, borderColor: 'rgba(51,255,214,0.3)', borderRadius: 14, padding: 14, elevation: 8 },
  toastText: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 13, color: COLORS.text, flex: 1 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: SPACING.lg },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text },
  subtitle: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, marginTop: 4, fontSize: 13 },
  pulseCard: { padding: SPACING.lg, marginBottom: SPACING.md, borderColor: 'rgba(244,114,182,0.2)', borderWidth: 1 },
  pulseCardDone: { borderColor: 'rgba(51,255,214,0.25)' },
  pulseRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  pulseLabel: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 9, color: COLORS.textDim, letterSpacing: 2, marginBottom: 6 },
  pulseData: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  moodEmoji: { fontSize: 32 },
  moodText: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 16, color: COLORS.text },
  energyText: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 11, color: COLORS.textSecondary, marginTop: 2 },
  pulsePrompt: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 14, color: COLORS.textDim, fontStyle: 'italic' },
  checkinBtn: { flexDirection: 'row', alignItems: 'center', backgroundColor: COLORS.primary, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10 },
  checkinBtnDone: { backgroundColor: 'rgba(51,255,214,0.1)', borderWidth: 1, borderColor: 'rgba(51,255,214,0.3)' },
  checkinBtnText: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 12, color: COLORS.primary },
  scoreCard: { padding: SPACING.lg, marginBottom: SPACING.lg },
  scoreRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  scoreSub: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 9, color: COLORS.textDim, letterSpacing: 2 },
  scoreValue: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 48, color: COLORS.text },
  scoreMax: { fontSize: 18, color: COLORS.textDim },
  recoveryPill: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 6 },
  recoveryDot: { width: 8, height: 8, borderRadius: 4 },
  recoveryLabel: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 10, letterSpacing: 1 },
  miniBarBg: { height: 6, backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' },
  miniBarFill: { height: '100%', borderRadius: 3 },
  sectionTitle: { ...TYPOGRAPHY.label, color: COLORS.textDim, letterSpacing: 2, marginBottom: SPACING.md, marginTop: SPACING.md },
  emptyCard: { padding: SPACING.xl, alignItems: 'center' },
  emptyText: { ...TYPOGRAPHY.body, fontSize: 14, color: COLORS.textSecondary, textAlign: 'center' },
  domainCard: { padding: 14, marginBottom: 10 },
  domainRow: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  domainEmoji: { fontSize: 24 },
  domainHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  domainLabel: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 14, color: COLORS.text },
  domainScore: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 14 },
  domainBarBg: { height: 6, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 3, overflow: 'hidden', marginBottom: 4 },
  domainBarFill: { height: '100%', borderRadius: 3 },
  domainHabits: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 10, color: COLORS.textDim },
  chartCard: { padding: SPACING.md, marginBottom: SPACING.sm },
  stratCard: { flexDirection: 'row', alignItems: 'center', padding: 14, gap: 14 },
  stratIcon: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  stratTitle: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 14, color: COLORS.text },
  stratDesc: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 11, color: COLORS.textSecondary, marginTop: 2 },
  modal: { flex: 1, backgroundColor: COLORS.background },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 24, paddingTop: 20, paddingBottom: 16, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.07)' },
  modalTitle: { ...TYPOGRAPHY.h3, color: COLORS.text },
  modalClose: { ...TYPOGRAPHY.label, color: COLORS.textDim },
});
