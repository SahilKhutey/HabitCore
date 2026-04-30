import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Dimensions } from "react-native";
import { useUserStore } from "../../store/useUserStore";
import { MotiView } from "moti";
import { ArrowRight, Check } from "lucide-react-native";

const { width } = Dimensions.get("window");

const STEPS = [
  {
    id: "identity",
    title: "Who do you want to become?",
    options: [
      { id: "Fit", label: "💪 Fit", desc: "Focus on health & energy" },
      { id: "Learner", label: "📚 Learner", desc: "Focus on growth & skills" },
      { id: "Productive", label: "🚀 Productive", desc: "Focus on efficiency" },
      { id: "Calm", label: "🧘 Calm", desc: "Focus on peace & mindfulness" }
    ]
  },
  {
    id: "mode",
    title: "Choose your progression style",
    options: [
      { id: "Speed", label: "⚡ Speed Runner", desc: "Fast XP, rapid growth" },
      { id: "Consistency", label: "🔥 Consistency King", desc: "High streak rewards" },
      { id: "Competitive", label: "🏆 Competitive", desc: "Leaderboards & ranks" },
      { id: "Minimal", label: "🍃 Minimalist", desc: "Quiet, no pressure" }
    ]
  },
  {
    id: "engagement",
    title: "How intense should we be?",
    options: [
      { id: "Chill", label: "🍃 Chill", desc: "Gentle reminders" },
      { id: "Balanced", label: "⚖️ Balanced", desc: "Standard tracking" },
      { id: "Intense", label: "🔥 Intense", desc: "Aggressive streak alerts" }
    ]
  }
];

export default function OnboardingFlow({ onFinish }: { onFinish: () => void }) {
  const [currentStep, setCurrentStep] = useState(0);
  const { updatePreferences } = useUserStore();
  const step = STEPS[currentStep];

  const handleSelect = (id: string) => {
    updatePreferences({ [step.id]: id });
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onFinish();
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.progressHeader}>
        {STEPS.map((_, i) => (
          <View 
            key={i} 
            style={[styles.progressDot, i <= currentStep && styles.activeDot]} 
          />
        ))}
      </View>

      <MotiView 
        from={{ opacity: 0, translateX: 50 }}
        animate={{ opacity: 1, translateX: 0 }}
        key={currentStep}
        style={styles.content}
      >
        <Text style={styles.title}>{step.title}</Text>
        
        {step.options.map((option) => (
          <TouchableOpacity 
            key={option.id} 
            style={styles.optionCard}
            onPress={() => handleSelect(option.id)}
          >
            <View>
              <Text style={styles.optionLabel}>{option.label}</Text>
              <Text style={styles.optionDesc}>{option.desc}</Text>
            </View>
            <ArrowRight size={20} color="rgba(255,255,255,0.3)" />
          </TouchableOpacity>
        ))}
      </MotiView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000", padding: 24, justifyContent: "center" },
  progressHeader: { flexDirection: "row", gap: 8, marginBottom: 40 },
  progressDot: { flex: 1, height: 4, backgroundColor: "#222", borderRadius: 2 },
  activeDot: { backgroundColor: "#00ffcc" },
  content: { flex: 1 },
  title: { color: "#fff", fontSize: 28, fontWeight: "800", marginBottom: 32 },
  optionCard: { 
    flexDirection: "row", 
    justifyContent: "space-between", 
    alignItems: "center",
    backgroundColor: "#111", 
    padding: 20, 
    borderRadius: 20, 
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.05)"
  },
  optionLabel: { color: "#fff", fontSize: 18, fontWeight: "700" },
  optionDesc: { color: "rgba(255,255,255,0.4)", fontSize: 13, marginTop: 4 }
});
