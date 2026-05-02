import React, { useState } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity,
  ScrollView, ActivityIndicator, SafeAreaView
} from 'react-native';
import { MotiView } from 'moti';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';
import { api } from '../api/client';
import { useUserStore } from '../store/useUserStore';

const ARCHETYPES = [
  {
    id: 'warrior',
    emoji: '⚔️',
    name: 'Warrior',
    tagline: 'Discipline. Intensity. Results.',
    description: 'You forge yourself through action. Physical excellence, mental toughness, and relentless consistency define who you are.',
    color: '#33ffd6',
    traits: ['Morning workouts', 'Cold exposure', 'Evening review'],
    bg: 'rgba(51, 255, 214, 0.06)',
    border: 'rgba(51, 255, 214, 0.3)',
  },
  {
    id: 'monk',
    emoji: '🧘',
    name: 'Monk',
    tagline: 'Clarity. Calm. Inner power.',
    description: 'You seek stillness in a loud world. Mindfulness, gratitude, and deep reflection are your tools for transformation.',
    color: '#a78bfa',
    traits: ['Daily meditation', 'Gratitude journaling', 'Digital detox'],
    bg: 'rgba(167, 139, 250, 0.06)',
    border: 'rgba(167, 139, 250, 0.3)',
  },
  {
    id: 'builder',
    emoji: '🚀',
    name: 'Builder',
    tagline: 'Create. Learn. Ship.',
    description: 'You measure your day in output. Deep work, learning, and building things that last is your reason for getting up.',
    color: '#38bdf8',
    traits: ['Deep work blocks', 'Daily learning', 'Project reviews'],
    bg: 'rgba(56, 189, 248, 0.06)',
    border: 'rgba(56, 189, 248, 0.3)',
  },
  {
    id: 'explorer',
    emoji: '🌿',
    name: 'Explorer',
    tagline: 'Curiosity. Connection. Growth.',
    description: 'You thrive on variety and human connection. Your growth comes from embracing new experiences and genuine relationships.',
    color: '#f472b6',
    traits: ['Morning walks', 'Reading & exploring', 'Social connections'],
    bg: 'rgba(244, 114, 182, 0.06)',
    border: 'rgba(244, 114, 182, 0.3)',
  },
];

interface Props {
  onComplete: (archetype: string) => void;
}

export default function ArchetypeSelector({ onComplete }: Props) {
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { token, setUserInfo } = useUserStore();

  const handleConfirm = async () => {
    if (!selected || !token) return;
    setLoading(true);
    try {
      const res = await api('/users/set-archetype', 'POST', {
        archetype: selected,
        seed_habits: true,
      }, token);
      setUserInfo({ identityGoal: res.identity_goal });
      onComplete(selected);
    } catch (e) {
      console.error('Archetype set failed:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <MotiView
          from={{ opacity: 0, translateY: -20 }}
          animate={{ opacity: 1, translateY: 0 }}
          transition={{ type: 'spring', duration: 700 }}
        >
          <Text style={styles.headline}>Who are you becoming?</Text>
          <Text style={styles.subline}>
            Choose your identity archetype. This shapes your habit suggestions, AI coaching, and behavioral targets.
          </Text>
        </MotiView>

        <View style={styles.grid}>
          {ARCHETYPES.map((arch, i) => {
            const isSelected = selected === arch.id;
            return (
              <MotiView
                key={arch.id}
                from={{ opacity: 0, translateY: 30 }}
                animate={{ opacity: 1, translateY: 0 }}
                transition={{ type: 'spring', delay: i * 100 }}
              >
                <TouchableOpacity
                  style={[
                    styles.card,
                    { backgroundColor: arch.bg, borderColor: isSelected ? arch.color : arch.border },
                    isSelected && styles.cardSelected,
                  ]}
                  onPress={() => setSelected(arch.id)}
                  activeOpacity={0.85}
                >
                  <View style={styles.cardTop}>
                    <Text style={styles.cardEmoji}>{arch.emoji}</Text>
                    {isSelected && (
                      <View style={[styles.checkBadge, { backgroundColor: arch.color }]}>
                        <Text style={styles.checkText}>✓</Text>
                      </View>
                    )}
                  </View>
                  <Text style={[styles.cardName, { color: arch.color }]}>{arch.name}</Text>
                  <Text style={styles.cardTagline}>{arch.tagline}</Text>
                  <Text style={styles.cardDesc}>{arch.description}</Text>

                  <View style={styles.traitRow}>
                    {arch.traits.map((t, ti) => (
                      <View key={ti} style={[styles.trait, { borderColor: `${arch.color}40` }]}>
                        <Text style={[styles.traitText, { color: arch.color }]}>{t}</Text>
                      </View>
                    ))}
                  </View>
                </TouchableOpacity>
              </MotiView>
            );
          })}
        </View>

        <TouchableOpacity
          style={[styles.confirmBtn, !selected && styles.confirmBtnDisabled]}
          onPress={handleConfirm}
          disabled={!selected || loading}
        >
          {loading ? (
            <ActivityIndicator color="#000" />
          ) : (
            <Text style={styles.confirmText}>
              {selected
                ? `Begin as ${ARCHETYPES.find(a => a.id === selected)?.name} →`
                : 'Select an archetype to continue'}
            </Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { padding: SPACING.margin, paddingBottom: 60 },
  headline: {
    ...TYPOGRAPHY.h1,
    color: COLORS.text,
    marginBottom: 12,
    textAlign: 'center',
  },
  subline: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
    fontSize: 14,
    lineHeight: 22,
    textAlign: 'center',
    marginBottom: SPACING.xl,
  },
  grid: { gap: 16 },
  card: {
    borderRadius: 20,
    borderWidth: 1.5,
    padding: SPACING.lg,
    marginBottom: 4,
  },
  cardSelected: {
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.25,
    shadowRadius: 16,
    elevation: 8,
  },
  cardTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardEmoji: { fontSize: 36 },
  checkBadge: {
    width: 28, height: 28, borderRadius: 14,
    alignItems: 'center', justifyContent: 'center',
  },
  checkText: { color: '#000', fontWeight: '900', fontSize: 14 },
  cardName: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 22,
    marginBottom: 2,
  },
  cardTagline: {
    fontFamily: 'SpaceGrotesk_500Medium',
    fontSize: 12,
    color: COLORS.textDim,
    letterSpacing: 1,
    marginBottom: 10,
    textTransform: 'uppercase',
  },
  cardDesc: {
    ...TYPOGRAPHY.body,
    fontSize: 14,
    color: COLORS.textSecondary,
    lineHeight: 21,
    marginBottom: 14,
  },
  traitRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  trait: {
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  traitText: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 11 },
  confirmBtn: {
    marginTop: SPACING.xl,
    backgroundColor: COLORS.primary,
    height: 56,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
  },
  confirmBtnDisabled: {
    backgroundColor: 'rgba(255,255,255,0.08)',
    shadowOpacity: 0,
    elevation: 0,
  },
  confirmText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 16,
    color: '#000',
  },
});
