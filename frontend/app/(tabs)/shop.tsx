import React, { useState, useEffect, useCallback } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView,
  TouchableOpacity,
  FlatList,
  RefreshControl,
  Alert
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS, SHADOWS } from '../../src/theme/theme';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { Shield, Palette, Zap, Star, Coins } from 'lucide-react-native';
import { MotiView } from 'moti';
import { api } from '../../src/api/client';
import { triggerHaptic } from '../../src/utils/animationManager';

const SHOP_ITEMS = [
  { id: 'streak_freeze', name: 'Streak Freeze', desc: 'Protect your streak for one day if you miss a habit.', cost: 200, icon: Shield, color: '#3b82f6' },
  { id: 'xp_boost', name: '2x XP Boost', desc: 'Double XP for 24 hours to accelerate your level progress.', cost: 350, icon: Zap, color: COLORS.primary },
  { id: 'neon_ring', name: 'Neon Ring', desc: 'A glowing purple avatar border for elite practitioners.', cost: 150, icon: Star, color: COLORS.identity.awareness },
  { id: 'golden_theme', name: 'Golden Theme', desc: 'Bathe your dashboard in the light of supreme achievement.', cost: 500, icon: Palette, color: COLORS.warning },
];

export default function ShopScreen() {
  const { coins, token, setUserInfo } = useUserStore();
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);

  const fetchBalance = useCallback(async () => {
    if (!token) return;
    try {
      const res = await api('/habits/state', 'GET', null, token);
      if (res?.user_state) {
        setUserInfo({ coins: res.user_state.coins });
      }
    } catch (e) { console.error(e); }
  }, [token, setUserInfo]);

  useEffect(() => { fetchBalance(); }, [fetchBalance]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchBalance();
    setRefreshing(false);
  };

  const handleBuy = async (itemId: string, cost: number) => {
    if (coins < cost) {
      triggerHaptic('error');
      Alert.alert('Insufficient Balance', "You don't have enough 🪙 to purchase this item.");
      return;
    }

    try {
      setLoading(itemId);
      triggerHaptic('impactMedium');
      
      const res = await api(`/shop/buy/${itemId}`, 'POST', null, token!);
      
      if (res.success) {
        triggerHaptic('success');
        Alert.alert('Success', `You purchased ${itemId.replace('_', ' ')}!`);
        fetchBalance();
      }
    } catch (e: any) {
      triggerHaptic('error');
      Alert.alert('Purchase Failed', e.message || 'Something went wrong.');
    } finally {
      setLoading(null);
    }
  };

  const renderItem = ({ item, index }: any) => (
    <MotiView
      from={{ opacity: 0, translateY: 10 }}
      animate={{ opacity: 1, translateY: 0 }}
      transition={{ delay: index * 100 }}
    >
      <GlassCard style={styles.card}>
        <View style={styles.cardContent}>
          <View style={[styles.iconBox, { backgroundColor: `${item.color}15` }]}>
            <item.icon size={24} color={item.color} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.itemName}>{item.name}</Text>
            <Text style={styles.itemDesc}>{item.desc}</Text>
            
            <TouchableOpacity 
              onPress={() => handleBuy(item.id, item.cost)}
              disabled={loading === item.id}
              style={[
                styles.buyBtn, 
                coins < item.cost && styles.buyBtnDisabled,
                loading === item.id && styles.buyBtnLoading
              ]}
              activeOpacity={0.8}
            >
              <Text style={[styles.buyBtnText, coins < item.cost && styles.buyBtnTextDisabled]}>
                {loading === item.id ? 'Processing...' : `Buy for ${item.cost} 🪙`}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </GlassCard>
    </MotiView>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>Forge</Text>
            <Text style={styles.subtitle}>Unlock identity enhancements.</Text>
          </View>
          <GlassCard style={styles.balanceBox}>
            <Text style={styles.balanceLabel}>TREASURY</Text>
            <Text style={styles.balanceValue}>{coins || 0} 🪙</Text>
          </GlassCard>
        </View>

        <FlatList
          data={SHOP_ITEMS}
          renderItem={renderItem}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  listContent: { padding: SPACING[5], paddingBottom: 100 },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    padding: SPACING[5],
    paddingBottom: SPACING[8],
    paddingTop: SPACING[8]
  },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text },
  subtitle: { ...TYPOGRAPHY.body, color: COLORS.textDim, fontSize: 14, marginTop: 4 },
  balanceBox: { 
    paddingHorizontal: 16, 
    paddingVertical: 10, 
    borderRadius: RADIUS.lg,
    backgroundColor: COLORS.surface
  },
  balanceLabel: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 8, letterSpacing: 1.5 },
  balanceValue: { ...TYPOGRAPHY.h3, color: COLORS.warning, marginTop: 2, fontSize: 16 },
  card: { marginBottom: SPACING[4], padding: 0, borderRadius: RADIUS.xl, backgroundColor: COLORS.surface },
  cardContent: { flexDirection: 'row', padding: SPACING[5], gap: SPACING[4] },
  iconBox: { 
    width: 56, 
    height: 56, 
    borderRadius: RADIUS.lg, 
    alignItems: 'center', 
    justifyContent: 'center',
  },
  itemName: { ...TYPOGRAPHY.h3, color: COLORS.text, fontSize: 18 },
  itemDesc: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, marginTop: 4, fontSize: 13, lineHeight: 18 },
  buyBtn: { 
    marginTop: 16, 
    backgroundColor: COLORS.primary, 
    paddingVertical: 10, 
    paddingHorizontal: 16, 
    borderRadius: RADIUS.md,
    alignSelf: 'flex-start',
    ...SHADOWS.card
  },
  buyBtnDisabled: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
  },
  buyBtnLoading: {
    opacity: 0.7
  },
  buyBtnText: { 
    ...TYPOGRAPHY.label, 
    color: '#fff', 
    fontSize: 12,
    textTransform: 'none'
  },
  buyBtnTextDisabled: {
    color: COLORS.textDim
  }
});
