import React from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, ScrollView } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';
import { GlassCard } from './GlassCard';
import { Sparkles, Brain, ArrowRight } from 'lucide-react-native';
import { MotiView, AnimatePresence } from 'moti';

interface AhaMomentModalProps {
  visible: boolean;
  insight: string;
  onClose: () => void;
}

export const AhaMomentModal = ({ visible, insight, onClose }: AhaMomentModalProps) => {
  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.overlay}>
        <MotiView
          from={{ opacity: 0, scale: 0.9, translateY: 20 }}
          animate={{ opacity: 1, scale: 1, translateY: 0 }}
          transition={{ type: 'spring', damping: 15 }}
          style={styles.container}
        >
          <GlassCard variant="ai" style={styles.card}>
            <View style={styles.header}>
              <View style={styles.iconCircle}>
                <Sparkles size={24} color={COLORS.secondary} />
              </View>
              <Text style={styles.headerTitle}>THE AHA MOMENT</Text>
            </View>

            <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
              <Text style={styles.insightText}>{insight}</Text>
              
              <View style={styles.divider} />
              
              <View style={styles.footer}>
                <Brain size={16} color={COLORS.primary} />
                <Text style={styles.footerText}>
                  This pattern was identified by analyzing your first reflection against your psychological archetype.
                </Text>
              </View>
            </ScrollView>

            <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
              <Text style={styles.closeBtnText}>I see the pattern</Text>
              <ArrowRight size={16} color="#fff" />
            </TouchableOpacity>
          </GlassCard>
        </MotiView>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.85)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  container: {
    width: '100%',
    maxWidth: 400,
  },
  card: {
    padding: 24,
    borderRadius: 32,
    borderWidth: 1,
    borderColor: 'rgba(167, 139, 250, 0.4)',
  },
  header: {
    alignItems: 'center',
    marginBottom: 20,
  },
  iconCircle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(167, 139, 250, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  headerTitle: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 12,
    color: COLORS.secondary,
    letterSpacing: 3,
  },
  scroll: {
    maxHeight: 300,
  },
  insightText: {
    fontFamily: 'SpaceGrotesk_600SemiBold',
    fontSize: 20,
    color: COLORS.text,
    lineHeight: 28,
    textAlign: 'center',
  },
  divider: {
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginVertical: 20,
  },
  footer: {
    flexDirection: 'row',
    gap: 12,
    paddingHorizontal: 8,
  },
  footerText: {
    fontFamily: 'SpaceGrotesk_400Regular',
    fontSize: 12,
    color: COLORS.textSecondary,
    flex: 1,
    lineHeight: 18,
  },
  closeBtn: {
    backgroundColor: COLORS.secondary,
    height: 56,
    borderRadius: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    marginTop: 24,
    shadowColor: COLORS.secondary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  closeBtnText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 16,
    color: '#fff',
  },
});
