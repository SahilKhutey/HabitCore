import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert
} from "react-native";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createHabit, updateHabit } from "../../api/client";
import { useUserStore } from "../../store/useUserStore";
import { triggerHaptic } from "../../utils/animationManager";
import { ArrowLeft } from "lucide-react-native";
import { scheduleHabitReminder } from "../../services/notificationService";

const suggestions = ["Drink Water", "Workout", "Read 10 min", "Meditation"];

export default function AddHabitScreen({ navigation, route }: any) {
  const habitToEdit = route.params?.habit;
  
  const [name, setName] = useState(habitToEdit?.name || habitToEdit?.title || "");
  const [time, setTime] = useState<string | null>(habitToEdit?.time || null);
  const { token } = useUserStore();
  const queryClient = useQueryClient();

  const isEditing = !!habitToEdit;

  const mutation = useMutation({
    mutationFn: (data: { name: string; time: string | null }) => 
        isEditing 
            ? updateHabit(habitToEdit.id, data.name, data.time, token!)
            : createHabit(data.name, data.time, token!),
    onSuccess: (data) => {
      triggerHaptic("level_up"); // Success feel
      
      // Schedule Reminder
      scheduleHabitReminder({ 
        id: data.id, 
        name: data.name, 
        time: data.time 
      });

      queryClient.invalidateQueries({ queryKey: ["habits"] });
      navigation.goBack(); // instant return
    },
    onError: (error: any) => {
        alert(error.message);
    }
  });

  const handleSave = () => {
    if (!name) return;
    
    // Premium Limit Check
    const habitsCount = queryClient.getQueryData<any[]>(["habits"])?.length || 0;
    const isPremium = useUserStore.getState().isPremium;

    if (!isPremium && habitsCount >= 3 && !isEditing) {
        Alert.alert(
            "Habit Limit Reached 🚀",
            "Upgrade to Premium to track unlimited habits and unlock your full potential.",
            [
                { text: "Maybe Later", style: "cancel" },
                { text: "View Plans", onPress: () => navigation.navigate("Paywall") }
            ]
        );
        return;
    }

    mutation.mutate({ name, time });
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity 
        style={styles.backBtn} 
        onPress={() => navigation.goBack()}
      >
        <ArrowLeft size={24} color={COLORS.text} />
      </TouchableOpacity>

      <Text style={styles.title}>Add Habit</Text>

      {/* INPUT */}
      <TextInput
        placeholder="Enter habit..."
        placeholderTextColor="#666"
        value={name}
        onChangeText={setName}
        style={styles.input}
        autoFocus
      />

      {/* SUGGESTIONS */}
      <Text style={styles.section}>Suggested</Text>
      <View style={styles.row}>
        {suggestions.map((s, i) => (
          <TouchableOpacity
            key={i}
            onPress={() => setName(s)}
            style={styles.suggestion}
          >
            <Text style={{ color: "#fff" }}>{s}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* TIME */}
      <Text style={styles.section}>Time (Optional)</Text>
      <View style={styles.row}>
        {["Morning", "Afternoon", "Night"].map((t) => (
          <TouchableOpacity
            key={t}
            onPress={() => setTime(t)}
            style={[
              styles.timeBtn,
              time === t && { backgroundColor: COLORS.primary },
            ]}
          >
            <Text style={{ color: time === t ? "#000" : "#fff", fontWeight: '700' }}>
              {t}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* SAVE */}
      <TouchableOpacity
        style={[styles.saveBtn, !name && { opacity: 0.5 }]}
        onPress={handleSave}
        disabled={mutation.isPending || !name}
      >
        {mutation.isPending ? (
          <ActivityIndicator color="#000" />
        ) : (
          <Text style={{ color: "#000", fontWeight: '800', fontSize: 16 }}>
            {isEditing ? "Update Habit" : "Save Habit"}
          </Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    padding: 20,
    paddingTop: 60,
  },

  backBtn: {
    marginBottom: 20,
  },

  title: {
    color: COLORS.text,
    fontSize: 28,
    fontWeight: '800',
    marginBottom: 30,
  },

  input: {
    backgroundColor: COLORS.surface,
    padding: 20,
    borderRadius: 20,
    color: COLORS.text,
    fontSize: 18,
    marginBottom: 30,
    borderWidth: 1,
    borderColor: COLORS.glassBorder,
  },

  section: {
    color: COLORS.textSecondary,
    fontWeight: '800',
    textTransform: 'uppercase',
    fontSize: 12,
    letterSpacing: 1,
    marginBottom: 15,
  },

  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginBottom: 30,
    gap: 10,
  },

  suggestion: {
    backgroundColor: COLORS.surface,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: COLORS.glassBorder,
  },

  timeBtn: {
    backgroundColor: COLORS.surface,
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: COLORS.glassBorder,
  },

  saveBtn: {
    backgroundColor: COLORS.secondary,
    padding: 18,
    borderRadius: 20,
    alignItems: "center",
    marginTop: 'auto',
    marginBottom: 20,
    shadowColor: COLORS.secondary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 8,
  },
});
