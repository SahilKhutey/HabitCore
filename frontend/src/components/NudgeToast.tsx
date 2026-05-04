import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Dimensions } from 'react-native';
import { MotiView, AnimatePresence } from 'moti';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS, SHADOWS } from '../theme/theme';
import { Bell } from 'lucide-react-native';
import { triggerHaptic } from '../utils/animationManager';

interface Nudge {
  id: string;
  message: string;
  type: 'action' | 'reminder';
}

export default function NudgeToast() {
  const [nudge, setNudge] = useState<Nudge | null>(null);

  // Simulation: Show a nudge after 10 seconds for demonstration
  useEffect(() => {
    const timer = setTimeout(() => {
      setNudge({
        id: '1',
        message: 'You usually stop around now.\nStay for 2 more minutes.',
        type: 'action'
      });
      triggerHaptic('notification');
    }, 10000);
    
    return () => clearTimeout(timer);
  }, []);

  if (!nudge) return null;

  return (
    <AnimatePresence>
      {nudge && (
        <MotiView
          from={{ opacity: 0, translateY: 50, scale: 0.95 }}
          animate={{ opacity: 1, translateY: 0, scale: 1 }}
          exit={{ opacity: 0, translateY: 20, scale: 0.95 }}
          style={styles.container}
        >
          <View style={styles.card}>
            <View style={styles.glow} />
            <View style={styles.contentContainer}>
              <View style={styles.iconContainer}>
                <Bell color={COLORS.primary} size={18} />
              </View>
              
              <View style={styles.textContainer}>
                <Text style={styles.title}>Behavioral Nudge</Text>
                <Text style={styles.message}>{nudge.message}</Text>
                
                <View style={styles.actions}>
                  <TouchableOpacity 
                    onPress={() => setNudge(null)}
                    style={styles.primaryButton}
                    activeOpacity={0.8}
                  >
                    <Text style={styles.primaryText}>Continue</Text>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    onPress={() => setNudge(null)}
                    style={styles.secondaryButton}
                    activeOpacity={0.7}
                  >
                    <Text style={styles.secondaryText}>Dismiss</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          </View>
        </MotiView>
      )}
    </AnimatePresence>
  );
}

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: SPACING[12],
    left: SPACING[5],
    right: SPACING[5],
    zIndex: 1000,
  },
  card: {
    backgroundColor: '#1A1F2E', // Specific nudge background
    borderRadius: RADIUS.xl,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: COLORS.primary, // Specific nudge border
    ...SHADOWS.glowPrimary, // Specific nudge glow
  },
  glow: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 2,
    backgroundColor: COLORS.primary,
    opacity: 0.5,
  },
  contentContainer: {
    padding: SPACING[5],
    flexDirection: 'row',
    gap: SPACING[4],
  },
  iconContainer: {
    width: 36,
    height: 36,
    borderRadius: RADIUS.md,
    backgroundColor: 'rgba(124, 140, 255, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  textContainer: { flex: 1, gap: SPACING[1] },
  title: { 
    ...TYPOGRAPHY.label, 
    color: COLORS.primary, 
    fontSize: 10, 
    letterSpacing: 1.5 
  },
  message: { 
    ...TYPOGRAPHY.body, 
    color: COLORS.text, 
    fontSize: 15, 
    lineHeight: 22 
  },
  actions: { 
    flexDirection: 'row', 
    gap: SPACING[3], 
    marginTop: SPACING[4] 
  },
  primaryButton: { 
    backgroundColor: COLORS.primary, 
    paddingHorizontal: SPACING[5], 
    paddingVertical: SPACING[2], 
    borderRadius: RADIUS.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryText: { 
    ...TYPOGRAPHY.label, 
    color: '#fff', 
    fontSize: 12,
    textTransform: 'none'
  },
  secondaryButton: { 
    paddingHorizontal: SPACING[5], 
    paddingVertical: SPACING[2], 
    borderRadius: RADIUS.lg,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryText: { 
    ...TYPOGRAPHY.label, 
    color: COLORS.textSecondary, 
    fontSize: 12,
    textTransform: 'none'
  },
});
