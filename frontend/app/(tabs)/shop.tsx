import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView,
  TouchableOpacity,
  FlatList
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../../src/theme/theme';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { Shield, Palette, Zap, Star } from 'lucide-react-native';
import { MotiView } from 'moti';

const SHOP_ITEMS = [
  { id: '1', name: 'Golden Theme', desc: 'Bathe your entire dashboard in the glorious light of supreme achievement.', cost: 500, icon: Palette, color: COLORS.gold },
  { id: '2', name: 'Streak Freeze', desc: 'Protect your streak for one day if you miss a habit.', cost: 200, icon: Shield, color: '#3b82f6' },
  { id: '3', name: '2x XP Boost', desc: 'Double XP for 24 hours to accelerate your level progress.', cost: 350, icon: Zap, color: COLORS.primary },
  { id: '4', name: 'Neon Ring', desc: 'A glowing purple avatar border for elite practitioners.', cost: 150, icon: Star, color: COLORS.secondary }
];

export default function ShopScreen() {
  const { coins } = useUserStore();

  const renderItem = ({ item, index }: any) => (
    <MotiView
      from={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', delay: index * 100 }}
    >
      <GlassCard style={styles.card}>
        <View style={styles.cardContent}>
          <View style={[styles.iconBox, { backgroundColor: `${item.color}20` }]}>
            <item.icon size={24} color={item.color} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.itemName}>{item.name}</Text>
            <Text style={styles.itemDesc}>{item.desc}</Text>
            <TouchableOpacity style={[styles.buyBtn, coins < item.cost && styles.buyBtnDisabled]}>
              <Text style={styles.buyBtnText}>
                {coins >= item.cost ? `Buy for 💰 ${item.cost}` : `Need 💰 ${item.cost}`}
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
            <Text style={styles.title}>Rewards</Text>
            <Text style={styles.subtitle}>Unlock cyber-enhancements.</Text>
          </View>
          <View style={styles.balanceBox}>
            <Text style={styles.balanceLabel}>BALANCE</Text>
            <Text style={styles.balanceValue}>💰 {coins || 450}</Text>
          </View>
        </View>

        <FlatList
          data={SHOP_ITEMS}
          renderItem={renderItem}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  listContent: { padding: SPACING.margin, paddingBottom: 100 },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    padding: SPACING.margin,
    paddingBottom: SPACING.lg
  },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text },
  subtitle: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, marginTop: 4 },
  balanceBox: { 
    backgroundColor: 'rgba(255, 255, 255, 0.05)', 
    paddingHorizontal: 16, 
    paddingVertical: 10, 
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)'
  },
  balanceLabel: { ...TYPOGRAPHY.caption, color: COLORS.textDim, fontSize: 8, letterSpacing: 1 },
  balanceValue: { ...TYPOGRAPHY.h3, color: COLORS.gold, marginTop: 2 },
  card: { marginBottom: SPACING.md, padding: 0 },
  cardContent: { flexDirection: 'row', padding: SPACING.lg },
  iconBox: { 
    width: 50, 
    height: 50, 
    borderRadius: 14, 
    alignItems: 'center', 
    justifyContent: 'center',
    marginRight: 16
  },
  itemName: { ...TYPOGRAPHY.h3, color: COLORS.text },
  itemDesc: { ...TYPOGRAPHY.caption, color: COLORS.textSecondary, marginTop: 6, lineHeight: 18 },
  buyBtn: { 
    marginTop: 16, 
    backgroundColor: COLORS.primary, 
    paddingVertical: 8, 
    paddingHorizontal: 16, 
    borderRadius: 10,
    alignSelf: 'flex-start'
  },
  buyBtnDisabled: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
  },
  buyBtnText: { 
    ...TYPOGRAPHY.label, 
    color: '#000', 
    fontSize: 12 
  }
});
