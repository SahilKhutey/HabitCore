import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from "react-native";
import { COLORS } from "../../theme/theme";
import { ArrowLeft, CheckCircle2, ChevronRight } from "lucide-react-native";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useUserStore } from "../../store/useUserStore";

export default function FocusModeScreen({ navigation }: any) {
  const { token } = useUserStore();
  const [currentIndex, setCurrentIndex] = useState(0);

  const { data: habits, isLoading } = useQuery({
    queryKey: ['habits'],
    queryFn: () => api('/habits/', 'GET', null, token)
  });

  const activeHabits = habits?.filter((h: any) => !h.is_completed) || [];

  if (isLoading) return <View style={styles.container}><Text style={styles.loading}>Entering Focus Zone...</Text></View>;

  const currentHabit = activeHabits[currentIndex];

  const handleComplete = () => {
    // In production, call API to complete habit
    if (currentIndex < activeHabits.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      navigation.goBack();
    }
  };

  if (!currentHabit) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.doneText}>🎉 All focus tasks complete!</Text>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backBtnText}>Return to Dashboard</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <ArrowLeft color="#fff" size={24} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Focus Zone</Text>
        <View style={{ width: 24 }} />
      </View>

      <View style={styles.content}>
        <Text style={styles.progressText}>Task {currentIndex + 1} of {activeHabits.length}</Text>
        <Text style={styles.habitName}>{currentHabit.name}</Text>
        
        <TouchableOpacity style={styles.completeBtn} onPress={handleComplete}>
          <CheckCircle2 color="#000" size={32} />
          <Text style={styles.completeBtnText}>Mark Done</Text>
        </TouchableOpacity>

        {currentIndex < activeHabits.length - 1 && (
            <TouchableOpacity style={styles.skipBtn} onPress={() => setCurrentIndex(currentIndex + 1)}>
                <Text style={styles.skipBtnText}>Skip for now</Text>
                <ChevronRight color={COLORS.textDim} size={20} />
            </TouchableOpacity>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
  },
  headerTitle: {
    color: "#fff",
    fontSize: 18,
    fontWeight: '700',
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  progressText: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 10,
    textTransform: 'uppercase',
  },
  habitName: {
    color: "#fff",
    fontSize: 32,
    fontWeight: '900',
    textAlign: 'center',
    marginBottom: 60,
  },
  completeBtn: {
    backgroundColor: COLORS.primary,
    paddingVertical: 20,
    paddingHorizontal: 40,
    borderRadius: 30,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    elevation: 10,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
  },
  completeBtnText: {
    color: "#000",
    fontSize: 18,
    fontWeight: '800',
  },
  skipBtn: {
    marginTop: 30,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  skipBtnText: {
    color: COLORS.textDim,
    fontSize: 16,
  },
  doneText: {
    color: "#fff",
    fontSize: 24,
    fontWeight: '800',
    textAlign: 'center',
    marginTop: 100,
  },
  backBtn: {
    marginTop: 40,
    alignSelf: 'center',
    padding: 15,
  },
  backBtnText: {
    color: COLORS.primary,
    fontSize: 16,
    fontWeight: '600',
  },
  loading: {
    color: "#fff",
    fontSize: 18,
  }
});
