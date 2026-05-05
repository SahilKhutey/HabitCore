import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, SafeAreaView,
  TouchableOpacity, RefreshControl, Dimensions
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { MotiView } from 'moti';
import {
  TrendingUp, TrendingDown, Target, Activity, Brain, Shield
} from 'lucide-react-native';

const { width } = Dimensions.get('window');

export default function IdentityScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [journeySummary, setJourneySummary] = useState<any>(null);
  const [patterns, setPatterns] = useState<any>(null);
  const [identityInsights, setIdentityInsights] = useState<any>(null);
  const { token } = useUserStore();

    const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [journey, patternRes, insightsRes] = await Promise.all([
        api('/identity/summary', 'GET', null, token),
        api('/psychological/behavior/patterns', 'GET', null, token),
        api('/psychological/identity-insights', 'GET', null, token),
      ]);
      setJourneySummary(journey);
      setPatterns(patternRes);
      setIdentityInsights(insightsRes);
    } catch (e) { console.error('Intelligence fetch error:', e); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = async () => { setRefreshing(true); await fetchData(); setRefreshing(false); };

  const IdentityPulseBar = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <View style={styles.pulseRow}>
      <View style={styles.pulseHeader}>
        <Text style={styles.pulseLabel}>{label}</Text>
        <Text style={styles.pulseValue}>{Math.round(value * 100)}%</Text>
      </View>
      <View style={styles.pulseBarBg}>
        <MotiView 
          from={{ width: 0 }}
          animate={{ width: `${value * 100}%` }}
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
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />}
      >
        <MotiView
          from={{ opacity: 0, translateY: 10 }}
          animate={{ opacity: 1, translateY: 0 }}
        >
          <Text style={styles.title}>Your Pattern</Text>
          <Text style={styles.subtitle}>Analyzing 30 days of behavioral evolution</Text>
        </MotiView>

        <GlassCard style={styles.mainCard}>
          <IdentityPulseBar 
            label="Discipline" 
            value={(journeySummary?.discipline_score || 0) / 100} 
            color={COLORS.identity.discipline} 
          />
          <IdentityPulseBar 
            label="Awareness" 
            value={0.8} 
            color={COLORS.identity.awareness} 
          />
          <IdentityPulseBar 
            label="Avoidance" 
            value={patterns?.burnout_score || 0} 
            color={COLORS.identity.avoidance} 
          />
        </GlassCard>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <TrendingUp size={16} color={COLORS.textDim} />
            <Text style={styles.sectionLabel}>Insights & Trends</Text>
          </View>
          
          <View style={styles.trendGrid}>
            {(identityInsights?.trends || []).map((trend: any, i: number) => (
              <GlassCard key={i} style={styles.trendItem}>
                <Text style={styles.trendVal}>{trend.value}</Text>
                <Text style={styles.trendLabel}>{trend.label}</Text>
              </GlassCard>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Shield size={16} color={COLORS.textDim} />
            <Text style={styles.sectionLabel}>Identity Alignment</Text>
          </View>
          
          <GlassCard style={styles.traitCard}>
            <Brain size={24} color={COLORS.primary} style={{ marginBottom: SPACING[4] }} />
            <Text style={styles.traitText}>
              {identityInsights?.top_trait || "“Analyzing your behavioral patterns to find your core alignment.”"}
            </Text>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>Verified Pattern</Text>
            </View>
          </GlassCard>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  content: { padding: SPACING[5], paddingTop: SPACING[10], paddingBottom: SPACING[12] },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text, marginBottom: SPACING[1] },
  subtitle: { ...TYPOGRAPHY.body, color: COLORS.textDim, fontSize: 14, marginBottom: SPACING[8] },
  mainCard: { 
    padding: SPACING[6], 
    borderRadius: RADIUS.xl, 
    gap: SPACING[8],
    backgroundColor: COLORS.surface
  },
  pulseRow: { gap: SPACING[3] },
  pulseHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  pulseLabel: { ...TYPOGRAPHY.h3, fontSize: 16, color: COLORS.text },
  pulseValue: { ...TYPOGRAPHY.caption, color: COLORS.textDim, fontWeight: '600' },
  pulseBarBg: { height: 8, backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: RADIUS.full, overflow: 'hidden' },
  pulseBarFill: { height: '100%', borderRadius: RADIUS.full },
  
  section: { marginTop: SPACING[10] },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: SPACING[2], marginBottom: SPACING[4] },
  sectionLabel: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 10, letterSpacing: 1.5 },
  
  trendGrid: { flexDirection: 'row', gap: SPACING[4] },
  trendItem: { 
    flex: 1, 
    padding: SPACING[5], 
    borderRadius: RADIUS.lg, 
    alignItems: 'center',
    backgroundColor: COLORS.surfaceLight 
  },
  trendVal: { ...TYPOGRAPHY.h2, color: COLORS.primary, fontSize: 20 },
  trendLabel: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 4 },
  
  traitCard: { 
    padding: SPACING[8], 
    borderRadius: RADIUS.xl, 
    alignItems: 'center',
    backgroundColor: COLORS.surface 
  },
  traitText: { ...TYPOGRAPHY.h3, color: COLORS.text, textAlign: 'center', lineHeight: 28, fontSize: 18 },
  badge: {
    marginTop: SPACING[6],
    paddingHorizontal: SPACING[4],
    paddingVertical: SPACING[1],
    borderRadius: RADIUS.full,
    backgroundColor: 'rgba(124, 140, 255, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(124, 140, 255, 0.2)'
  },
  badgeText: { ...TYPOGRAPHY.caption, color: COLORS.primary, fontWeight: '600', fontSize: 10 }
});
