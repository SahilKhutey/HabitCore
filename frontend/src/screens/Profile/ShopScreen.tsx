import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert } from 'react-native';
import { GlassCard } from '../../components/GlassCard';
import { COLORS, SPACING, TYPOGRAPHY } from '../../theme/theme';
import { useUserStore } from '../../store/useUserStore';
import { api, buyShopItem } from '../../api/client';
import { useQueryClient } from '@tanstack/react-query';
import { Gem, Snowflake, Palette } from 'lucide-react-native';

const SHOP_ITEMS = [
  { id: 'streak_freeze', name: 'Streak Freeze', price: 100, icon: <Snowflake color={COLORS.accent} />, description: 'Prevents your streak from breaking for one day.' },
  { id: 'premium_theme', name: 'Premium Theme', price: 500, icon: <Palette color={COLORS.primary} />, description: 'Unlocks the "Cyberpunk" premium theme.' },
];

export default function ShopScreen() {
  const { coins, id, token, paywall_variant } = useUserStore();
  const queryClient = useQueryClient();

  const handleBuy = async (itemId: string, price: number) => {
    if ((coins || 0) < price) {
      Alert.alert("Insufficient Coins", "Complete more habits to earn coins!");
      return;
    }

    try {
      await buyShopItem(itemId, token!);
      useUserStore.getState().setUserInfo({ coins: (coins || 0) - price });
      queryClient.invalidateQueries({ queryKey: ["shopItems"] });
      Alert.alert("Success", "Item purchased!");
    } catch (err) {
      Alert.alert("Error", "Failed to complete purchase");
    }
  };

  const getPaywallMessage = () => {
    switch(paywall_variant) {
      case 'B': return "Never break your streak again 🔥";
      case 'C': return "Unlock Premium or lose your progress ⚠️";
      default: return "Upgrade to Premium 🚀";
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={TYPOGRAPHY.h1}>Hero Shop</Text>
        <View style={styles.balanceCard}>
          <Gem size={20} color={COLORS.accent} />
          <Text style={styles.balanceText}>{coins || 0} Coins</Text>
        </View>
      </View>

      <GlassCard style={{ ...styles.referralCard, backgroundColor: 'rgba(139, 92, 246, 0.1)' }}>
        <View style={styles.details}>
          <Text style={TYPOGRAPHY.h2}>{getPaywallMessage()}</Text>
          <Text style={TYPOGRAPHY.caption}>Get Unlimited Habits & Streak Freezes</Text>
        </View>
        <TouchableOpacity style={styles.buyButton}>
          <Text style={styles.buyText}>Upgrade</Text>
        </TouchableOpacity>
      </GlassCard>

      <FlatList
        data={SHOP_ITEMS}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <GlassCard style={styles.itemCard}>
            <View style={styles.iconContainer}>{item.icon}</View>
            <View style={styles.details}>
              <Text style={TYPOGRAPHY.h2}>{item.name}</Text>
              <Text style={TYPOGRAPHY.caption}>{item.description}</Text>
            </View>
            <TouchableOpacity 
              style={styles.buyButton}
              onPress={() => handleBuy(item.id, item.price)}
            >
              <Text style={styles.buyText}>{item.price} 💎</Text>
            </TouchableOpacity>
          </GlassCard>
        )}
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    padding: SPACING.md,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: SPACING.lg,
  },
  balanceCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  balanceText: {
    color: COLORS.text,
    fontWeight: '700',
    marginLeft: 8,
  },
  listContent: {
    paddingBottom: SPACING.xl,
  },
  itemCard: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  iconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255,255,255,0.05)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  details: {
    flex: 1,
    marginLeft: SPACING.md,
  },
  buyButton: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 10,
  },
  shareButton: {
    backgroundColor: COLORS.secondary,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 10,
  },
  referralCard: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.lg,
    backgroundColor: 'rgba(16, 185, 129, 0.05)',
    borderColor: 'rgba(16, 185, 129, 0.2)',
  },
  buyText: {
    color: '#FFF',
    fontWeight: '700',
  },
});
