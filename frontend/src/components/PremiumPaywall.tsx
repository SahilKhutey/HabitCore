import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Modal } from "react-native";
import { useUserStore } from "../store/useUserStore";
import { Flame, CheckCircle2, ShieldCheck, Zap } from "lucide-react-native";
import { BlurView } from "expo-blur";
import { MotiView } from "moti";

export const PremiumPaywall = ({ visible, onClose }: { visible: boolean, onClose: () => void }) => {
  const user = useUserStore();

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.overlay}>
        <BlurView intensity={80} tint="dark" style={StyleSheet.absoluteFill} />
        
        <MotiView 
          from={{ translateY: 300 }}
          animate={{ translateY: 0 }}
          style={styles.container}
        >
          <View style={styles.streakAlert}>
            <Flame size={40} color="#f59e0b" fill="#f59e0b" />
            <Text style={styles.streakTitle}>Don't Break Your Streak!</Text>
            <Text style={styles.streakSub}>You've built 5 days of momentum. Protect it now.</Text>
          </View>

          <View style={styles.benefits}>
            <Benefit icon={<ShieldCheck size={20} color="#00ffcc" />} text="Unlimited Streak Freezes" />
            <Benefit icon={<Zap size={20} color="#a855f7" />} text="Advanced Behavioral Insights" />
            <Benefit icon={<CheckCircle2 size={20} color="#3b82f6" />} text="Unlimited Habits & Quests" />
          </View>

          <TouchableOpacity style={styles.upgradeButton} onPress={onClose}>
            <Text style={styles.upgradeText}>Unlock Premium – $4.99/mo</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.skipButton} onPress={onClose}>
            <Text style={styles.skipText}>Maybe later</Text>
          </TouchableOpacity>
        </MotiView>
      </View>
    </Modal>
  );
};

const Benefit = ({ icon, text }: { icon: any, text: string }) => (
  <View style={styles.benefitItem}>
    {icon}
    <Text style={styles.benefitText}>{text}</Text>
  </View>
);

const styles = StyleSheet.create({
  overlay: { flex: 1, justifyContent: "flex-end" },
  container: { 
    backgroundColor: "#111", 
    borderTopLeftRadius: 32, 
    borderTopRightRadius: 32, 
    padding: 32, 
    paddingBottom: 48,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.1)"
  },
  streakAlert: { alignItems: "center", marginBottom: 32 },
  streakTitle: { color: "#fff", fontSize: 24, fontWeight: "800", marginTop: 16 },
  streakSub: { color: "rgba(255,255,255,0.5)", textAlign: "center", marginTop: 8 },
  benefits: { marginBottom: 32 },
  benefitItem: { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 16 },
  benefitText: { color: "#fff", fontSize: 16, fontWeight: "500" },
  upgradeButton: { backgroundColor: "#00ffcc", height: 56, borderRadius: 16, alignItems: "center", justifyContent: "center" },
  upgradeText: { color: "#000", fontSize: 18, fontWeight: "700" },
  skipButton: { alignItems: "center", marginTop: 20 },
  skipText: { color: "rgba(255,255,255,0.3)", fontSize: 14 }
});
