import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';
import { GlassCard } from './GlassCard';
import { Smile, Meh, Frown, Angry, Moon, Zap, ChevronRight } from 'lucide-react-native';
import { dailyCheckin } from '../api/client';
import { useUserStore } from '../store/useUserStore';
import { triggerHaptic } from '../utils/animationManager';

interface DailyCheckinProps {
  onComplete: (data: any) => void;
  isHindi?: boolean;
}

export default function DailyCheckin({ onComplete, isHindi = false }: DailyCheckinProps) {
  const [mood, setMood] = useState('');
  const [energyMorning, setEnergyMorning] = useState('');
  const [energyEvening, setEnergyEvening] = useState('');
  const [sleepQuality, setSleepQuality] = useState(3);
  const [loading, setLoading] = useState(false);
  const { token } = useUserStore();

  const moods = [
    { value: 'happy', icon: <Smile color="#4ade80" />, label: isHindi ? 'खुश' : 'Happy' },
    { value: 'neutral', icon: <Meh color="#94a3b8" />, label: isHindi ? 'सामान्य' : 'Neutral' },
    { value: 'sad', icon: <Frown color="#38bdf8" />, label: isHindi ? 'उदास' : 'Sad' },
    { value: 'angry', icon: <Angry color="#ef4444" />, label: isHindi ? 'गुस्सा' : 'Angry' },
    { value: 'tired', icon: <Moon color="#a855f7" />, label: isHindi ? 'थका' : 'Tired' }
  ];

  const energyLevels = [
    { value: 'high', label: isHindi ? 'उच्च' : 'High' },
    { value: 'medium', label: isHindi ? 'मध्यम' : 'Medium' },
    { value: 'low', label: isHindi ? 'कम' : 'Low' }
  ];

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const response = await dailyCheckin({
        mood,
        energy_morning: energyMorning,
        energy_evening: energyEvening,
        sleep_quality: sleepQuality
      }, token!);
      
      triggerHaptic("success");
      onComplete(response);
    } catch (error) {
      triggerHaptic("error");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>
        {isHindi ? 'आज आप कैसा महसूस कर रहे हैं?' : 'How are you feeling today?'}
      </Text>

      {/* Mood Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionLabel}>{isHindi ? 'मूड' : 'Mood'}</Text>
        <View style={styles.moodGrid}>
          {moods.map((m) => (
            <TouchableOpacity
              key={m.value}
              onPress={() => setMood(m.value)}
              style={[styles.moodCard, mood === m.value && styles.activeCard]}
            >
              {m.icon}
              <Text style={[styles.cardLabel, mood === m.value && styles.activeLabel]}>{m.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Energy Levels */}
      <View style={styles.section}>
        <Text style={styles.sectionLabel}>{isHindi ? 'सुबह की ऊर्जा' : 'Morning Energy'}</Text>
        <View style={styles.optionGrid}>
          {energyLevels.map((l) => (
            <TouchableOpacity
              key={l.value}
              onPress={() => setEnergyMorning(l.value)}
              style={[styles.optionCard, energyMorning === l.value && styles.activeCard]}
            >
              <Text style={[styles.optionText, energyMorning === l.value && styles.activeLabel]}>{l.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionLabel}>{isHindi ? 'शाम की ऊर्जा' : 'Evening Energy'}</Text>
        <View style={styles.optionGrid}>
          {energyLevels.map((l) => (
            <TouchableOpacity
              key={l.value}
              onPress={() => setEnergyEvening(l.value)}
              style={[styles.optionCard, energyEvening === l.value && styles.activeCard]}
            >
              <Text style={[styles.optionText, energyEvening === l.value && styles.activeLabel]}>{l.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Sleep Quality */}
      <View style={styles.section}>
        <Text style={styles.sectionLabel}>{isHindi ? 'नींद की गुणवत्ता (1-5)' : 'Sleep Quality (1-5)'}</Text>
        <View style={styles.sleepGrid}>
          {[1, 2, 3, 4, 5].map((num) => (
            <TouchableOpacity
              key={num}
              onPress={() => setSleepQuality(num)}
              style={[styles.sleepNum, sleepQuality === num && styles.activeSleepNum]}
            >
              <Text style={[styles.sleepText, sleepQuality === num && styles.activeSleepText]}>{num}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <TouchableOpacity
        onPress={handleSubmit}
        disabled={!mood || !energyMorning || !energyEvening || loading}
        style={[styles.submitButton, (!mood || !energyMorning || !energyEvening) && styles.disabledButton]}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.submitText}>{isHindi ? 'सबमिट करें' : 'Submit Check-in'}</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 24, paddingBottom: 60 },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text, marginBottom: 32 },
  section: { marginBottom: 32 },
  sectionLabel: { color: COLORS.primary, fontSize: 12, fontWeight: '800', textTransform: 'uppercase', letterSpacing: 2, marginBottom: 16 },
  moodGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  moodCard: { 
    width: '30%', 
    aspectRatio: 1, 
    backgroundColor: 'rgba(255,255,255,0.03)', 
    borderRadius: 20, 
    alignItems: 'center', 
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)'
  },
  optionGrid: { flexDirection: 'row', gap: 12 },
  optionCard: { 
    flex: 1, 
    paddingVertical: 12, 
    backgroundColor: 'rgba(255,255,255,0.03)', 
    borderRadius: 12, 
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)'
  },
  activeCard: { 
    backgroundColor: 'rgba(56,189,248,0.1)', 
    borderColor: COLORS.primary,
    borderWidth: 2
  },
  cardLabel: { color: COLORS.textSecondary, fontSize: 11, fontWeight: '700', marginTop: 8 },
  optionText: { color: COLORS.textSecondary, fontSize: 13, fontWeight: '700' },
  activeLabel: { color: COLORS.text },
  sleepGrid: { flexDirection: 'row', gap: 12 },
  sleepNum: { 
    width: 48, 
    height: 48, 
    borderRadius: 24, 
    backgroundColor: 'rgba(255,255,255,0.03)', 
    alignItems: 'center', 
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)'
  },
  activeSleepNum: { backgroundColor: COLORS.primary, borderColor: COLORS.primary },
  sleepText: { color: COLORS.textSecondary, fontWeight: '800' },
  activeSleepText: { color: '#fff' },
  submitButton: { 
    backgroundColor: COLORS.primary, 
    height: 56, 
    borderRadius: 16, 
    alignItems: 'center', 
    justifyContent: 'center', 
    marginTop: 16,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5
  },
  disabledButton: { opacity: 0.5 },
  submitText: { color: '#fff', fontSize: 16, fontWeight: '800' }
});
