import React, { useState, useEffect, useCallback } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  TouchableOpacity, 
  ScrollView,
  TextInput,
  RefreshControl,
  Alert,
  ActivityIndicator,
  Dimensions
} from 'react-native';

const { width } = Dimensions.get('window');
import { COLORS, SPACING, TYPOGRAPHY, RADIUS, SHADOWS } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { 
  Plus, Trash2, Clock, X, Brain, Sparkles, 
  Zap, Shield, Star
} from 'lucide-react-native';
import { MotiView, AnimatePresence } from 'moti';
import { triggerHaptic } from '../../src/utils/animationManager';

import { ArchetypeVisual } from '../../src/components/ArchetypeVisual';
import { EvolutionRing } from '../../src/components/EvolutionRing';

export default function StudioScreen() {
  const { token, level, xp, coins, setUserInfo } = useUserStore();
  const [avatar, setAvatar] = useState<any>(null);
  const [shopItems, setShopItems] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'avatar' | 'anchors' | 'routines' | 'journeys'>('avatar');

  const renderRoutinesSection = () => (
    <View style={styles.routinesSection}>
      <Text style={styles.sectionTitle}>ROUTINE PACKS</Text>
      <Text style={styles.shopSub}>Bundled behaviors for rapid alignment</Text>
      
      <TouchableOpacity style={styles.routineCard} onPress={() => handleInstallRoutine('morning_ritual')}>
        <GlassCard style={styles.routineInner}>
          <View style={styles.routineIcon}>
             <Clock size={24} color={COLORS.primary} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.routineTitle}>Morning Ritual</Text>
            <Text style={styles.routineMeta}>Sunlight, Meditation, Hydration</Text>
          </View>
          <View style={styles.routineAdd}>
            <Plus size={16} color="#FFF" />
          </View>
        </GlassCard>
      </TouchableOpacity>

      <TouchableOpacity style={styles.routineCard} onPress={() => handleInstallRoutine('deep_focus')}>
        <GlassCard style={styles.routineInner}>
          <View style={[styles.routineIcon, { backgroundColor: 'rgba(139, 164, 208, 0.1)' }]}>
             <Brain size={24} color="#8BA4D0" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.routineTitle}>Deep Focus</Text>
            <Text style={styles.routineMeta}>Phone Away, Pomodoro, Review</Text>
          </View>
          <View style={[styles.routineAdd, { backgroundColor: '#8BA4D0' }]}>
            <Plus size={16} color="#FFF" />
          </View>
        </GlassCard>
      </TouchableOpacity>
    </View>
  );

  const renderJourneysSection = () => (
    <View style={styles.journeysSection}>
      <Text style={styles.sectionTitle}>IDENTITY EVOLUTION</Text>
      <Text style={styles.shopSub}>Your path from Beginner to Elite</Text>

      <View style={styles.timeline}>
        {[
          { title: 'Beginner', desc: 'Establish the core discipline.', current: level >= 1 && level < 5 },
          { title: 'Builder', desc: 'Expand into complex behaviors.', current: level >= 5 && level < 10 },
          { title: 'Disciplined', desc: 'Consistent excellence.', current: level >= 10 && level < 20 },
          { title: 'Elite', desc: 'Ultimate behavioral mastery.', current: level >= 20 },
        ].map((step, i) => {
          const isCompleted = (i === 0 && level >= 5) || (i === 1 && level >= 10) || (i === 2 && level >= 20);
          return (
            <View key={step.title} style={styles.timelineStep}>
              <View style={styles.timelineLeft}>
                <View style={[
                  styles.timelineDot, 
                  step.current && styles.timelineDotActive,
                  isCompleted && { backgroundColor: COLORS.success }
                ]} />
                {i < 3 && <View style={styles.timelineLine} />}
              </View>
              <View style={styles.timelineContent}>
                <Text style={[
                  styles.timelineTitle, 
                  step.current && styles.timelineTitleActive,
                  isCompleted && { color: COLORS.success }
                ]}>
                  {step.title} {isCompleted && '✓'}
                </Text>
                <Text style={styles.timelineDesc}>{step.desc}</Text>
              </View>
            </View>
          );
        })}
      </View>
    </View>
  );
  
  const [habits, setHabits] = useState<any[]>([]);
  const [showAddHabit, setShowAddHabit] = useState(false);

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      setLoading(true);
      const [avatarRes, shopRes, habitRes] = await Promise.all([
        api('/api/avatar/', 'GET', null, token),
        api('/api/avatar/shop', 'GET', null, token),
        api('/habits/today/status', 'GET', null, token)
      ]);
      
      if (avatarRes?.success) {
        setAvatar(avatarRes.avatar);
        setUserInfo({
          level: avatarRes.avatar.level,
          xp: avatarRes.avatar.xp,
          coins: avatarRes.avatar.economy.coins
        });
      }
      if (shopRes?.success) setShopItems(shopRes.items);
      if (habitRes?.habits) setHabits(habitRes.habits);
      
    } catch (e) {
      console.error('Studio fetch error:', e);
    } finally {
      setLoading(false);
    }
  }, [token, setUserInfo]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const handlePurchase = async (itemId: string) => {
    try {
      triggerHaptic('impactMedium');
      const res = await api('/api/avatar/purchase', 'POST', { item_id: itemId }, token!);
      if (res.success) {
        triggerHaptic('success');
        Alert.alert('Success', res.message);
        fetchData();
      } else {
        triggerHaptic('error');
        Alert.alert('Purchase Failed', res.message);
      }
    } catch (e: any) {
      Alert.alert('Error', e.message);
    }
  };

  const handleInstallRoutine = async (packId: string) => {
    try {
      triggerHaptic('impactHeavy');
      setLoading(true);
      const res = await api(`/habits/routines/install/${packId}`, 'POST', null, token!);
      if (res.status === 'success') {
        triggerHaptic('success');
        Alert.alert('Protocol Installed', res.message);
        fetchData();
      }
    } catch (e: any) {
      Alert.alert('Error', e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteHabit = async (habitId: string) => {
    try {
      triggerHaptic('impactHeavy');
      const res = await api(`/habits/${habitId}`, 'DELETE', null, token!);
      if (res.success) {
        fetchData();
      }
    } catch (e: any) {
      console.error('Delete error:', e);
    }
  };

  const handleEquip = async (type: string, value: string | null) => {
    try {
      triggerHaptic('impactLight');
      const res = await api('/api/avatar/equip', 'POST', { item_type: type, item_value: value }, token!);
      if (res.success) {
        fetchData();
      }
    } catch (e: any) {
      console.error('Equip error:', e);
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity?.toLowerCase()) {
      case 'common': return COLORS.textDim;
      case 'rare': return COLORS.primary;
      case 'epic': return COLORS.identity.awareness;
      case 'legendary': return COLORS.warning;
      default: return COLORS.primary;
    }
  };

  const renderAvatarSection = () => (
    <View style={styles.avatarSection}>
      <GlassCard style={styles.characterStage}>
        <ArchetypeVisual archetype={avatar?.archetype || 'pioneer'} />
        
        <View style={styles.archetypeContainer}>
           <EvolutionRing 
             progress={avatar?.evolution_progress || 0.3} 
             size={160} 
             strokeWidth={4}
             color={getRarityColor(avatar?.rarity || 'common')}
           >
             <MotiView
               from={{ scale: 0.8, opacity: 0 }}
               animate={{ scale: 1, opacity: 1 }}
               transition={{ type: 'spring', delay: 200 }}
               style={styles.avatarCircle}
             >
               <Text style={styles.avatarEmoji}>
                 {avatar?.archetype === 'monk' ? '🧘' : (avatar?.archetype === 'pioneer' ? '⚡' : (avatar?.archetype === 'sage' ? '🧠' : '🚀'))}
               </Text>
             </MotiView>
           </EvolutionRing>
        </View>
        
        <View style={styles.characterInfo}>
          <Text style={styles.characterName}>{avatar?.archetype?.toUpperCase() || 'PIONEER'}</Text>
          <View style={styles.stageBadge}>
            <Text style={styles.characterStageText}>STAGE {avatar?.evolution_stage || 1}</Text>
          </View>
        </View>
      </GlassCard>

      <Text style={styles.sectionTitle}>EQUIPPED LOADOUT</Text>
      <View style={styles.equippedGrid}>
        {['skin', 'outfit', 'aura', 'accessory'].map((type) => (
          <View key={type} style={styles.equippedSlot}>
            <TouchableOpacity 
              style={styles.slotBox}
              onPress={() => handleEquip(type, avatar?.appearance[type] ? null : 'equipped')}
            >
              <Text style={styles.slotText}>{avatar?.appearance[type] ? '✓' : '+'}</Text>
              {avatar?.appearance[type] && <View style={[styles.slotIndicator, { backgroundColor: COLORS.primary }]} />}
            </TouchableOpacity>
            <Text style={styles.slotLabel}>{type.toUpperCase()}</Text>
          </View>
        ))}
      </View>

      <View style={styles.shopHeader}>
        <Text style={styles.sectionTitle}>THE FORGE</Text>
        <Text style={styles.shopSub}>Acquire behavioral enhancements</Text>
      </View>
      
      <View style={styles.shopGrid}>
        {shopItems.map((item, i) => (
          <MotiView 
            key={item.id}
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            transition={{ delay: i * 50 }}
          >
            <TouchableOpacity 
              style={styles.shopCard}
              onPress={() => handlePurchase(item.id)}
              disabled={coins < item.price}
            >
              <GlassCard style={[styles.itemIconBox, coins < item.price && { opacity: 0.4 }]}>
                <View style={[styles.rarityCorner, { backgroundColor: getRarityColor(item.rarity) }]} />
                <Sparkles size={24} color={getRarityColor(item.rarity)} />
                {item.stats?.xp_boost > 0 && (
                  <View style={styles.statBadge}>
                    <Zap size={8} color={COLORS.warning} />
                    <Text style={styles.statBadgeText}>+{item.stats.xp_boost}% XP</Text>
                  </View>
                )}
              </GlassCard>
              <View style={styles.itemMeta}>
                <Text style={styles.itemName} numberOfLines={1}>{item.name}</Text>
                <View style={styles.priceTag}>
                  <Text style={[styles.priceText, coins < item.price && { color: COLORS.danger }]}>{item.price} 🪙</Text>
                </View>
              </View>
            </TouchableOpacity>
          </MotiView>
        ))}
      </View>
    </View>
  );

  const renderAnchorsSection = () => (
    <View style={styles.anchorsSection}>
       <View style={styles.habitHeader}>
          <View>
            <Text style={styles.sectionTitle}>BEHAVIORAL ANCHORS</Text>
            <Text style={styles.shopSub}>Your identity's structural integrity</Text>
          </View>
          <TouchableOpacity 
            style={styles.addButton}
            onPress={() => { triggerHaptic('impactLight'); fetchData(); }}
          >
            <Plus size={20} color={COLORS.text} />
          </TouchableOpacity>
       </View>
       
       {habits.length === 0 ? (
         <View style={styles.emptyAnchors}>
            <Brain size={48} color={COLORS.surfaceLight} />
            <Text style={styles.emptyText}>No anchors active yet.</Text>
         </View>
       ) : habits.map((h, i) => (
         <MotiView
           key={h.id}
           from={{ opacity: 0, translateX: -10 }}
           animate={{ opacity: 1, translateX: 0 }}
           transition={{ delay: i * 100 }}
         >
           <GlassCard style={styles.habitItem}>
              <View style={styles.habitIconBox}>
                <Clock size={16} color={COLORS.primary} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.habitName}>{h.name}</Text>
                <Text style={styles.habitMeta}>{h.time || 'Anytime'} • {(h.domain || 'mental').toUpperCase()}</Text>
              </View>
              <TouchableOpacity onPress={() => handleDeleteHabit(h.id)}>
                <Trash2 size={16} color={COLORS.danger} opacity={0.6} />
              </TouchableOpacity>
           </GlassCard>
         </MotiView>
       ))}
    </View>
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
            <Text style={styles.title}>Evolve</Text>
            <Text style={styles.subtitle}>Align your avatar with your actions.</Text>
          </View>
          <GlassCard style={styles.balanceBox}>
            <Text style={styles.balanceText}>{coins} 🪙</Text>
          </GlassCard>
        </View>

        <View style={styles.tabContainer}>
          <TouchableOpacity 
            style={[styles.tab, activeTab === 'avatar' && styles.activeTab]}
            onPress={() => { triggerHaptic('impactLight'); setActiveTab('avatar'); }}
          >
            <Text style={[styles.tabText, activeTab === 'avatar' && styles.activeTabText]}>Avatar</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.tab, activeTab === 'anchors' && styles.activeTab]}
            onPress={() => { triggerHaptic('impactLight'); setActiveTab('anchors'); }}
          >
            <Text style={[styles.tabText, activeTab === 'anchors' && styles.activeTabText]}>Anchors</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.tab, activeTab === 'routines' && styles.activeTab]}
            onPress={() => { triggerHaptic('impactLight'); setActiveTab('routines'); }}
          >
            <Text style={[styles.tabText, activeTab === 'routines' && styles.activeTabText]}>Routines</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.tab, activeTab === 'journeys' && styles.activeTab]}
            onPress={() => { triggerHaptic('impactLight'); setActiveTab('journeys'); }}
          >
            <Text style={[styles.tabText, activeTab === 'journeys' && styles.activeTabText]}>Journeys</Text>
          </TouchableOpacity>
        </View>

        {activeTab === 'avatar' && renderAvatarSection()}
        {activeTab === 'anchors' && renderAnchorsSection()}
        {activeTab === 'routines' && renderRoutinesSection()}
        {activeTab === 'journeys' && renderJourneysSection()}

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
    marginBottom: SPACING[6],
    paddingTop: SPACING[4]
  },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text },
  subtitle: { ...TYPOGRAPHY.body, color: COLORS.textDim, fontSize: 14, marginTop: 4 },
  balanceBox: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: RADIUS.full, backgroundColor: 'rgba(124, 140, 255, 0.1)' },
  balanceText: { ...TYPOGRAPHY.label, color: COLORS.primary, fontSize: 12 },

  tabContainer: { flexDirection: 'row', gap: SPACING[4], marginBottom: SPACING[8] },
  tab: { paddingVertical: 8, paddingHorizontal: 4, borderBottomWidth: 2, borderBottomColor: 'transparent' },
  activeTab: { borderBottomColor: COLORS.primary },
  tabText: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 13 },
  activeTabText: { color: COLORS.text },

  avatarSection: { gap: SPACING[6] },
  characterStage: { 
    height: 320,
    alignItems: 'center', 
    justifyContent: 'center',
    borderRadius: RADIUS.xl, 
    backgroundColor: COLORS.surface,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
    ...SHADOWS.card
  },
  archetypeContainer: {
    zIndex: 1,
  },
  avatarCircle: { 
    width: 130, 
    height: 130, 
    borderRadius: 65, 
    backgroundColor: COLORS.surfaceLight, 
    alignItems: 'center', 
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255,255,255,0.1)',
    ...SHADOWS.glowPrimary
  },
  avatarEmoji: { fontSize: 50 },
  characterInfo: { alignItems: 'center', marginTop: SPACING[6], zIndex: 1 },
  characterName: { ...TYPOGRAPHY.h2, color: COLORS.text, letterSpacing: 4, fontSize: 28 },
  stageBadge: {
    marginTop: 8,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: RADIUS.sm,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)'
  },
  characterStageText: { ...TYPOGRAPHY.label, color: COLORS.primary, fontSize: 10, letterSpacing: 2 },

  sectionTitle: { ...TYPOGRAPHY.label, color: COLORS.text, fontSize: 11, letterSpacing: 2 },
  shopSub: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 2 },
  equippedGrid: { flexDirection: 'row', gap: SPACING[3], marginTop: SPACING[2] },
  equippedSlot: { flex: 1, alignItems: 'center', gap: 8 },
  slotBox: { width: '100%', aspectRatio: 1, borderRadius: RADIUS.lg, backgroundColor: COLORS.surface, alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: COLORS.border },
  slotText: { color: COLORS.textDim, fontSize: 20 },
  slotLabel: { ...TYPOGRAPHY.caption, fontSize: 8, letterSpacing: 1 },
  slotIndicator: { position: 'absolute', bottom: 8, width: 4, height: 4, borderRadius: 2 },

  shopHeader: { marginTop: SPACING[4] },
  shopGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: SPACING[4], marginTop: SPACING[4] },
  shopCard: { width: (width - SPACING[5] * 2 - SPACING[4]) / 2, gap: 12 },
  itemIconBox: { 
    width: '100%', 
    aspectRatio: 1, 
    borderRadius: RADIUS.xl, 
    alignItems: 'center', 
    justifyContent: 'center', 
    backgroundColor: COLORS.surfaceLight,
    overflow: 'hidden'
  },
  rarityCorner: {
    position: 'absolute',
    top: -15,
    right: -15,
    width: 30,
    height: 30,
    transform: [{ rotate: '45deg' }],
    opacity: 0.8
  },
  statBadge: {
    position: 'absolute',
    bottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: RADIUS.sm,
    backgroundColor: 'rgba(0,0,0,0.3)',
  },
  statBadgeText: { ...TYPOGRAPHY.label, fontSize: 8, color: COLORS.text },
  itemMeta: { gap: 2 },
  itemName: { ...TYPOGRAPHY.h3, fontSize: 14, color: COLORS.text },
  priceTag: { flexDirection: 'row', alignItems: 'center' },
  priceText: { ...TYPOGRAPHY.label, fontSize: 11, color: COLORS.warning },

  anchorsSection: { gap: SPACING[5] },
  habitHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: SPACING[2] },
  addButton: { width: 36, height: 36, borderRadius: 18, backgroundColor: COLORS.primary, alignItems: 'center', justifyContent: 'center' },
  habitItem: { flexDirection: 'row', alignItems: 'center', padding: SPACING[4], borderRadius: RADIUS.lg, backgroundColor: COLORS.surface, gap: SPACING[4] },
  habitIconBox: { width: 32, height: 32, borderRadius: 8, backgroundColor: 'rgba(124, 140, 255, 0.1)', alignItems: 'center', justifyContent: 'center' },
  habitName: { ...TYPOGRAPHY.h3, color: COLORS.text, fontSize: 16 },
  habitMeta: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 2, letterSpacing: 0.5 },
  emptyAnchors: { height: 200, alignItems: 'center', justifyContent: 'center', gap: 16 },
  emptyText: { ...TYPOGRAPHY.body, color: COLORS.textDim },

  routinesSection: { gap: SPACING[4], marginTop: SPACING[2] },
  routineCard: { marginBottom: SPACING[2] },
  routineInner: { flexDirection: 'row', alignItems: 'center', padding: SPACING[4], borderRadius: RADIUS.lg, backgroundColor: COLORS.surface, gap: SPACING[4] },
  routineIcon: { width: 48, height: 48, borderRadius: 12, backgroundColor: 'rgba(109, 186, 157, 0.1)', alignItems: 'center', justifyContent: 'center' },
  routineTitle: { ...TYPOGRAPHY.h3, color: COLORS.text, fontSize: 16 },
  routineMeta: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 2 },
  routineAdd: { width: 32, height: 32, borderRadius: 16, backgroundColor: COLORS.primary, alignItems: 'center', justifyContent: 'center' },

  journeysSection: { gap: SPACING[6], marginTop: SPACING[2] },
  timeline: { marginTop: SPACING[4], paddingLeft: SPACING[2] },
  timelineStep: { flexDirection: 'row', gap: SPACING[4], minHeight: 80 },
  timelineLeft: { alignItems: 'center', width: 20 },
  timelineDot: { width: 12, height: 12, borderRadius: 6, backgroundColor: '#E5E7EB', zIndex: 1 },
  timelineDotActive: { backgroundColor: COLORS.primary, width: 16, height: 16, borderRadius: 8, borderWidth: 3, borderColor: 'rgba(109, 186, 157, 0.2)' },
  timelineLine: { position: 'absolute', top: 12, width: 2, height: '100%', backgroundColor: '#E5E7EB' },
  timelineContent: { flex: 1, paddingTop: 0 },
  timelineTitle: { ...TYPOGRAPHY.h3, color: COLORS.textDim, fontSize: 16 },
  timelineTitleActive: { color: COLORS.text, fontWeight: '700' },
  timelineDesc: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 4, lineHeight: 18 }
});
