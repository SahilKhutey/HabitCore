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
  ActivityIndicator
} from 'react-native';
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

export default function StudioScreen() {
  const { token, level, xp, coins, setUserInfo } = useUserStore();
  const [avatar, setAvatar] = useState<any>(null);
  const [shopItems, setShopItems] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'avatar' | 'anchors'>('avatar');
  
  // Habits state (previously in this file)
  const [habits, setHabits] = useState<any[]>([]);
  const [showAddHabit, setShowAddHabit] = useState(false);
  const [newName, setNewName] = useState('');

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
        // Sync global store
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

  const renderAvatarSection = () => (
    <View style={styles.avatarSection}>
      <GlassCard style={styles.characterStage}>
        <View style={styles.archetypeContainer}>
           <MotiView
             from={{ scale: 0.5, opacity: 0 }}
             animate={{ scale: 1, opacity: 1 }}
             transition={{ type: 'spring' }}
             style={styles.avatarCircle}
           >
             <Text style={styles.avatarEmoji}>
               {avatar?.archetype === 'pioneer' ? '⚡' : (avatar?.archetype === 'sage' ? '🧘' : '🚀')}
             </Text>
             {avatar?.appearance?.aura && (
               <MotiView 
                 from={{ opacity: 0, scale: 0.8 }}
                 animate={{ opacity: 1, scale: 1.2 }}
                 transition={{ loop: true, type: 'timing', duration: 2000 }}
                 style={[styles.aura, { borderColor: avatar.appearance.aura.includes('Fire') ? COLORS.danger : COLORS.primary }]}
               />
             )}
           </MotiView>
        </View>
        
        <View style={styles.characterInfo}>
          <Text style={styles.characterName}>{avatar?.archetype?.toUpperCase() || 'PIONEER'}</Text>
          <Text style={styles.characterStageText}>Evolution Stage {avatar?.evolution_stage || 1}</Text>
        </View>
      </GlassCard>

      <Text style={styles.sectionTitle}>EQUIPPED ITEMS</Text>
      <View style={styles.equippedGrid}>
        {['skin', 'outfit', 'aura', 'accessory'].map((type) => (
          <View key={type} style={styles.equippedSlot}>
            <View style={styles.slotBox}>
              <Text style={styles.slotText}>{avatar?.appearance[type] ? '✓' : '+'}</Text>
            </View>
            <Text style={styles.slotLabel}>{type.toUpperCase()}</Text>
          </View>
        ))}
      </View>

      <Text style={styles.sectionTitle}>THE FORGE</Text>
      <View style={styles.shopGrid}>
        {shopItems.map((item, i) => (
          <MotiView 
            key={item.id}
            from={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 100 }}
          >
            <TouchableOpacity 
              style={styles.shopCard}
              onPress={() => handlePurchase(item.id)}
              disabled={coins < item.price}
            >
              <GlassCard style={[styles.itemIconBox, coins < item.price && { opacity: 0.5 }]}>
                <Sparkles size={20} color={COLORS.primary} />
              </GlassCard>
              <Text style={styles.itemName} numberOfLines={1}>{item.name}</Text>
              <View style={styles.priceTag}>
                <Text style={styles.priceText}>{item.price} 🪙</Text>
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
          <Text style={styles.sectionTitle}>BEHAVIORAL ANCHORS</Text>
          <TouchableOpacity onPress={() => setShowAddHabit(!showAddHabit)}>
            <Plus size={20} color={COLORS.primary} />
          </TouchableOpacity>
       </View>
       
       {habits.map((h, i) => (
         <GlassCard key={h.id} style={styles.habitItem}>
            <View style={{ flex: 1 }}>
              <Text style={styles.habitName}>{h.name}</Text>
              <Text style={styles.habitMeta}>{h.time || 'Anytime'} • {h.difficulty}</Text>
            </View>
            <TouchableOpacity onPress={() => {}}>
              <Trash2 size={16} color={COLORS.danger} />
            </TouchableOpacity>
         </GlassCard>
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
        </View>

        {activeTab === 'avatar' ? renderAvatarSection() : renderAnchorsSection()}

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
  balanceBox: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: RADIUS.full, backgroundColor: 'rgba(124, 140, 255, 0.1)' },
  balanceText: { ...TYPOGRAPHY.label, color: COLORS.primary, fontSize: 12 },

  tabContainer: { flexDirection: 'row', gap: SPACING[4], marginBottom: SPACING[8] },
  tab: { paddingVertical: 8, paddingHorizontal: 4, borderBottomWidth: 2, borderBottomColor: 'transparent' },
  activeTab: { borderBottomColor: COLORS.primary },
  tabText: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 13 },
  activeTabText: { color: COLORS.text },

  avatarSection: { gap: SPACING[6] },
  characterStage: { 
    padding: SPACING[8], 
    alignItems: 'center', 
    borderRadius: RADIUS.xl, 
    backgroundColor: COLORS.surface,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.03)'
  },
  avatarCircle: { 
    width: 120, 
    height: 120, 
    borderRadius: 60, 
    backgroundColor: COLORS.surfaceLight, 
    alignItems: 'center', 
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: COLORS.primary,
    ...SHADOWS.glowPrimary
  },
  avatarEmoji: { fontSize: 50 },
  aura: { position: 'absolute', width: 140, height: 140, borderRadius: 70, borderWidth: 2, opacity: 0.3 },
  characterInfo: { alignItems: 'center', marginTop: SPACING[6] },
  characterName: { ...TYPOGRAPHY.h2, color: COLORS.text, letterSpacing: 2 },
  characterStageText: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 4 },

  sectionTitle: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 10, letterSpacing: 1.5, marginTop: SPACING[4] },
  equippedGrid: { flexDirection: 'row', gap: SPACING[3] },
  equippedSlot: { flex: 1, alignItems: 'center', gap: 6 },
  slotBox: { width: '100%', aspectRatio: 1, borderRadius: RADIUS.md, backgroundColor: COLORS.surface, alignItems: 'center', justifyContent: 'center', borderStyle: 'dashed', borderWidth: 1, borderColor: COLORS.border },
  slotText: { color: COLORS.textDim, fontSize: 16 },
  slotLabel: { ...TYPOGRAPHY.caption, fontSize: 8 },

  shopGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: SPACING[4] },
  shopCard: { width: (width - SPACING[5] * 2 - SPACING[4]) / 2, gap: 8 },
  itemIconBox: { width: '100%', aspectRatio: 1, borderRadius: RADIUS.lg, alignItems: 'center', justifyContent: 'center', backgroundColor: COLORS.surfaceLight },
  itemName: { ...TYPOGRAPHY.body, fontSize: 14, color: COLORS.textSecondary },
  priceTag: { flexDirection: 'row', alignItems: 'center' },
  priceText: { ...TYPOGRAPHY.label, fontSize: 10, color: COLORS.warning },

  anchorsSection: { gap: SPACING[6] },
  habitHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  habitItem: { flexDirection: 'row', alignItems: 'center', padding: SPACING[5], borderRadius: RADIUS.lg, backgroundColor: COLORS.surface },
  habitName: { ...TYPOGRAPHY.h3, color: COLORS.text, fontSize: 17 },
  habitMeta: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 2 }
});
