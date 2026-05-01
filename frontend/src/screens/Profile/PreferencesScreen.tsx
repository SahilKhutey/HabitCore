import React from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Alert, ActivityIndicator } from "react-native";
import { useUserStore, UserState } from "../../store/useUserStore";
import { updatePreferences } from "../../api/client";
import { COLORS, SPACING, TYPOGRAPHY } from "../../theme/theme";
import { useMutation } from "@tanstack/react-query";
import { Zap, Target, Trophy, Coffee, ChevronRight } from "lucide-react-native";
import { triggerHaptic } from "../../utils/animationManager";

export default function PreferencesScreen() {
  const { token, mode, progress_style, engagement_level, identity_goal, setUserInfo } = useUserStore();

  const mutation = useMutation({
    mutationFn: (data: any) => updatePreferences(data, token!),
    onSuccess: (_, variables) => {
      triggerHaptic("success");
      setUserInfo(variables);
    },
    onError: () => {
      triggerHaptic("error");
      Alert.alert("Error", "Failed to save preferences");
    }
  });

  const renderSection = (title: string, current: string, key: string, options: any[]) => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <View style={styles.grid}>
        {options.map((opt) => {
          const isActive = current === opt.id;
          return (
            <TouchableOpacity
              key={opt.id}
              style={[styles.card, isActive && styles.activeCard]}
              onPress={() => mutation.mutate({ [key]: opt.id })}
              activeOpacity={0.8}
            >
              <View style={[styles.iconContainer, isActive && styles.activeIconContainer]}>
                {opt.icon || <ChevronRight size={16} color={isActive ? COLORS.primary : COLORS.textDim} />}
              </View>
              <Text style={[styles.cardText, isActive && styles.activeCardText]}>{opt.id}</Text>
              {opt.desc && <Text style={[styles.cardDesc, isActive && styles.activeCardDesc]}>{opt.desc}</Text>}
              {isActive && <View style={styles.activeIndicator} />}
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 100 }}>
      <View style={styles.header}>
        <Text style={styles.title}>Ritual Config</Text>
        {mutation.isPending && <ActivityIndicator size="small" color={COLORS.primary} />}
      </View>
      
      {renderSection("Progression Mode", mode, "mode", [
        { id: "Speed", icon: <Zap size={20} color="#00ffcc" />, desc: "Fast XP, low streak focus" },
        { id: "Consistency", icon: <Target size={20} color="#a855f7" />, desc: "Double streak bonuses" },
        { id: "Competitive", icon: <Trophy size={20} color="#eab308" />, desc: "Leaderboard & Ranks" },
      ])}

      {renderSection("Identity Anchor", identity_goal, "identity_goal", [
        { id: "Fit", desc: "Physical health focus" },
        { id: "Learner", desc: "Mental growth focus" },
        { id: "Productive", desc: "Efficiency focus" },
        { id: "Calm", desc: "Mindfulness focus" },
      ])}

      {renderSection("Nudge Intensity", engagement_level, "engagement_level", [
        { id: "Chill", desc: "Minimal notifications" },
        { id: "Balanced", desc: "Standard triggers" },
        { id: "Intense", desc: "Maximum accountability" },
      ])}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 32, marginTop: 60, paddingHorizontal: 24 },
  title: { color: COLORS.text, fontSize: 36, fontWeight: "900", letterSpacing: -1 },
  section: { marginBottom: 40, paddingHorizontal: 24 },
  sectionTitle: { color: COLORS.primary, fontSize: 12, textTransform: "uppercase", fontWeight: "800", marginBottom: 20, letterSpacing: 2, opacity: 0.8 },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: 16 },
  card: { 
    width: "47%", 
    backgroundColor: "rgba(255,255,255,0.03)", 
    padding: 20, 
    borderRadius: 24, 
    borderWidth: 1, 
    borderColor: "rgba(255,255,255,0.08)",
    position: "relative",
    overflow: "hidden"
  },
  activeCard: { 
    borderColor: COLORS.primary, 
    backgroundColor: "rgba(56,189,248,0.1)",
    borderWidth: 2
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: "rgba(255,255,255,0.05)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 12
  },
  activeIconContainer: {
    backgroundColor: "rgba(56,189,248,0.2)"
  },
  cardText: { color: COLORS.textSecondary, fontWeight: "700", fontSize: 16 },
  activeCardText: { color: COLORS.text, fontWeight: "800" },
  cardDesc: { color: "rgba(148,163,184,0.6)", fontSize: 11, marginTop: 6, lineHeight: 14, fontWeight: "500" },
  activeCardDesc: { color: COLORS.textSecondary },
  activeIndicator: {
    position: "absolute",
    top: 12,
    right: 12,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: COLORS.primary,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 4,
    elevation: 5
  }
});
