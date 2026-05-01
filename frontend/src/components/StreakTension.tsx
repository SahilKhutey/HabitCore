import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';
import { GlassCard } from './GlassCard';
import { Clock, AlertTriangle } from 'lucide-react-native';

interface StreakTensionProps {
  currentStreak: number;
  lastActivity: string;
  isHindi?: boolean;
}

export default function StreakTension({ currentStreak, lastActivity, isHindi = false }: StreakTensionProps) {
  const [timeLeft, setTimeLeft] = useState('');
  const [showTension, setShowTension] = useState(false);

  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date();
      const lastActive = new Date(lastActivity);
      const nextDeadline = new Date(lastActive);
      nextDeadline.setDate(nextDeadline.getDate() + 1);
      
      const timeDiff = nextDeadline.getTime() - now.getTime();
      const hoursLeft = Math.floor(timeDiff / (1000 * 60 * 60));
      const minutesLeft = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
      
      if (hoursLeft <= 4 && hoursLeft >= 0) {
        setShowTension(true);
        setTimeLeft(`${hoursLeft}h ${minutesLeft}m`);
      } else {
        setShowTension(false);
      }
    };

    calculateTimeLeft();
    const interval = setInterval(calculateTimeLeft, 60000);

    return () => clearInterval(interval);
  }, [lastActivity]);

  if (!showTension) return null;

  const tensionMessage = isHindi
    ? `⚠️ केवल ${timeLeft} बचा है आपकी ${currentStreak}-दिन की स्ट्रीक बचाने के लिए!`
    : `⚠️ Only ${timeLeft} left to save your ${currentStreak}-day streak!`;

  return (
    <GlassCard style={styles.container}>
      <View style={styles.header}>
        <Clock color="#eab308" size={20} />
        <Text style={styles.message}>{tensionMessage}</Text>
      </View>
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: 'rgba(234, 179, 8, 0.1)', borderColor: '#eab308' },
  header: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  message: { ...TYPOGRAPHY.body, color: '#eab308', fontWeight: '700' }
});
