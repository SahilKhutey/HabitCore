import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../../theme/theme';
import { MotiView, MotiText } from 'moti';
import { Dumbbell, Book, Briefcase, Brain } from 'lucide-react-native';

const GOALS = [
  { id: 'fitness', label: 'Fitness', icon: <Dumbbell color={COLORS.neonGreen} />, suggestions: ['Drink 2L Water', '10 min Workout', 'Walk 5k steps'] },
  { id: 'study', label: 'Study', icon: <Book color={COLORS.primary} />, suggestions: ['Read 10 pages', 'Study 30 min', 'Review notes'] },
  { id: 'productivity', label: 'Productivity', icon: <Briefcase color={COLORS.accent} />, suggestions: ['Deep work 1h', 'Clear inbox', 'Plan tomorrow'] },
  { id: 'mindfulness', label: 'Mindfulness', icon: <Brain color={COLORS.secondary} />, suggestions: ['Meditate 5 min', 'Journal entry', 'Deep breathing'] },
];

export default function OnboardingScreen({ navigation }: any) {
  const [step, setStep] = useState(0);
  const [selectedGoal, setSelectedGoal] = useState<string | null>(null);

  const nextStep = () => {
    if (step < 2) setStep(step + 1);
    else navigation.navigate('Login');
  };

  return (
    <SafeAreaView style={styles.container}>
      {step === 0 && (
        <MotiView 
          from={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          style={styles.stepContainer}
        >
          <Text style={[TYPOGRAPHY.h1, styles.title]}>Build your dream habits 🚀</Text>
          <TouchableOpacity style={styles.button} onPress={nextStep}>
            <Text style={styles.buttonText}>Start Journey</Text>
          </TouchableOpacity>
        </MotiView>
      )}

      {step === 1 && (
        <View style={styles.stepContainer}>
          <Text style={[TYPOGRAPHY.h2, styles.subtitle]}>What do you want to improve?</Text>
          <View style={styles.grid}>
            {GOALS.map((goal) => (
              <TouchableOpacity 
                key={goal.id} 
                style={[styles.goalCard, selectedGoal === goal.id && styles.selectedGoal]}
                onPress={() => {
                  setSelectedGoal(goal.id);
                  nextStep();
                }}
              >
                {goal.icon}
                <Text style={styles.goalLabel}>{goal.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}

      {step === 2 && (
        <View style={styles.stepContainer}>
          <Text style={[TYPOGRAPHY.h2, styles.subtitle]}>Suggested habits for you:</Text>
          {GOALS.find(g => g.id === selectedGoal)?.suggestions.map((s, i) => (
            <MotiView 
              key={s}
              from={{ opacity: 0, translateX: -20 }}
              animate={{ opacity: 1, translateX: 0 }}
              transition={{ delay: i * 100 }}
              style={styles.suggestionItem}
            >
              <Text style={styles.suggestionText}>+ {s}</Text>
            </MotiView>
          ))}
          <TouchableOpacity style={[styles.button, { marginTop: SPACING.xl }]} onPress={nextStep}>
            <Text style={styles.buttonText}>Add Habits & Begin</Text>
          </TouchableOpacity>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    padding: SPACING.xl,
  },
  stepContainer: {
    alignItems: 'center',
    width: '100%',
  },
  title: {
    textAlign: 'center',
    fontSize: 32,
    marginBottom: SPACING.xl,
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: SPACING.xl,
  },
  button: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 16,
    width: '100%',
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '700',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    width: '100%',
  },
  goalCard: {
    width: '48%',
    backgroundColor: COLORS.surface,
    padding: SPACING.md,
    borderRadius: 20,
    alignItems: 'center',
    marginBottom: SPACING.md,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  selectedGoal: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
  },
  goalLabel: {
    color: COLORS.text,
    marginTop: 8,
    fontWeight: '600',
  },
  suggestionItem: {
    width: '100%',
    backgroundColor: COLORS.surface,
    padding: SPACING.md,
    borderRadius: 12,
    marginBottom: SPACING.sm,
  },
  suggestionText: {
    color: COLORS.neonGreen,
    fontWeight: '600',
  },
});
