import React, { useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, SafeAreaView } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import AvatarCharacter from '../../src/components/AvatarCharacter';
import { GlassCard } from '../../src/components/GlassCard';
import { COLORS, TYPOGRAPHY, SPACING } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';

export default function AvatarStudioScreen() {
  const [activeTab, setActiveTab] = useState('studio'); // 'studio' or 'forge'
  const [selectedCategory, setSelectedCategory] = useState('outfit');
  const queryClient = useQueryClient();
  const { token } = useUserStore();

  const handleTabSwitch = (tab: string) => {
    setActiveTab(tab);
    setSelectedCategory(tab === 'studio' ? 'outfit' : 'theme');
  };

  const { data: avatarResponse, isLoading: isLoadingAvatar } = useQuery({
    queryKey: ['avatar'],
    queryFn: () => api('/api/avatar/', 'GET', null, token!),
    enabled: !!token,
  });

  const { data: shopResponse, isLoading: isLoadingShop } = useQuery({
    queryKey: ['avatar-shop'],
    queryFn: () => api('/api/avatar/shop', 'GET', null, token!),
    enabled: !!token,
  });

  const { data: forgeResponse, isLoading: isLoadingForge } = useQuery({
    queryKey: ['forge-shop'],
    queryFn: () => api('/shop/items', 'GET', null, token!),
    enabled: !!token,
  });

  const purchaseMutation = useMutation({
    mutationFn: (itemId: string) => api('/api/avatar/purchase', 'POST', { item_id: itemId }, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['avatar'] });
    }
  });

  const avatar = avatarResponse?.avatar;
  const studioItems = shopResponse?.items || [];
  const forgeItems = forgeResponse || [];

  const categories = activeTab === 'studio' 
    ? [
        { id: 'outfit', label: 'Outfits' },
        { id: 'aura', label: 'Auras' },
        { id: 'accessory', label: 'Accessories' }
      ]
    : [
        { id: 'theme', label: 'Themes' },
        { id: 'powerup', label: 'Powerups' },
        { id: 'booster', label: 'Boosters' }
      ];

  const filteredItems = activeTab === 'studio'
    ? studioItems.filter((item: any) => item.type === selectedCategory)
    : forgeItems.filter((item: any) => item.category === selectedCategory);

  if (isLoadingAvatar || isLoadingShop || isLoadingForge) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.topToggle}>
          <TouchableOpacity 
            onPress={() => handleTabSwitch('studio')}
            style={[styles.toggleBtn, activeTab === 'studio' && styles.toggleBtnActive]}
          >
            <Text style={[styles.toggleText, activeTab === 'studio' && styles.toggleTextActive]}>STUDIO</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            onPress={() => handleTabSwitch('forge')}
            style={[styles.toggleBtn, activeTab === 'forge' && styles.toggleBtnActive]}
          >
            <Text style={[styles.toggleText, activeTab === 'forge' && styles.toggleTextActive]}>FORGE</Text>
          </TouchableOpacity>
        </View>

        {activeTab === 'studio' ? (
          <View style={styles.previewSection}>
            <Text style={styles.archetypeTitle}>{avatar?.archetype?.toUpperCase() || 'BEGINNER'}</Text>
            <AvatarCharacter 
              avatar={avatar} 
              size={180}
              animate={true}
            />
          </View>
        ) : (
          <View style={styles.forgeHeader}>
             <Text style={styles.archetypeTitle}>ENHANCEMENTS</Text>
             <Text style={styles.forgeSubtitle}>Power-ups and system themes.</Text>
          </View>
        )}

        <GlassCard style={styles.statsCard}>
          <View style={styles.currencyContainer}>
            <Text style={styles.currencyText}>🪙 {avatar?.economy?.coins || 0}</Text>
          </View>
        </GlassCard>

        <View style={styles.tabsWrapper}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabsScroll}>
            {categories.map(category => (
              <TouchableOpacity
                key={category.id}
                onPress={() => setSelectedCategory(category.id)}
                style={[
                  styles.tab,
                  selectedCategory === category.id && styles.tabActive
                ]}
              >
                <Text style={[
                  styles.tabText,
                  selectedCategory === category.id && styles.tabTextActive
                ]}>
                  {category.label}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        <FlatList
          data={filteredItems}
          keyExtractor={(item) => item.id}
          numColumns={2}
          contentContainerStyle={styles.itemsGrid}
          renderItem={({ item }) => {
            const isUnlocked = activeTab === 'studio' 
              ? avatar?.economy?.unlocked_items?.includes(item.id)
              : false; // Forge items are usually one-time use or permanent unlocks
            
            const isEquipped = activeTab === 'studio'
              ? avatar?.economy?.equipped_items?.[item.type] === item.id
              : false;

            const canAfford = (avatar?.economy?.coins || 0) >= item.price;

            return (
              <GlassCard style={[styles.itemCard, isEquipped && styles.equippedCard]}>
                <View style={styles.itemContent}>
                  <Text style={styles.itemName}>{item.name}</Text>
                  <Text style={styles.itemRarity}>{item.rarity?.toUpperCase() || item.category?.toUpperCase()}</Text>
                  
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
                        {isUnlocked ? 'EQUIP' : `🪙 ${item.price || item.cost}`}
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
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: {
    flex: 1,
    paddingTop: SPACING.md,
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  previewSection: {
    alignItems: 'center',
    paddingHorizontal: SPACING.md,
    marginBottom: SPACING.sm,
  },
  topToggle: {
    flexDirection: 'row',
    backgroundColor: 'rgba(255,255,255,0.05)',
    marginHorizontal: SPACING.md,
    borderRadius: 12,
    padding: 4,
    marginBottom: SPACING.md,
  },
  toggleBtn: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 8,
  },
  toggleBtnActive: {
    backgroundColor: COLORS.primary,
  },
  toggleText: {
    ...TYPOGRAPHY.label,
    color: COLORS.textDim,
    fontSize: 12,
  },
  toggleTextActive: {
    color: '#000',
  },
  forgeHeader: {
    alignItems: 'center',
    paddingVertical: SPACING.md,
  },
  forgeSubtitle: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textSecondary,
    marginTop: 4,
  },
  archetypeTitle: {
    ...TYPOGRAPHY.h2,
    color: COLORS.primary,
    fontWeight: '900',
    marginBottom: 4,
    letterSpacing: 2,
  },
  statsCard: {
    marginHorizontal: SPACING.md,
    padding: SPACING.sm,
    marginBottom: SPACING.md,
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
    color: '#000',
    fontSize: 12,
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
    backgroundColor: 'rgba(255,255,255,0.05)',
    height: 40,
    justifyContent: 'center',
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
    color: '#000',
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
    backgroundColor: 'rgba(255,255,255,0.1)',
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
