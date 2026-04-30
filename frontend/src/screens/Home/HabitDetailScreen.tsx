import React, { useState } from "react";
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, Dimensions } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { getHabitHistory } from "../../api/client";
import { useUserStore } from "../../store/useUserStore";
import { ArrowLeft, Calendar, Grid, Flame, Share as ShareIcon } from "lucide-react-native";
import Animated, { FadeInUp, Layout } from "react-native-reanimated";
import Share from "react-native-share";

const { width } = Dimensions.get("window");

export default function HabitDetailScreen({ route, navigation }: any) {
  const { habit } = route.params;
  const { token } = useUserStore();
  const [view, setView] = useState<"month" | "year">("month");

  const { data: history = [] } = useQuery({
    queryKey: ['habitHistory', habit.id],
    queryFn: () => getHabitHistory(habit.id, token!),
    enabled: !!token,
  });

  const renderMonthGrid = () => {
    const daysInMonth = 30; // Simplified for MVP
    const currentMonth = "April 2026";
    
    return (
      <Animated.View entering={FadeInUp} style={styles.card}>
        <Text style={styles.cardTitle}>{currentMonth}</Text>
        <View style={styles.gridContainer}>
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const dayNum = i + 1;
            // Match ISO date string (YYYY-MM-DD)
            const dateStr = `2026-04-${dayNum.toString().padStart(2, '0')}`;
            const isDone = history.includes(dateStr);
            const isToday = dayNum === 30; // Mock today for visual

            return (
              <View 
                key={i} 
                style={[
                  styles.dayBox, 
                  { backgroundColor: isDone ? "#00ffcc" : "#222" },
                  isToday && styles.todayBox
                ]}
              >
                <Text style={[styles.dayText, { color: isDone ? "#000" : "#666" }]}>
                  {dayNum}
                </Text>
              </View>
            );
          })}
        </View>
      </Animated.View>
    );
  };

  const renderYearHeatmap = () => {
    const totalDays = 365;
    return (
      <Animated.View entering={FadeInUp} style={styles.card}>
        <Text style={styles.cardTitle}>Year Activity</Text>
        <View style={styles.heatmapContainer}>
          {Array.from({ length: totalDays }).map((_, i) => (
            <View 
              key={i} 
              style={[
                styles.heatBox, 
                { backgroundColor: Math.random() > 0.8 ? "#00ffcc" : "#111" } // Mock some data
              ]} 
            />
          ))}
        </View>
        <View style={styles.heatmapLegend}>
          <Text style={styles.legendText}>Less</Text>
          <View style={[styles.heatBox, { backgroundColor: "#111" }]} />
          <View style={[styles.heatBox, { backgroundColor: "#00ffcc" }]} />
          <Text style={styles.legendText}>More</Text>
        </View>
      </Animated.View>
    );
  };

  const shareStreak = async () => {
    try {
      const streak = habit.streak?.current_streak || 0;
      await Share.open({
        message: `🔥 I'm on a ${streak}-day streak for "${habit.name || habit.title}"! Join me on HabitHero 💪`,
      });
    } catch (err) {
      console.log("Share failed", err);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <ArrowLeft size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.title}>{habit.name || habit.title}</Text>
        <TouchableOpacity onPress={shareStreak}>
          <ShareIcon size={24} color="#00ffcc" />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* STATS SUMMARY */}
        <View style={styles.statsRow}>
            <View style={styles.statCard}>
                <Flame size={20} color="#ff5500" />
                <Text style={styles.statValue}>{habit.streak?.current_streak || 0}</Text>
                <Text style={styles.statLabel}>Streak</Text>
            </View>
            <View style={styles.statCard}>
                <Calendar size={20} color="#00ffcc" />
                <Text style={styles.statValue}>{history.length}</Text>
                <Text style={styles.statLabel}>Total</Text>
            </View>
        </View>

        {/* VIEW SELECTOR */}
        <View style={styles.selector}>
          <TouchableOpacity 
            onPress={() => setView("month")}
            style={[styles.selectorBtn, view === "month" && styles.selectorActive]}
          >
            <Calendar size={18} color={view === "month" ? "#000" : "#fff"} />
            <Text style={[styles.selectorText, { color: view === "month" ? "#000" : "#fff" }]}>Month</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            onPress={() => setView("year")}
            style={[styles.selectorBtn, view === "year" && styles.selectorActive]}
          >
            <Grid size={18} color={view === "year" ? "#000" : "#fff"} />
            <Text style={[styles.selectorText, { color: view === "year" ? "#000" : "#fff" }]}>Year</Text>
          </TouchableOpacity>
        </View>

        {view === "month" ? renderMonthGrid() : renderYearHeatmap()}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  header: { 
    flexDirection: "row", 
    justifyContent: "space-between", 
    alignItems: "center", 
    padding: 20,
    paddingTop: 40 
  },
  title: { color: "#fff", fontSize: 20, fontWeight: "800" },
  scrollContent: { padding: 20 },
  statsRow: { flexDirection: "row", gap: 15, marginBottom: 25 },
  statCard: { 
    flex: 1, 
    backgroundColor: "#111", 
    borderRadius: 16, 
    padding: 20, 
    alignItems: "center",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.05)"
  },
  statValue: { color: "#fff", fontSize: 24, fontWeight: "900", marginVertical: 5 },
  statLabel: { color: "#666", fontSize: 12, fontWeight: "700", textTransform: "uppercase" },
  selector: { 
    flexDirection: "row", 
    backgroundColor: "#111", 
    borderRadius: 12, 
    padding: 4, 
    marginBottom: 25 
  },
  selectorBtn: { 
    flex: 1, 
    flexDirection: "row", 
    alignItems: "center", 
    justifyContent: "center", 
    paddingVertical: 10, 
    borderRadius: 8,
    gap: 8
  },
  selectorActive: { backgroundColor: "#00ffcc" },
  selectorText: { fontWeight: "700", fontSize: 14 },
  card: { 
    backgroundColor: "#111", 
    borderRadius: 20, 
    padding: 20, 
    borderWidth: 1, 
    borderColor: "rgba(255,255,255,0.05)" 
  },
  cardTitle: { color: "#fff", fontSize: 18, fontWeight: "800", marginBottom: 20 },
  gridContainer: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  dayBox: { 
    width: (width - 100) / 7, 
    aspectRatio: 1, 
    borderRadius: 8, 
    alignItems: "center", 
    justifyContent: "center" 
  },
  todayBox: { borderWidth: 2, borderColor: "#fff" },
  dayText: { fontSize: 12, fontWeight: "800" },
  heatmapContainer: { flexDirection: "row", flexWrap: "wrap", gap: 4 },
  heatBox: { width: 10, height: 10, borderRadius: 2 },
  heatmapLegend: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: 20, alignSelf: "flex-end" },
  legendText: { color: "#666", fontSize: 10 }
});
