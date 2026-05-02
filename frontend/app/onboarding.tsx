import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, Dimensions } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../src/theme/theme';
import { MotiView, AnimatePresence } from 'moti';
import { Dumbbell, Briefcase, Brain, Zap, Clock, Rocket } from 'lucide-react-native';
import { router } from 'expo-router';

const { width } = Dimensions.get('window');

const IDENTITIES = [
  { id: 'fit', label: 'Fit & Energetic', icon: <Dumbbell color={COLORS.primary} />, habits: ['Drink 2L Water', '10 min Workout'] },
  { id: 'focused', label: 'Deeply Focused', icon: <Brain color={COLORS.secondary} />, habits: ['Meditate 5 min', 'Deep Work 1h'] },
  { id: 'productive', label: 'High Achiever', icon: <Briefcase color={COLORS.accent} />, habits: ['Read 10 pages', 'Plan Tomorrow'] },
];

export default function OnboardingScreen() {
  const [step, setStep] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [reminderTime, setReminderTime] = useState('09:00 AM');

  const nextStep = () => {
    if (step < 4) setStep(step + 1);
    else router.replace('/auth/login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <AnimatePresence exitBeforeEnter>
        {step === 0 && (
          <MotiView 
            key="step0"
            from={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            style={styles.stepContainer}
          >
            <Zap size={64} color={COLORS.primary} style={{ marginBottom: 20 }} />
            <Text style={styles.heroTitle}>Build Habits{"\n"}That Stick</Text>
            <Text style={styles.heroSub}>The gamified ecosystem designed for consistency, not complexity.</Text>
            <TouchableOpacity style={styles.primaryBtn} onPress={nextStep}>
              <Text style={styles.btnText}>Start Journey</Text>
            </TouchableOpacity>
          </MotiView>
        )}

        {step === 1 && (
          <MotiView 
            key="step1"
            from={{ opacity: 0, translateX: 50 }}
            animate={{ opacity: 1, translateX: 0 }}
            exit={{ opacity: 0, translateX: -50 }}
            style={styles.stepContainer}
          >
            <Text style={styles.title}>Who do you want to become?</Text>
            <View style={styles.identityList}>
              {IDENTITIES.map((item) => (
                <TouchableOpacity 
                  key={item.id} 
                  style={[styles.idCard, selectedId === item.id && styles.selectedCard]}
                  onPress={() => {
                    setSelectedId(item.id);
                    nextStep();
                  }}
                >
                  <View style={styles.idIcon}>{item.icon}</View>
                  <Text style={styles.idLabel}>{item.label}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </MotiView>
        )}

        {step === 2 && (
          <MotiView 
            key="step2"
            from={{ opacity: 0, translateX: 50 }}
            animate={{ opacity: 1, translateX: 0 }}
            exit={{ opacity: 0, translateX: -50 }}
            style={styles.stepContainer}
          >
            <Text style={styles.title}>Start with these 2 habits</Text>
            <Text style={styles.subtitle}>Small actions lead to massive identity shifts.</Text>
            <View style={styles.habitList}>
                {IDENTITIES.find(i => i.id === selectedId)?.habits.map((h, i) => (
                    <View key={i} style={styles.habitItem}>
                        <View style={styles.checkCircle}><Text style={{color: COLORS.primary}}>✔</Text></View>
                        <Text style={styles.habitText}>{h}</Text>
                    </View>
                ))}
            </View>
            <TouchableOpacity style={styles.primaryBtn} onPress={nextStep}>
              <Text style={styles.btnText}>Sounds Perfect</Text>
            </TouchableOpacity>
          </MotiView>
        )}

        {step === 3 && (
          <MotiView 
            key="step3"
            from={{ opacity: 0, translateX: 50 }}
            animate={{ opacity: 1, translateX: 0 }}
            exit={{ opacity: 0, translateX: -50 }}
            style={styles.stepContainer}
          >
            <Clock size={48} color={COLORS.primary} style={{ marginBottom: 20 }} />
            <Text style={styles.title}>Set your morning nudge</Text>
            <View style={styles.timeGrid}>
                {['07:00 AM', '08:00 AM', '09:00 AM'].map((t) => (
                    <TouchableOpacity 
                        key={t} 
                        style={[styles.timeBtn, reminderTime === t && styles.selectedTime]}
                        onPress={() => setReminderTime(t)}
                    >
                        <Text style={[styles.timeText, reminderTime === t && { color: '#000' }]}>{t}</Text>
                    </TouchableOpacity>
                ))}
            </View>
            <TouchableOpacity style={styles.primaryBtn} onPress={nextStep}>
              <Text style={styles.btnText}>Set Reminder</Text>
            </TouchableOpacity>
          </MotiView>
        )}

        {step === 4 && (
          <MotiView 
            key="step4"
            from={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            style={styles.stepContainer}
          >
            <Rocket size={80} color={COLORS.primary} style={{ marginBottom: 30 }} />
            <Text style={styles.heroTitle}>You're Ready!</Text>
            <Text style={styles.heroSub}>Your identity shift starts now. Welcome to the elite.</Text>
            <TouchableOpacity style={styles.primaryBtn} onPress={nextStep}>
              <Text style={styles.btnText}>Enter Dashboard</Text>
            </TouchableOpacity>
          </MotiView>
        )}
      </AnimatePresence>

      <View style={styles.progressDots}>
        {[0,1,2,3,4].map((i) => (
            <View key={i} style={[styles.dot, step === i && styles.activeDot]} />
        ))}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    padding: 24,
  },
  stepContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  heroTitle: {
    color: COLORS.text,
    fontSize: 40,
    fontWeight: '900',
    textAlign: 'center',
    lineHeight: 48,
  },
  heroSub: {
    color: COLORS.textDim,
    fontSize: 16,
    textAlign: 'center',
    marginTop: 15,
    marginBottom: 40,
    lineHeight: 24,
    paddingHorizontal: 20,
  },
  title: {
    color: COLORS.text,
    fontSize: 24,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 30,
  },
  subtitle: {
    color: COLORS.textDim,
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 30,
  },
  primaryBtn: {
    backgroundColor: COLORS.primary,
    paddingVertical: 18,
    paddingHorizontal: 40,
    borderRadius: 20,
    width: '100%',
    alignItems: 'center',
  },
  btnText: {
    color: '#000',
    fontSize: 18,
    fontWeight: '800',
  },
  identityList: {
    width: '100%',
    gap: 15,
  },
  idCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  selectedCard: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(0, 255, 204, 0.05)',
  },
  idIcon: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: 10,
    borderRadius: 12,
    marginRight: 15,
  },
  idLabel: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: '700',
  },
  habitList: {
    width: '100%',
    marginBottom: 40,
    gap: 12,
  },
  habitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.02)',
    padding: 15,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  checkCircle: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  habitText: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: '600',
  },
  timeGrid: {
    width: '100%',
    gap: 10,
    marginBottom: 40,
  },
  timeBtn: {
    padding: 20,
    borderRadius: 16,
    backgroundColor: COLORS.surface,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  selectedTime: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  timeText: {
    color: COLORS.text,
    fontSize: 18,
    fontWeight: '800',
  },
  progressDots: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
    paddingBottom: 20,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#333',
  },
  activeDot: {
    backgroundColor: COLORS.primary,
    width: 20,
  },
});
