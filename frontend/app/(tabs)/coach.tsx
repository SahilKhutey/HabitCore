import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  TouchableOpacity,
  RefreshControl,
  Dimensions,
  TextInput
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS, SHADOWS } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { 
  Brain, 
  TrendingUp, 
  Lightbulb, 
  Zap, 
  ChevronRight, 
  Heart,
  Activity,
  AlertTriangle,
  Sparkles
} from 'lucide-react-native';
import { MotiView } from 'moti';
import { triggerHaptic } from '../../src/utils/animationManager';

const { width } = Dimensions.get('window');

export default function CoachScreen() {
  const { token } = useUserStore();
  const [refreshing, setRefreshing] = useState(false);
  const [patterns, setPatterns] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [challenge, setChallenge] = useState<any>(null);
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<any[]>([
    { role: 'assistant', content: 'Cognitive state analyzed. How can I optimize your behavioral trajectory today?' }
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [patternRes, recRes, challengeRes] = await Promise.all([
        api('/psychological/behavior/patterns', 'GET', null, token),
        api('/analytics/recommendations', 'GET', null, token),
        api('/psychological/daily-challenge', 'GET', null, token),
      ]);
      setPatterns(patternRes);
      setRecommendations(recRes);
      setChallenge(challengeRes?.challenge);
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

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    
    const userMsg = chatInput;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatInput('');
    setIsTyping(true);
    triggerHaptic('impactLight');

    // Mock AI delay
    setTimeout(() => {
      setIsTyping(false);
      triggerHaptic('impactMedium');
      let response = "I've logged your input. Based on your current domain scores, I recommend focusing on structural consistency rather than intensity.";
      if (userMsg.toLowerCase().includes('physical')) response = "Physical domain is at 43%. A 20-minute zone 2 cardio session would restore your baseline without depleting cognitive reserves.";
      if (userMsg.toLowerCase().includes('mental')) response = "Mental domain is optimal at 86%. This is a high-leverage window for complex problem solving or creative synthesis.";
      
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    }, 1500);
  };

  const burnout = patterns?.burnout_score ?? 0;
  const burnoutLevel = burnout > 0.7 ? 'Critical' : burnout > 0.4 ? 'Elevated' : 'Stable';
  const burnoutColor = burnout > 0.7 ? COLORS.danger : burnout > 0.4 ? COLORS.warning : COLORS.success;

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />}
      >
        {/* Header */}
        <MotiView from={{ opacity: 0, translateY: -10 }} animate={{ opacity: 1, translateY: 0 }}>
          <View style={styles.header}>
            <View>
              <Text style={styles.title}>Cognitive Coach</Text>
              <Text style={styles.subtitle}>Real-time behavioral optimization.</Text>
            </View>
            <View style={styles.aiBadge}>
              <Brain size={18} color={COLORS.primary} />
              <Text style={styles.aiBadgeText}>AI LIVE</Text>
            </View>
          </View>
        </MotiView>

        {/* Burnout Risk Card */}
        <MotiView from={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 100 }}>
          <GlassCard style={styles.burnoutCard}>
            <View style={styles.cardHeader}>
              <Activity size={18} color={burnoutColor} />
              <Text style={[styles.cardTitle, { color: burnoutColor }]}>COGNITIVE LOAD</Text>
            </View>
            <View style={styles.burnoutMain}>
               <Text style={styles.burnoutValue}>{burnoutLevel}</Text>
               <Text style={styles.burnoutDesc}>
                 {burnout > 0.7 ? "High risk of ego depletion. Prioritize rest over discipline today." : 
                  burnout > 0.4 ? "Moderate mental fatigue detected. Focus on one high-leverage task." : 
                  "Mental resources optimal. Ideal for deep architectural work."}
               </Text>
            </View>
            <View style={styles.progressBarBg}>
               <View style={[styles.progressBarFill, { width: `${burnout * 100}%`, backgroundColor: burnoutColor }]} />
            </View>
          </GlassCard>
        </MotiView>

        {/* Daily Challenge */}
        {challenge && (
          <MotiView from={{ opacity: 0, translateY: 10 }} animate={{ opacity: 1, translateY: 0 }} transition={{ delay: 200 }}>
            <GlassCard style={styles.challengeCard}>
              <View style={styles.cardHeader}>
                <Zap size={18} color={COLORS.warning} />
                <Text style={[styles.cardTitle, { color: COLORS.warning }]}>DAILY STIMULUS</Text>
                <View style={styles.xpPill}>
                  <Text style={styles.xpPillText}>+{challenge.xp_reward || 50} XP</Text>
                </View>
              </View>
              <Text style={styles.challengeName}>{challenge.challenge}</Text>
              <Text style={styles.challengeDesc}>{challenge.description}</Text>
              <TouchableOpacity style={styles.actionBtn}>
                <Text style={styles.actionText}>Accept Integration</Text>
                <ChevronRight size={14} color={COLORS.warning} />
              </TouchableOpacity>
            </GlassCard>
          </MotiView>
        )}

        {/* Recommendations */}
        <MotiView from={{ opacity: 0, translateY: 10 }} animate={{ opacity: 1, translateY: 0 }} transition={{ delay: 300 }}>
          <Text style={styles.sectionLabel}>System Recommendations</Text>
          <GlassCard style={styles.recCard}>
            {recommendations?.insights?.map((ins: string, i: number) => (
              <View key={i} style={styles.recRow}>
                <Sparkles size={16} color={COLORS.primary} style={{ marginTop: 2 }} />
                <Text style={styles.recText}>{ins}</Text>
              </View>
            ))}
            {(!recommendations?.insights || recommendations.insights.length === 0) && (
              <Text style={styles.emptyText}>Analyzing your behavioral data to generate optimizations...</Text>
            )}
          </GlassCard>
        </MotiView>

        {/* Chat Section */}
        <MotiView from={{ opacity: 0, translateY: 20 }} animate={{ opacity: 1, translateY: 0 }} transition={{ delay: 400 }}>
          <Text style={[styles.sectionLabel, { marginTop: SPACING[10] }]}>Direct Intelligence</Text>
          <GlassCard style={styles.chatCard}>
            <View style={styles.chatHeader}>
              <View style={styles.activeDot} />
              <Text style={styles.chatTitle}>Behavioral Synthesis</Text>
            </View>
            
            <ScrollView style={styles.chatHistory} contentContainerStyle={{ gap: 12 }}>
              {messages.map((m, i) => (
                <MotiView 
                  key={i} 
                  from={{ opacity: 0, translateX: m.role === 'user' ? 10 : -10 }}
                  animate={{ opacity: 1, translateX: 0 }}
                  style={[styles.chatBubble, m.role === 'user' && styles.userBubble]}
                >
                  <Text style={[styles.chatBubbleText, m.role === 'user' && { color: '#FFF' }]}>{m.content}</Text>
                </MotiView>
              ))}
              {isTyping && (
                <Text style={styles.typingIndicator}>AI is thinking...</Text>
              )}
            </ScrollView>

            <View style={styles.chatInputContainer}>
              <TextInput 
                placeholder="Ask about your patterns..."
                placeholderTextColor={COLORS.textDim}
                style={styles.chatInput}
                value={chatInput}
                onChangeText={setChatInput}
                onSubmitEditing={handleSendMessage}
              />
              <TouchableOpacity style={styles.chatSendBtn} onPress={handleSendMessage}>
                <Zap size={16} color="#FFF" />
              </TouchableOpacity>
            </View>
          </GlassCard>
        </MotiView>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  content: { padding: SPACING[5], paddingBottom: 100 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING[8],
    paddingTop: SPACING[4]
  },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text },
  subtitle: { ...TYPOGRAPHY.body, color: COLORS.textDim, fontSize: 14, marginTop: 4 },
  aiBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: 'rgba(124, 140, 255, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: RADIUS.full,
    borderWidth: 1,
    borderColor: 'rgba(124, 140, 255, 0.2)'
  },
  aiBadgeText: { ...TYPOGRAPHY.label, color: COLORS.primary, fontSize: 10, letterSpacing: 1 },

  burnoutCard: { padding: SPACING[6], borderRadius: RADIUS.xl, marginBottom: SPACING[6], backgroundColor: COLORS.surface },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: SPACING[2], marginBottom: SPACING[4] },
  cardTitle: { ...TYPOGRAPHY.label, fontSize: 10, letterSpacing: 1.5 },
  burnoutMain: { marginBottom: SPACING[6] },
  burnoutValue: { ...TYPOGRAPHY.h1, fontSize: 28, color: COLORS.text, marginBottom: SPACING[1] },
  burnoutDesc: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, fontSize: 14, lineHeight: 22 },
  progressBarBg: { height: 4, backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: RADIUS.full, overflow: 'hidden' },
  progressBarFill: { height: '100%', borderRadius: RADIUS.full },

  challengeCard: { padding: SPACING[6], borderRadius: RADIUS.xl, marginBottom: SPACING[10], backgroundColor: COLORS.surface },
  xpPill: { marginLeft: 'auto', backgroundColor: 'rgba(251, 191, 36, 0.1)', paddingHorizontal: 10, paddingVertical: 4, borderRadius: RADIUS.full },
  xpPillText: { ...TYPOGRAPHY.label, color: COLORS.warning, fontSize: 10 },
  challengeName: { ...TYPOGRAPHY.h2, fontSize: 20, color: COLORS.text, marginBottom: SPACING[2] },
  challengeDesc: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, fontSize: 14, lineHeight: 22 },
  actionBtn: { flexDirection: 'row', alignItems: 'center', marginTop: SPACING[6], gap: SPACING[2] },
  actionText: { ...TYPOGRAPHY.label, color: COLORS.warning, fontSize: 12, textTransform: 'none' },

  sectionLabel: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 10, letterSpacing: 2, marginBottom: SPACING[4] },
  recCard: { padding: SPACING[6], borderRadius: RADIUS.xl, gap: SPACING[5], backgroundColor: COLORS.surfaceLight },
  recRow: { flexDirection: 'row', gap: SPACING[4], alignItems: 'flex-start' },
  recText: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, fontSize: 14, lineHeight: 22, flex: 1 },
  emptyText: { ...TYPOGRAPHY.body, color: COLORS.textDim, textAlign: 'center', paddingVertical: 20 },

  chatCard: { padding: SPACING[5], borderRadius: RADIUS.xl, backgroundColor: COLORS.surface },
  chatHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: SPACING[4] },
  activeDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#10B981' },
  chatTitle: { ...TYPOGRAPHY.label, fontSize: 10, color: COLORS.textDim, letterSpacing: 1 },
  chatBubble: {
    backgroundColor: 'rgba(124, 140, 255, 0.05)',
    padding: SPACING[4],
    borderRadius: RADIUS.lg,
    borderBottomLeftRadius: 0,
    marginBottom: SPACING[6]
  },
  chatBubbleText: { ...TYPOGRAPHY.body, color: COLORS.text, fontSize: 14, lineHeight: 22 },
  userBubble: {
    backgroundColor: COLORS.primary,
    alignSelf: 'flex-end',
    borderBottomLeftRadius: RADIUS.lg,
    borderBottomRightRadius: 0
  },
  chatHistory: { maxHeight: 300, marginBottom: SPACING[4] },
  typingIndicator: { ...TYPOGRAPHY.caption, color: COLORS.textDim, fontStyle: 'italic', marginLeft: 4 },
  chatInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING[3],
    backgroundColor: '#F3F4F6',
    borderRadius: RADIUS.full,
    paddingLeft: SPACING[5],
    paddingRight: SPACING[2],
    height: 48,
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  chatInput: { flex: 1, color: COLORS.text, fontSize: 14 },
  chatSendBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center'
  }
});
