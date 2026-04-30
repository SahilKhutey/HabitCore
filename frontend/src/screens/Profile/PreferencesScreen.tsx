import React from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Alert } from "react-native";
import { useUserStore, UserState } from "../../store/useUserStore";
import { buyShopItem } from "../../api/client";
import { useQueryClient } from "@tanstack/react-query";
import { Zap, Target, Trophy, Coffee } from "lucide-react-native";

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000", padding: 20 },
  header: { color: "#fff", fontSize: 24, fontWeight: "800", marginBottom: 32 },
  section: { marginBottom: 32 },
  sectionTitle: { color: "rgba(255,255,255,0.5)", fontSize: 14, textTransform: "uppercase", marginBottom: 16 },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: 12 },
  card: { 
    width: "48%", 
    backgroundColor: "#111", 
    padding: 16, 
    borderRadius: 16, 
    borderWidth: 1, 
    borderColor: "rgba(255,255,255,0.05)" 
  },
  activeCard: { borderColor: "#00ffcc", backgroundColor: "rgba(0,255,204,0.05)" },
  cardText: { color: "#fff", fontWeight: "600", marginTop: 8 },
  cardDesc: { color: "rgba(255,255,255,0.4)", fontSize: 11, marginTop: 4 },
  miniBar: { width: 30, height: 4, backgroundColor: "#00ffcc", borderRadius: 2 },
  miniRing: { width: 20, height: 20, borderRadius: 10, borderWidth: 2, borderColor: "#00ffcc" }
});

const OPTIONS = {
  mode: [
    { id: "Speed", icon: <Zap size={20} color="#00ffcc" />, desc: "Fast XP, low streak focus" },
    { id: "Consistency", icon: <Target size={20} color="#a855f7" />, desc: "Double streak bonuses" },
    { id: "Competitive", icon: <Trophy size={20} color="#eab308" />, desc: "Leaderboard & Ranks" },
    { id: "Minimal", icon: <Coffee size={20} color="#94a3b8" />, desc: "No pressure, clean UI" },
  ],
  style: [
    { id: "bar", icon: <View style={styles.miniBar} /> },
    { id: "ring", icon: <View style={styles.miniRing} /> },
    { id: "streak", icon: <Text style={{ fontSize: 18 }}>🔥🔥</Text> },
  ],
  engagement: [
    { id: "Chill", desc: "Minimal notifications" },
    { id: "Balanced", desc: "Standard nudges" },
    { id: "Intense", desc: "Aggressive streak alerts" },
  ],
  identity: [
    { id: "Fit", color: "#22c55e" },
    { id: "Learner", color: "#3b82f6" },
    { id: "Productive", color: "#a855f7" },
    { id: "Calm", color: "#06b6d4" },
  ]
};

export default function PreferencesScreen() {
  const user = useUserStore();
  const { coins, token, updatePreferences } = user;
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

  const renderSection = (title: string, key: keyof UserState, items: any[]) => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <View style={styles.grid}>
        {items.map((item) => (
          <TouchableOpacity
            key={item.id}
            style={[
              styles.card,
              user[key] === item.id && styles.activeCard
            ]}
            onPress={() => updatePreferences({ [key]: item.id })}
          >
            {item.icon}
            <Text style={styles.cardText}>{item.id}</Text>
            {item.desc && <Text style={styles.cardDesc}>{item.desc}</Text>}
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>Personalize Your Journey</Text>
      
      {renderSection("Progression Style", "mode", OPTIONS.mode)}
      {renderSection("Progress Visualization", "style", OPTIONS.style)}
      {renderSection("Engagement Intensity", "engagement", OPTIONS.engagement)}
      {renderSection("Primary Identity", "identity", OPTIONS.identity)}

      <View style={{ height: 100 }} />
    </ScrollView>
  );
}
