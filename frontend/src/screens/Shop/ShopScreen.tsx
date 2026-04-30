import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, FlatList, Dimensions, ActivityIndicator } from "react-native";
import { useUserStore } from "../../store/useUserStore";
import { COLORS, SPACING, TYPOGRAPHY } from "../../theme/theme";
import { Coins, Flame, Palette, Zap, Box, CheckCircle2 } from "lucide-react-native";
import Animated, { FadeInUp, Layout } from "react-native-reanimated";
import { MotiView } from "moti";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getShopItems, buyShopItem } from "../../api/client";
import { triggerHaptic } from "../../utils/animationManager";

const { width } = Dimensions.get("window");

const RARITY_COLORS: Record<string, string> = {
  common: "#94a3b8",
  uncommon: "#22c55e",
  rare: "#3b82f6",
  legendary: "#eab308",
};

export default function ShopScreen() {
  const user = useUserStore();
  const { setUserInfo, token } = user;
  const queryClient = useQueryClient();
  const [lastBoughtId, setLastBoughtId] = useState<string | null>(null);

  const { data: shopItems, isLoading } = useQuery({
    queryKey: ["shopItems"],
    queryFn: getShopItems,
  });

  const buyMutation = useMutation({
    mutationFn: (itemId: string) => buyShopItem(itemId, token!),
    onSuccess: (data, itemId) => {
      triggerHaptic("success");
      setUserInfo({ 
        coins: data.remaining_coins,
        xp: data.xp 
      });
      setLastBoughtId(itemId);
      setTimeout(() => setLastBoughtId(null), 2000);
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
    },
    onError: (error: any) => {
      triggerHaptic("error");
      alert(error.message || "Purchase failed");
    }
  });

  const handleBuy = (item: any) => {
    if (user.coins < item.cost) {
        triggerHaptic("error");
        return;
    }
    buyMutation.mutate(item.id);
  };

  if (isLoading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Hero Shop</Text>
        <View style={styles.coinBadge}>
          <Coins size={18} color="#eab308" fill="#eab308" />
          <Text style={styles.coinText}>{user.coins}</Text>
        </View>
      </View>

      <FlatList
        data={shopItems}
        keyExtractor={(item) => item.id}
        numColumns={2}
        contentContainerStyle={styles.listContent}
        columnWrapperStyle={styles.columnWrapper}
        renderItem={({ item, index }) => {
          const isBought = lastBoughtId === item.id;
          const canAfford = user.coins >= item.cost;

          return (
            <Animated.View 
              entering={FadeInUp.delay(index * 100)}
              layout={Layout.springify()}
              style={styles.cardContainer}
            >
              <TouchableOpacity 
                activeOpacity={0.8}
                style={[
                  styles.card, 
                  { borderColor: canAfford ? "rgba(255,255,255,0.1)" : "rgba(255,255,255,0.02)" },
                  isBought && styles.successCard
                ]}
                onPress={() => handleBuy(item)}
                disabled={!canAfford || buyMutation.isPending}
              >
                {isBought ? (
                    <MotiView 
                        from={{ scale: 0 }} 
                        animate={{ scale: 1 }} 
                        style={styles.successOverlay}
                    >
                        <CheckCircle2 size={32} color={COLORS.secondary} />
                        <Text style={styles.successText}>PURCHASED!</Text>
                    </MotiView>
                ) : (
                    <>
                        <View style={[styles.rarityTag, { backgroundColor: (RARITY_COLORS[item.rarity] || "#94a3b8") + "20" }]}>
                            <Text style={[styles.rarityText, { color: RARITY_COLORS[item.rarity] || "#94a3b8" }]}>{(item.rarity || item.category).toUpperCase()}</Text>
                        </View>
                        
                        <View style={styles.iconBox}>
                            {item.category === "powerup" && <Flame color="#f59e0b" />}
                            {item.category === "booster" && <Zap color="#a855f7" />}
                            {item.category === "theme" && <Palette color="#00ffcc" />}
                            {item.category === "mystery" && <Box color="#3b82f6" />}
                            {!["powerup", "booster", "theme", "mystery"].includes(item.category) && <Box color="#94a3b8" />}
                        </View>
                        
                        <Text style={styles.itemName} numberOfLines={1}>{item.name}</Text>
                        
                        <View style={styles.priceTag}>
                            <Coins size={12} color="#eab308" />
                            <Text style={[styles.priceText, !canAfford && styles.tooExpensive]}>{item.cost}</Text>
                        </View>
                    </>
                )}
              </TouchableOpacity>
            </Animated.View>
          );
        }}
      />
    </View>
  );
}

// Reuse styles but add new ones
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000", padding: 20 },
  centered: { justifyContent: "center", alignItems: "center" },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 32, marginTop: 40 },
  title: { color: "#fff", fontSize: 28, fontWeight: "800" },
  coinBadge: { flexDirection: "row", alignItems: "center", backgroundColor: "rgba(234, 179, 8, 0.1)", paddingHorizontal: 16, paddingVertical: 8, borderRadius: 24 },
  coinText: { color: "#eab308", fontWeight: "800", marginLeft: 8, fontSize: 16 },
  listContent: { paddingBottom: 40 },
  columnWrapper: { justifyContent: "space-between" },
  cardContainer: { width: (width - 52) / 2, marginBottom: 12 },
  card: { 
    backgroundColor: "#111", 
    borderRadius: 24, 
    padding: 16, 
    alignItems: "center",
    borderWidth: 1,
    height: 160,
    justifyContent: "center"
  },
  successCard: {
    borderColor: COLORS.secondary,
    backgroundColor: "rgba(16, 185, 129, 0.05)"
  },
  successOverlay: {
    alignItems: "center",
    justifyContent: "center"
  },
  successText: {
    color: COLORS.secondary,
    fontWeight: "800",
    fontSize: 10,
    marginTop: 8
  },
  rarityTag: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8, marginBottom: 12, position: "absolute", top: 12 },
  rarityText: { fontSize: 8, fontWeight: "800" },
  iconBox: { width: 48, height: 48, borderRadius: 16, backgroundColor: "rgba(255,255,255,0.03)", alignItems: "center", justifyContent: "center", marginBottom: 12 },
  itemName: { color: "#fff", fontWeight: "600", fontSize: 13, textAlign: "center", marginBottom: 8 },
  priceTag: { flexDirection: "row", alignItems: "center", gap: 4 },
  priceText: { color: "#eab308", fontWeight: "700", fontSize: 14 },
  tooExpensive: { color: "rgba(255,255,255,0.2)" }
});


