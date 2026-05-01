import React from "react";
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator } from "react-native";
import { useUserStore } from "../../store/useUserStore";
import { COLORS, SPACING, TYPOGRAPHY } from "../../theme/theme";
import { Box, Flame, Zap, Palette, Package } from "lucide-react-native";
import { GlassCard } from "../../components/GlassCard";
import { useQuery } from "@tanstack/react-query";
import { getInventory, equipItem } from "../../api/client";
import Animated, { FadeInUp } from "react-native-reanimated";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { triggerHaptic } from "../../utils/animationManager";

export default function InventoryScreen() {
  const { token } = useUserStore();

  const queryClient = useQueryClient();

  const { data: inventory, isLoading } = useQuery({
    queryKey: ["inventory"],
    queryFn: () => getInventory(token!),
    enabled: !!token,
  });

  const equipMutation = useMutation({
    mutationFn: (inventoryId: string) => equipItem(inventoryId, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      triggerHaptic("success");
    },
    onError: () => {
      triggerHaptic("error");
    }
  });

  const getIcon = (category: string) => {
    switch (category) {
      case "powerup": return <Flame color="#f59e0b" />;
      case "booster": return <Zap color="#a855f7" />;
      case "theme": return <Palette color="#00ffcc" />;
      default: return <Package color="#94a3b8" />;
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator color={COLORS.primary} size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Treasury</Text>
      
      {inventory?.length === 0 ? (
        <View style={styles.emptyState}>
          <Box size={64} color="rgba(255,255,255,0.1)" />
          <Text style={styles.emptyText}>Your treasury is empty</Text>
          <Text style={styles.emptySub}>Visit the Shop to unlock items</Text>
        </View>
      ) : (
        <FlatList
          data={inventory}
          keyExtractor={(item) => item.inventory_id}
          contentContainerStyle={{ paddingBottom: 100 }}
          renderItem={({ item, index }) => (
            <Animated.View entering={FadeInUp.delay(index * 100)}>
              <GlassCard style={[styles.itemCard, item.is_active && styles.activeCard]}>
                <View style={styles.itemInfo}>
                  <View style={[styles.iconBox, item.is_active && styles.activeIconBox]}>
                    {getIcon(item.category)}
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.itemName}>{item.name}</Text>
                    <Text style={styles.itemDesc} numberOfLines={2}>{item.description}</Text>
                  </View>
                </View>
                
                <TouchableOpacity 
                  style={[styles.useButton, item.is_active && styles.activeButton]} 
                  onPress={() => equipMutation.mutate(item.inventory_id)}
                  activeOpacity={0.7}
                  disabled={equipMutation.isPending}
                >
                  <Text style={[styles.useText, item.is_active && styles.activeButtonText]}>
                    {item.is_active ? "ACTIVE" : "EQUIP"}
                  </Text>
                </TouchableOpacity>
              </GlassCard>
            </Animated.View>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  centered: { justifyContent: "center", alignItems: "center" },
  header: { color: COLORS.text, fontSize: 36, fontWeight: "900", marginBottom: 32, marginTop: 60, paddingHorizontal: 24, letterSpacing: -1 },
  itemCard: { 
    flexDirection: "row", 
    justifyContent: "space-between", 
    alignItems: "center", 
    padding: 20, 
    marginHorizontal: 24,
    marginBottom: 16,
    borderRadius: 28,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.05)"
  },
  activeCard: {
    borderColor: COLORS.primary,
    backgroundColor: "rgba(56,189,248,0.05)",
    borderWidth: 2
  },
  itemInfo: { flexDirection: "row", alignItems: "center", gap: 16, flex: 1 },
  iconBox: { 
    width: 56, 
    height: 56, 
    borderRadius: 20, 
    backgroundColor: "rgba(255,255,255,0.04)", 
    alignItems: "center", 
    justifyContent: "center" 
  },
  activeIconBox: {
    backgroundColor: "rgba(56,189,248,0.15)"
  },
  itemName: { color: COLORS.text, fontWeight: "800", fontSize: 18, letterSpacing: -0.5 },
  itemDesc: { color: COLORS.textSecondary, fontSize: 13, marginTop: 4, lineHeight: 18 },
  useButton: { 
    backgroundColor: "rgba(255,255,255,0.08)", 
    paddingHorizontal: 16, 
    paddingVertical: 10, 
    borderRadius: 14, 
    minWidth: 80,
    alignItems: "center"
  },
  activeButton: {
    backgroundColor: COLORS.primary,
  },
  useText: { color: COLORS.textSecondary, fontWeight: "800", fontSize: 12, letterSpacing: 0.5 },
  activeButtonText: {
    color: "#fff",
  },
  emptyState: { flex: 1, justifyContent: "center", alignItems: "center", opacity: 0.8 },
  emptyText: { color: COLORS.text, fontSize: 22, fontWeight: "800", marginTop: 24 },
  emptySub: { color: COLORS.textSecondary, fontSize: 16, marginTop: 8 }
});
