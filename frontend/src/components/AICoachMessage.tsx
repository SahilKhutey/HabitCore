import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';
import { GlassCard } from './GlassCard';
import { Bot } from 'lucide-react-native';
import { useUserStore } from '../store/useUserStore';
import { api } from '../api/client';

interface AICoachMessageProps {
  currentStreak: number;
  recentFailures: number;
  isHindi?: boolean;
}

export default function AICoachMessage({ currentStreak, recentFailures, isHindi = false }: AICoachMessageProps) {
  const [advice, setAdvice] = useState('');
  const [loading, setLoading] = useState(true);
  const { token } = useUserStore();

  const fetchAdvice = async () => {
    setLoading(true);
    try {
      const response = await api("/psychological/ai-coach/advice", "POST", {
        current_streak: currentStreak,
        recent_failures: recentFailures
      }, token!);
      setAdvice(response.advice);
    } catch (error) {
      setAdvice(isHindi 
        ? 'छोटे, सुसंगत कदमों पर ध्यान दें। दृढ़ता सिद्धि से बेहतर है।'
        : 'Focus on small, consistent steps. Persistence beats perfection.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchAdvice();
    }
  }, [currentStreak, recentFailures]);

  return (
    <GlassCard style={styles.container}>
      <View style={styles.header}>
        <View style={styles.iconContainer}>
          <Bot color={COLORS.primary} size={20} />
        </View>
        <Text style={styles.title}>
          {isHindi ? 'AI कोच सलाह' : 'AI Coach Advice'}
        </Text>
      </View>
      
      {loading ? (
        <ActivityIndicator color={COLORS.primary} style={styles.loader} />
      ) : (
        <Text style={styles.adviceText}>{advice}</Text>
      )}
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, borderLeftWidth: 4, borderLeftColor: COLORS.primary },
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  iconContainer: { 
    width: 32, 
    height: 32, 
    borderRadius: 16, 
    backgroundColor: 'rgba(56,189,248,0.1)', 
    alignItems: 'center', 
    justifyContent: 'center',
    marginRight: 10
  },
  title: { ...TYPOGRAPHY.body, fontWeight: '800', color: COLORS.text },
  adviceText: { ...TYPOGRAPHY.body, color: COLORS.textSecondary, lineHeight: 20 },
  loader: { padding: 10 }
});
