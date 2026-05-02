import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  Modal, 
  TextInput, 
  TouchableOpacity, 
  KeyboardAvoidingView, 
  Platform 
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';
import { GlassCard } from './GlassCard';
import { X, Zap, Clock, Star } from 'lucide-react-native';
import { MotiView, AnimatePresence } from 'moti';

interface AddHabitModalProps {
  visible: boolean;
  onClose: () => void;
  onAdd: (habit: { name: string; time: string; difficulty: string }) => Promise<void>;
}

export const AddHabitModal = ({ visible, onClose, onAdd }: AddHabitModalProps) => {
  const [name, setName] = useState('');
  const [time, setTime] = useState('09:00');
  const [difficulty, setDifficulty] = useState('medium');
  const [loading, setLoading] = useState(false);

  const handleAdd = async () => {
    if (!name.trim()) return;
    setLoading(true);
    await onAdd({ name, time, difficulty });
    setLoading(false);
    setName('');
    onClose();
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          <GlassCard style={styles.modalContent}>
            <View style={styles.header}>
              <Text style={styles.title}>NEW RITUAL</Text>
              <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
                <X color={COLORS.textDim} size={20} />
              </TouchableOpacity>
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.label}>HABIT NAME</Text>
              <TextInput
                style={styles.input}
                placeholder="e.g. Deep Work"
                placeholderTextColor={COLORS.textDim}
                value={name}
                onChangeText={setName}
                autoFocus
              />
            </View>

            <View style={styles.row}>
              <View style={[styles.inputContainer, { flex: 1, marginRight: 8 }]}>
                <Text style={styles.label}>TIME</Text>
                <View style={styles.iconInput}>
                  <Clock size={14} color={COLORS.primary} style={{ marginRight: 8 }} />
                  <TextInput
                    style={[styles.input, { marginTop: 0, height: 40 }]}
                    value={time}
                    onChangeText={setTime}
                    placeholder="09:00"
                  />
                </View>
              </View>

              <View style={[styles.inputContainer, { flex: 1, marginLeft: 8 }]}>
                <Text style={styles.label}>DIFFICULTY</Text>
                <View style={styles.difficultyContainer}>
                  {['easy', 'medium', 'hard'].map((d) => (
                    <TouchableOpacity
                      key={d}
                      onPress={() => setDifficulty(d)}
                      style={[
                        styles.diffOption,
                        difficulty === d && styles.diffOptionActive
                      ]}
                    >
                      <Text style={[
                        styles.diffText,
                        difficulty === d && styles.diffTextActive
                      ]}>
                        {d[0].toUpperCase()}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            </View>

            <TouchableOpacity 
              style={[styles.submitBtn, !name.trim() && styles.submitBtnDisabled]} 
              onPress={handleAdd}
              disabled={loading || !name.trim()}
            >
              <Text style={styles.submitBtnText}>
                {loading ? 'INITIALIZING...' : 'ACTIVATE RITUAL'}
              </Text>
              <Zap size={16} color="#000" fill="#000" />
            </TouchableOpacity>
          </GlassCard>
        </KeyboardAvoidingView>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    padding: SPACING.lg,
  },
  keyboardView: {
    width: '100%',
  },
  modalContent: {
    width: '100%',
    padding: SPACING.xl,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.xl,
  },
  title: {
    ...TYPOGRAPHY.label,
    color: COLORS.primary,
    letterSpacing: 2,
  },
  closeBtn: {
    padding: 4,
  },
  inputContainer: {
    marginBottom: SPACING.lg,
  },
  label: {
    ...TYPOGRAPHY.label,
    color: COLORS.textDim,
    fontSize: 10,
    marginBottom: 8,
  },
  input: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    padding: 12,
    color: COLORS.text,
    fontSize: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  iconInput: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  row: {
    flexDirection: 'row',
    marginBottom: SPACING.xl,
  },
  difficultyContainer: {
    flexDirection: 'row',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    padding: 4,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    height: 40,
  },
  diffOption: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 8,
  },
  diffOptionActive: {
    backgroundColor: COLORS.primary,
  },
  diffText: {
    color: COLORS.textDim,
    fontSize: 12,
    fontWeight: '700',
  },
  diffTextActive: {
    color: '#000',
  },
  submitBtn: {
    backgroundColor: COLORS.primary,
    height: 56,
    borderRadius: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
  },
  submitBtnDisabled: {
    opacity: 0.5,
  },
  submitBtnText: {
    color: '#000',
    fontSize: 14,
    fontFamily: 'SpaceGrotesk_700Bold',
    marginRight: 8,
  },
});
