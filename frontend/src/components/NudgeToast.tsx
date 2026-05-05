import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { MotiView, AnimatePresence } from 'moti';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS, SHADOWS } from '../theme/theme';
import { Bell, CheckCircle, AlertCircle, Info } from 'lucide-react-native';
import { triggerHaptic } from '../utils/animationManager';
import { useNudgeStore } from '../services/NudgeService';

export default function NudgeToast() {
  const { activeNudge, hideNudge } = useNudgeStore();

  const getIcon = () => {
    switch (activeNudge?.type) {
      case 'success': return <CheckCircle color={COLORS.success} size={18} />;
      case 'error': return <AlertCircle color={COLORS.danger} size={18} />;
      default: return <Bell color={COLORS.primary} size={18} />;
    }
  };

  const getBorderColor = () => {
    switch (activeNudge?.type) {
      case 'success': return COLORS.success;
      case 'error': return COLORS.danger;
      default: return COLORS.primary;
    }
  };

  return (
    <AnimatePresence>
      {activeNudge && (
        <MotiView
          from={{ opacity: 0, translateY: 50, scale: 0.95 }}
          animate={{ opacity: 1, translateY: 0, scale: 1 }}
          exit={{ opacity: 0, translateY: 20, scale: 0.95 }}
          style={styles.container}
        >
          <View style={[styles.card, { borderColor: getBorderColor() }]}>
            <View style={[styles.glow, { backgroundColor: getBorderColor() }]} />
            <View style={styles.contentContainer}>
              <View style={[styles.iconContainer, { backgroundColor: `${getBorderColor()}15` }]}>
                {getIcon()}
              </View>
              
              <View style={styles.textContainer}>
                <Text style={[styles.title, { color: getBorderColor() }]}>
                  {activeNudge.type === 'success' ? 'SYSTEM CONFIRMED' : 
                   activeNudge.type === 'error' ? 'SYSTEM ALERT' : 
                   'BEHAVIORAL NUDGE'}
                </Text>
                <Text style={styles.message}>{activeNudge.message}</Text>
                
                <View style={styles.actions}>
                  {activeNudge.actionLabel && (
                    <TouchableOpacity 
                      onPress={() => {
                        activeNudge.onAction?.();
                        hideNudge();
                      }}
                      style={[styles.primaryButton, { backgroundColor: getBorderColor() }]}
                      activeOpacity={0.8}
                    >
                      <Text style={styles.primaryText}>{activeNudge.actionLabel}</Text>
                    </TouchableOpacity>
                  )}
                  <TouchableOpacity 
                    onPress={hideNudge}
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

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: SPACING[12],
    left: SPACING[5],
    right: SPACING[5],
    zIndex: 1000,
  },
  card: {
    backgroundColor: '#1A1F2E',
    borderRadius: RADIUS.xl,
    overflow: 'hidden',
    borderWidth: 1,
    ...SHADOWS.glowPrimary,
  },
  glow: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 2,
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
    alignItems: 'center',
    justifyContent: 'center',
  },
  textContainer: { flex: 1, gap: SPACING[1] },
  title: { 
    ...TYPOGRAPHY.label, 
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
