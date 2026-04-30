import React from "react";
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from "react-native";
import { useUserStore } from "../../store/useUserStore";
import { COLORS, SPACING } from "../../theme/theme";
import { Box, Flame, Zap, Palette } from "lucide-react-native";
import { GlassCard } from "../../components/GlassCard";

const INVENTORY_DATA = [
  { id: "1", name: "Streak Freeze", count: 2, icon: <Flame color="#f59e0b" /> },
  { id: "2", name: "XP Booster", count: 1, icon: <Zap color="#a855f7" /> },
];

export default function InventoryScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.header}>Your Inventory</Text>
      
      <FlatList
        data={INVENTORY_DATA}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <GlassCard style={styles.itemCard}>
            <View style={styles.itemInfo}>
              <View style={styles.iconBox}>{item.icon}</View>
              <View>
                <Text style={styles.itemName}>{item.name}</Text>
                <Text style={styles.itemCount}>Owned: {item.count}</Text>
              </View>
            </View>
            
            <TouchableOpacity style={styles.useButton}>
              <Text style={styles.useText}>USE</Text>
            </TouchableOpacity>
          </GlassCard>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000", padding: 20 },
  header: { color: "#fff", fontSize: 24, fontWeight: "800", marginBottom: 32, marginTop: 40 },
  itemCard: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 16, marginBottom: 12 },
  itemInfo: { flexDirection: "row", alignItems: "center", gap: 12 },
  iconBox: { width: 48, height: 48, borderRadius: 12, backgroundColor: "rgba(255,255,255,0.03)", alignItems: "center", justifyContent: "center" },
  itemName: { color: "#fff", fontWeight: "600", fontSize: 16 },
  itemCount: { color: "rgba(255,255,255,0.4)", fontSize: 12, marginTop: 2 },
  useButton: { backgroundColor: "rgba(255,255,255,0.05)", paddingHorizontal: 16, paddingVertical: 8, borderRadius: 8, borderWidth: 1, borderColor: "rgba(255,255,255,0.1)" },
  useText: { color: "#fff", fontWeight: "700", fontSize: 12 }
});
