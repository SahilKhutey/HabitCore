import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from "react-native";
import { useUserStore } from "../store/useUserStore";
import { COLORS, SPACING } from "../theme/theme";
import { Sparkles, Plus } from "lucide-react-native";
import { Habit } from "../types/habit";

interface HabitSuggestionsProps {
  onSelect: (habit: Partial<Habit>) => void;
}

const SUGGESTIONS = {
  Fit: [
    { title: "Drink Water", xp: 10 },
    { title: "Morning Stretch", xp: 20 },
    { title: "Walk 5k Steps", xp: 40 }
  ],
  Productive: [
    { title: "Plan Day", xp: 10 },
    { title: "Deep Work (1h)", xp: 40 },
    { title: "Email Zero", xp: 20 }
  ],
  Calm: [
    { title: "Breathe (5m)", xp: 10 },
    { title: "Journaling", xp: 20 },
    { title: "No Tech Bedtime", xp: 40 }
  ]
};

export const HabitSuggestions = () => {
  const user = useUserStore();
  const identity = (user.identityGoal as keyof typeof SUGGESTIONS) || "Productive";
  const items = SUGGESTIONS[identity] || SUGGESTIONS.Productive;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Sparkles size={16} color="#00ffcc" />
        <Text style={styles.title}>AI Recommendations</Text>
      </View>
      
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.scroll}>
        {items.map((item, index) => (
          <TouchableOpacity key={index} style={styles.card}>
            <Text style={styles.cardTitle}>{item.title}</Text>
            <View style={styles.footer}>
              <Text style={styles.xp}>+{item.xp} XP</Text>
              <View style={styles.plus}>
                <Plus size={12} color="#000" />
              </View>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { marginVertical: 20 },
  header: { flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 12, paddingHorizontal: 20 },
  title: { color: "rgba(255,255,255,0.6)", fontSize: 13, fontWeight: "600", textTransform: "uppercase" },
  scroll: { paddingHorizontal: 16 },
  card: { 
    backgroundColor: "#111", 
    width: 140, 
    height: 100, 
    borderRadius: 16, 
    padding: 12, 
    marginHorizontal: 4,
    justifyContent: "space-between",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.05)"
  },
  cardTitle: { color: "#fff", fontWeight: "600", fontSize: 14 },
  footer: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  xp: { color: "#00ffcc", fontSize: 11, fontWeight: "700" },
  plus: { backgroundColor: "#00ffcc", borderRadius: 10, width: 18, height: 18, alignItems: "center", justifyContent: "center" }
});
