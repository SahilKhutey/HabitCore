import React from "react";
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, ActivityIndicator } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { getWeeklyReport, getLeaderboard } from "../../api/client";
import { useUserStore } from "../../store/useUserStore";
import { Trophy, BarChart2, TrendingUp, AlertCircle, User as UserIcon } from "lucide-react-native";
import Animated, { FadeInUp } from "react-native-reanimated";

export default function StatsScreen() {
  const { token } = useUserStore();

  const { data: report, isLoading: loadingReport } = useQuery({
    queryKey: ['weeklyReport'],
    queryFn: () => getWeeklyReport(token!),
    enabled: !!token,
  });

  const { data: leaderboard, isLoading: loadingLeaderboard } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: () => getLeaderboard(token!),
    enabled: !!token,
  });

  if (loadingReport || loadingLeaderboard) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <ActivityIndicator color="#00ffcc" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Performance</Text>

        {/* 📊 WEEKLY REPORT */}
        <Animated.View entering={FadeInUp} style={styles.card}>
          <View style={styles.cardHeader}>
            <BarChart2 size={20} color="#00ffcc" />
            <Text style={styles.cardTitle}>Weekly Report</Text>
          </View>
          
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{report?.total_completed || 0}</Text>
              <Text style={styles.statLabel}>Completions</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{report?.completion_rate || 0}%</Text>
              <Text style={styles.statLabel}>Rate</Text>
            </View>
          </View>

          <View style={styles.insightRow}>
            <TrendingUp size={16} color="#00ffcc" />
            <Text style={styles.insightText}>Best Day: <Text style={{ color: "#fff" }}>{report?.best_day || "N/A"}</Text></Text>
          </View>
          <View style={styles.insightRow}>
            <AlertCircle size={16} color="#ff5500" />
            <Text style={styles.insightText}>{report?.improvement_tip}</Text>
          </View>
        </Animated.View>

        {/* 🏆 LEADERBOARD */}
        <Text style={styles.sectionTitle}>Global Ranking</Text>
        <Animated.View entering={FadeInUp.delay(200)} style={styles.card}>
          <View style={styles.cardHeader}>
            <Trophy size={20} color="#ffd700" />
            <Text style={styles.cardTitle}>Top Performers</Text>
          </View>

          {leaderboard?.top_users.map((user: any, index: number) => (
            <View 
              key={user.id} 
              style={[
                styles.leaderboardItem, 
                user.is_me && styles.myLeaderboardItem,
                index === leaderboard.top_users.length - 1 && { borderBottomWidth: 0 }
              ]}
            >
              <View style={styles.rankContainer}>
                <Text style={[styles.rankText, index < 3 && { color: "#ffd700" }]}>#{index + 1}</Text>
              </View>
              <UserIcon size={16} color={user.is_me ? "#00ffcc" : "#666"} style={{ marginRight: 10 }} />
              <Text style={[styles.userName, user.is_me && { color: "#00ffcc", fontWeight: '800' }]}>
                {user.name} {user.is_me ? "(You)" : ""}
              </Text>
              <Text style={styles.userScore}>{user.score} ✔</Text>
            </View>
          ))}

          {leaderboard?.my_rank > 10 && (
            <View style={[styles.leaderboardItem, styles.myLeaderboardItem, { marginTop: 10, borderRadius: 10 }]}>
                <Text style={styles.rankText}>#{leaderboard.my_rank}</Text>
                <Text style={[styles.userName, { color: "#00ffcc" }]}> You</Text>
                <Text style={styles.userScore}>{leaderboard.top_users.find((u: any) => u.is_me)?.score || 0} ✔</Text>
            </View>
          )}
        </Animated.View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  scrollContent: { padding: 20 },
  title: { color: "#fff", fontSize: 28, fontWeight: "800", marginBottom: 25, marginTop: 10 },
  sectionTitle: { color: "#666", fontSize: 14, fontWeight: "700", textTransform: "uppercase", marginBottom: 15, marginTop: 25 },
  card: { 
    backgroundColor: "#111", 
    borderRadius: 20, 
    padding: 20, 
    borderWidth: 1, 
    borderColor: "rgba(255,255,255,0.05)" 
  },
  cardHeader: { flexDirection: "row", alignItems: "center", gap: 10, marginBottom: 20 },
  cardTitle: { color: "#fff", fontSize: 16, fontWeight: "700" },
  statsRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: 20 },
  statItem: { flex: 1 },
  statValue: { color: "#fff", fontSize: 32, fontWeight: "900" },
  statLabel: { color: "#666", fontSize: 12, fontWeight: "600" },
  insightRow: { flexDirection: "row", alignItems: "center", gap: 10, marginBottom: 10 },
  insightText: { color: "#888", fontSize: 14 },
  leaderboardItem: { 
    flexDirection: "row", 
    alignItems: "center", 
    paddingVertical: 15, 
    borderBottomWidth: 1, 
    borderBottomColor: "rgba(255,255,255,0.05)" 
  },
  myLeaderboardItem: { backgroundColor: "rgba(0, 255, 204, 0.05)", marginHorizontal: -10, paddingHorizontal: 10 },
  rankContainer: { width: 40 },
  rankText: { color: "#666", fontSize: 14, fontWeight: "800" },
  userName: { color: "#fff", fontSize: 14, flex: 1 },
  userScore: { color: "#fff", fontSize: 14, fontWeight: "800" }
});
