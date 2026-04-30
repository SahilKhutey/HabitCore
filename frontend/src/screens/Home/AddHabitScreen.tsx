import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator
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
    mutation.mutate({ name, time });
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity 
        style={styles.backBtn} 
        onPress={() => navigation.goBack()}
      >
        <ArrowLeft size={24} color="#fff" />
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
              time === t && { backgroundColor: "#00ffcc" },
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
    backgroundColor: "#000",
    padding: 20,
    paddingTop: 60,
  },

  backBtn: {
    marginBottom: 20,
  },

  title: {
    color: "#fff",
    fontSize: 28,
    fontWeight: '800',
    marginBottom: 30,
  },

  input: {
    backgroundColor: "#111",
    padding: 20,
    borderRadius: 16,
    color: "#fff",
    fontSize: 18,
    marginBottom: 30,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },

  section: {
    color: "#666",
    fontWeight: '700',
    textTransform: 'uppercase',
    fontSize: 12,
    marginBottom: 15,
  },

  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginBottom: 30,
    gap: 10,
  },

  suggestion: {
    backgroundColor: "#111",
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },

  timeBtn: {
    backgroundColor: "#111",
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },

  saveBtn: {
    backgroundColor: "#00ffcc",
    padding: 18,
    borderRadius: 20,
    alignItems: "center",
    marginTop: 'auto',
    marginBottom: 20,
    shadowColor: "#00ffcc",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
});
