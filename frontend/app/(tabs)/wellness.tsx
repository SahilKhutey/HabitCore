import React, { useState, useEffect, useCallback } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  SafeAreaView, 
  RefreshControl,
  TouchableOpacity
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { 
  Heart, 
  Wind, 
  Moon, 
  Sun, 
  Coffee,
  Activity,
  ChevronRight
} from 'lucide-react-native';
import { MotiView } from 'moti';
import { useRouter } from 'expo-router';
import { triggerHaptic } from '../../src/utils/animationManager';

export default function WellnessScreen() {
  const router = useRouter();
  const { token } = useUserStore();
  const [refreshing, setRefreshing] = useState(false);
  const [domains, setDomains] = useState<any[]>([]);
  const [overall, setOverall] = useState(0);

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const res = await api('/psychological/life-domains', 'GET', null, token);
      if (res.success) {
        setDomains(res.domains);
        setOverall(res.overall_score);
      }
    } catch (e) {
      console.error('Wellness fetch error:', e);
    }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const DomainCard = ({ domain, score, emoji, color, label, habits }: any) => (
    <GlassCard style={styles.domainCard}>
      <View style={styles.domainHeader}>
        <Text style={styles.domainEmoji}>{emoji}</Text>
        <Text style={styles.domainLabel}>{label}</Text>
        <Text style={[styles.domainScore, { color }]}>{score}%</Text>
      </View>
      <View style={styles.domainBarBg}>
        <MotiView 
          from={{ width: 0 }}
          animate={{ width: `${score}%` }}
          style={[styles.domainBarFill, { backgroundColor: color }]} 
        />
      </View>
      {habits && habits.length > 0 && (
        <View style={styles.habitsList}>
          {habits.map((h: string, idx: number) => (
            <Text key={idx} style={styles.habitItem}>• {h}</Text>
          ))}
        </View>
      )}
    </GlassCard>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView 
        style={styles.container} 
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />}
      >
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>Wellness</Text>
            <Text style={styles.subtitle}>Holistic behavioral balance.</Text>
          </View>
          <TouchableOpacity style={styles.overallBox} onPress={onRefresh}>
             <Text style={styles.overallLabel}>OVERALL</Text>
             <Text style={styles.overallVal}>{overall}%</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity 
          style={styles.checkinCTA}
          onPress={() => router.push('/reflection' as any)}
        >
          <GlassCard style={styles.checkinCTAInner}>
            <View style={styles.checkinIconBox}>
              <Heart color={COLORS.primary} size={24} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.checkinTitle}>Daily Alignment Check-in</Text>
              <Text style={styles.checkinSub}>Update your mood, sleep, and energy</Text>
            </View>
            <ChevronRight color={COLORS.textDim} size={20} />
          </GlassCard>
        </TouchableOpacity>

        <View style={styles.infoSectionTop}>
          <Text style={styles.infoTextTop}>
            Scores are calculated based on your habit completions over the last 7 days and your daily check-in responses. 
            You can explicitly assign habits to domains in the Studio or Today tab.
          </Text>
        </View>

        <View style={styles.domainGrid}>
          {domains.map((d, i) => (
            <MotiView 
              key={d.domain}
              from={{ opacity: 0, translateY: 10 }}
              animate={{ opacity: 1, translateY: 0 }}
              transition={{ delay: i * 100 }}
            >
              <DomainCard {...d} />
            </MotiView>
          ))}
          {domains.length === 0 && (
            <Text style={styles.emptyText}>Analyzing life domains from your activity logs...</Text>
          )}
        </View>

        <View style={styles.infoSection}>
           <Text style={styles.sectionTitle}>Equilibrium Analysis</Text>
           <GlassCard style={styles.infoCard}>
              <Activity color={COLORS.primary} size={20} />
              <Text style={styles.infoText}>
                Your physical and mental domains are currently decoupled. Try syncing your workouts with your reflection window to improve cognitive integration.
              </Text>
           </GlassCard>
        </View>

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
    marginBottom: SPACING[10],
    paddingTop: SPACING[4]
  },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text },
  subtitle: { ...TYPOGRAPHY.body, color: COLORS.textDim, fontSize: 14, marginTop: 4 },
  overallBox: { alignItems: 'center', backgroundColor: COLORS.surface, padding: 12, borderRadius: RADIUS.lg, borderWidth: 1, borderColor: COLORS.border },
  overallLabel: { ...TYPOGRAPHY.label, fontSize: 8, color: COLORS.textDim, letterSpacing: 1.5 },
  overallVal: { ...TYPOGRAPHY.h3, color: COLORS.primary, marginTop: 2, fontSize: 18 },
  
  domainGrid: { gap: SPACING[4] },
  domainCard: { padding: SPACING[5], borderRadius: RADIUS.xl, backgroundColor: COLORS.surface },
  domainHeader: { flexDirection: 'row', alignItems: 'center', gap: SPACING[3], marginBottom: SPACING[4] },
  domainEmoji: { fontSize: 20 },
  domainLabel: { ...TYPOGRAPHY.h3, color: COLORS.text, flex: 1, fontSize: 16 },
  domainScore: { ...TYPOGRAPHY.label, fontSize: 14, fontWeight: '700' },
  domainBarBg: { height: 6, backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: RADIUS.full, overflow: 'hidden' },
  domainBarFill: { height: '100%', borderRadius: RADIUS.full },
  habitsList: { marginTop: SPACING[4], gap: 4 },
  habitItem: { ...TYPOGRAPHY.caption, color: COLORS.textDim, fontSize: 12 },
  
  infoSectionTop: { marginBottom: SPACING[8], padding: SPACING[2] },
  infoTextTop: { ...TYPOGRAPHY.body, color: COLORS.textDim, fontSize: 13, lineHeight: 20, fontStyle: 'italic' },

  infoSection: { marginTop: SPACING[10] },
  sectionTitle: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 10, letterSpacing: 2, marginBottom: SPACING[4] },
  infoCard: { padding: SPACING[6], borderRadius: RADIUS.xl, flexDirection: 'row', gap: SPACING[4], backgroundColor: COLORS.surfaceLight },
  infoText: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, flex: 1, fontSize: 14, lineHeight: 22 },
  emptyText: { ...TYPOGRAPHY.body, color: COLORS.textDim, textAlign: 'center', marginTop: 40 },
  checkinCTA: { marginBottom: SPACING[6] },
  checkinCTAInner: { flexDirection: 'row', alignItems: 'center', padding: SPACING[5], borderRadius: RADIUS.xl, gap: SPACING[4], backgroundColor: COLORS.surface },
  checkinIconBox: { width: 48, height: 48, borderRadius: RADIUS.lg, backgroundColor: 'rgba(124, 140, 255, 0.1)', alignItems: 'center', justifyContent: 'center' },
  checkinTitle: { ...TYPOGRAPHY.h3, color: COLORS.text },
  checkinSub: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 2 }
});
