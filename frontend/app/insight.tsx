import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  SafeAreaView,
  Dimensions
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from '../src/theme/theme';
import { triggerHaptic } from '../src/utils/animationManager';
import { MotiView } from 'moti';
import { Brain, CheckCircle2, MessageCircle } from 'lucide-react-native';

const { width } = Dimensions.get('window');

export default function InsightScreen() {
  const router = useRouter();
  const { insight } = useLocalSearchParams<{ insight: string }>();

  const handleFeedback = (isAccurate: boolean) => {
    triggerHaptic(isAccurate ? 'success' : 'impactLight');
    router.replace('/(tabs)');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <MotiView 
        from={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        style={styles.container}
      >
        <View style={styles.content}>
          <MotiView 
            from={{ scale: 0.8, opacity: 0, rotate: '-10deg' }}
            animate={{ scale: 1, opacity: 1, rotate: '0deg' }}
            transition={{ type: 'spring', delay: 300 }}
            style={styles.iconContainer}
          >
            <Brain color={COLORS.primary} size={40} />
            <View style={styles.iconGlow} />
          </MotiView>

          <View style={styles.textContainer}>
            <Text style={styles.label}>AI Observation</Text>
            <Text style={styles.insightMain}>
              {insight || "You act faster at night than in the morning. This might be due to lower cognitive pressure in the PM."}
            </Text>
            <Text style={styles.insightSub}>
              Based on your last 3 reflections and behavior patterns.
            </Text>
          </View>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerLabel}>How does this land with you?</Text>
          
          <TouchableOpacity 
            onPress={() => handleFeedback(true)}
            style={styles.primaryButton}
            activeOpacity={0.9}
          >
            <CheckCircle2 color="#fff" size={20} />
            <Text style={styles.primaryText}>This feels accurate</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            onPress={() => handleFeedback(false)}
            style={styles.secondaryButton}
            activeOpacity={0.7}
          >
            <MessageCircle color={COLORS.textDim} size={20} />
            <Text style={styles.secondaryText}>I'm not sure yet</Text>
          </TouchableOpacity>
        </View>
      </MotiView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1, padding: SPACING[6] },
  content: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: SPACING[10] },
  iconContainer: { 
    width: 80, 
    height: 80, 
    borderRadius: RADIUS.full, 
    backgroundColor: COLORS.surface, 
    alignItems: 'center', 
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(124, 140, 255, 0.2)'
  },
  iconGlow: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    borderRadius: RADIUS.full,
    backgroundColor: COLORS.primary,
    opacity: 0.1,
    transform: [{ scale: 1.5 }]
  },
  textContainer: { alignItems: 'center', gap: SPACING[3] },
  label: { ...TYPOGRAPHY.label, color: COLORS.primary, fontSize: 10, letterSpacing: 2 },
  insightMain: { 
    ...TYPOGRAPHY.h1, 
    color: COLORS.text, 
    textAlign: 'center', 
    lineHeight: 44,
    fontSize: 28
  },
  insightSub: { 
    ...TYPOGRAPHY.body, 
    color: COLORS.textDim, 
    textAlign: 'center',
    fontSize: 14,
    paddingHorizontal: SPACING[4]
  },
  footer: { gap: SPACING[4], paddingBottom: SPACING[10] },
  footerLabel: { 
    ...TYPOGRAPHY.caption, 
    color: COLORS.textDim, 
    textAlign: 'center', 
    marginBottom: SPACING[2] 
  },
  primaryButton: { 
    backgroundColor: COLORS.primary, 
    height: 64, 
    borderRadius: RADIUS.xl, 
    flexDirection: 'row',
    alignItems: 'center', 
    justifyContent: 'center',
    gap: SPACING[3],
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 15,
    elevation: 8
  },
  primaryText: { ...TYPOGRAPHY.h3, color: '#fff', fontSize: 16 },
  secondaryButton: { 
    height: 64, 
    borderRadius: RADIUS.xl, 
    flexDirection: 'row',
    alignItems: 'center', 
    justifyContent: 'center',
    gap: SPACING[3],
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface
  },
  secondaryText: { ...TYPOGRAPHY.h3, color: COLORS.textSecondary, fontSize: 16 },
});
