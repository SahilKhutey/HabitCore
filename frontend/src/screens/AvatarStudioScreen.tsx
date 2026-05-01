import React, { useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import AvatarCharacter from '../components/AvatarCharacter';
import { GlassCard } from '../components/GlassCard';
import { COLORS, TYPOGRAPHY, SPACING } from '../theme/theme';
import { api } from '../api/client';
import { useUserStore } from '../store/useUserStore';

export default function AvatarStudioScreen() {
  const [selectedTab, setSelectedTab] = useState('outfit');
  const queryClient = useQueryClient();
  const { token } = useUserStore();

  // Fetch avatar data
  const { data: avatarResponse, isLoading: isLoadingAvatar } = useQuery({
    queryKey: ['avatar'],
    queryFn: () => api('/avatar/', 'GET', null, token!)
  });

  // Fetch shop items
  const { data: shopResponse, isLoading: isLoadingShop } = useQuery({
    queryKey: ['avatar-shop'],
    queryFn: () => api('/avatar/shop', 'GET', null, token!)
  });

  // Purchase mutation
  const purchaseMutation = useMutation({
    mutationFn: (itemId: string) => api('/avatar/purchase', 'POST', { item_id: itemId }, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['avatar'] });
    }
  });

  const avatar = avatarResponse?.avatar;
  const shopItems = shopResponse?.items || [];

  const categories = [
    { id: 'outfit', label: 'Outfits' },
    { id: 'aura', label: 'Auras' },
    { id: 'accessory', label: 'Accessories' },
    { id: 'emote', label: 'Emotes' }
  ];

  const filteredItems = shopItems.filter((item: any) => item.type === selectedTab);

  if (isLoadingAvatar || isLoadingShop) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Avatar Preview Section */}
      <View style={styles.previewSection}>
        <Text style={styles.archetypeTitle}>{avatar?.archetype?.toUpperCase() || 'BEGINNER'}</Text>
        <AvatarCharacter 
          avatar={avatar} 
          size={180}
          animate={true}
        />
        
        <GlassCard style={styles.statsCard}>
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Level {avatar?.level}</Text>
            <View style={styles.xpBarContainer}>
              <View style={[styles.xpBar, { width: `${(avatar?.xp / (avatar?.level * 150)) * 100}%` }]} />
            </View>
          </View>
          <View style={styles.currencyContainer}>
            <Text style={styles.currencyText}>🪙 {avatar?.economy.coins || 0}</Text>
          </View>
        </GlassCard>
      </View>

      {/* Customization Tabs */}
      <View style={styles.tabsWrapper}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabsScroll}>
          {categories.map(category => (
            <TouchableOpacity
              key={category.id}
              onPress={() => setSelectedTab(category.id)}
              style={[
                styles.tab,
                selectedTab === category.id && styles.tabActive
              ]}
            >
              <Text style={[
                styles.tabText,
                selectedTab === category.id && styles.tabTextActive
              ]}>
                {category.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Items Grid */}
      <FlatList
        data={filteredItems}
        keyExtractor={(item) => item.id}
        numColumns={2}
        contentContainerStyle={styles.itemsGrid}
        renderItem={({ item }) => {
          const isUnlocked = avatar?.economy.unlocked_items.includes(item.id);
          const isEquipped = avatar?.economy.equipped_items[item.type] === item.id;
          const canAfford = avatar?.economy.coins >= item.price;

          return (
            <GlassCard style={[styles.itemCard, isEquipped && styles.equippedCard]}>
              <View style={styles.itemContent}>
                <Text style={styles.itemName}>{item.name}</Text>
                <Text style={styles.itemRarity}>{item.rarity.toUpperCase()}</Text>
                
                {!isEquipped && (
                  <TouchableOpacity
                    style={[
                      styles.actionButton,
                      !isUnlocked && !canAfford && styles.buttonDisabled
                    ]}
                    onPress={() => purchaseMutation.mutate(item.id)}
                    disabled={purchaseMutation.isPending || (!isUnlocked && !canAfford)}
                  >
                    <Text style={styles.buttonText}>
                      {isUnlocked ? 'EQUIP' : `🪙 ${item.price}`}
                    </Text>
                  </TouchableOpacity>
                )}
                {isEquipped && (
                  <View style={styles.equippedBadge}>
                    <Text style={styles.equippedText}>EQUIPPED</Text>
                  </View>
                )}
              </View>
            </GlassCard>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bg,
    paddingTop: SPACING.xl,
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  previewSection: {
    alignItems: 'center',
    paddingHorizontal: SPACING.md,
    marginBottom: SPACING.lg,
  },
  archetypeTitle: {
    ...TYPOGRAPHY.h2,
    color: COLORS.primary,
    fontWeight: '900',
    marginBottom: SPACING.md,
    letterSpacing: 2,
  },
  statsCard: {
    width: '100%',
    padding: SPACING.md,
    marginTop: SPACING.lg,
  },
  statRow: {
    width: '100%',
    marginBottom: SPACING.sm,
  },
  statLabel: {
    ...TYPOGRAPHY.caption,
    color: COLORS.text,
    marginBottom: 4,
  },
  xpBarContainer: {
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  xpBar: {
    height: '100%',
    backgroundColor: COLORS.primary,
  },
  currencyContainer: {
    alignSelf: 'center',
    backgroundColor: COLORS.accent,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  currencyText: {
    ...TYPOGRAPHY.body,
    fontWeight: '800',
    color: COLORS.bg,
  },
  tabsWrapper: {
    height: 50,
    marginBottom: SPACING.md,
  },
  tabsScroll: {
    paddingHorizontal: SPACING.md,
  },
  tab: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    marginRight: 10,
    borderRadius: 20,
    backgroundColor: COLORS.card,
    height: 40,
  },
  tabActive: {
    backgroundColor: COLORS.primary,
  },
  tabText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
    fontSize: 14,
  },
  tabTextActive: {
    color: COLORS.bg,
    fontWeight: '700',
  },
  itemsGrid: {
    paddingHorizontal: SPACING.md,
    paddingBottom: 100,
  },
  itemCard: {
    flex: 1,
    margin: 6,
    padding: 12,
    minHeight: 120,
  },
  equippedCard: {
    borderColor: COLORS.primary,
    borderWidth: 1,
  },
  itemContent: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  itemName: {
    ...TYPOGRAPHY.body,
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
    color: COLORS.text,
  },
  itemRarity: {
    fontSize: 10,
    color: COLORS.textSecondary,
    marginBottom: 12,
  },
  actionButton: {
    backgroundColor: COLORS.secondary,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    width: '100%',
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: COLORS.card,
    opacity: 0.5,
  },
  buttonText: {
    ...TYPOGRAPHY.caption,
    color: '#fff',
    fontWeight: '800',
    fontSize: 12,
  },
  equippedBadge: {
    backgroundColor: 'rgba(0, 255, 204, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  equippedText: {
    fontSize: 10,
    color: COLORS.primary,
    fontWeight: '900',
  }
});
