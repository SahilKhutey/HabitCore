import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TextInput, 
  TouchableOpacity, 
  SafeAreaView,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Dimensions
} from 'react-native';
import { useRouter } from 'expo-router';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from '../src/theme/theme';
import { api } from '../src/api/client';
import { useUserStore } from '../src/store/useUserStore';
import { triggerHaptic } from '../src/utils/animationManager';
import { MotiView } from 'moti';
import { ChevronLeft, ArrowRight } from 'lucide-react-native';

const { height } = Dimensions.get('window');

export default function ReflectionScreen() {
  const router = useRouter();
  const [reflection, setReflection] = useState('');
  const [loading, setLoading] = useState(false);
  const { token } = useUserStore();

  const handleSubmit = async () => {
    if (!reflection.trim()) return;
    
    try {
      setLoading(true);
      triggerHaptic('impactMedium');
      
      const response = await api('/psychological/checkin', 'POST', {
        mood: 'neutral',
        energy_morning: 'medium',
        energy_evening: 'medium',
        sleep_quality: 3,
        reflection: reflection.trim()
      }, token!);
      
      triggerHaptic('success');
      router.replace({
        pathname: '/insight' as any,
        params: { insight: response.insights?.insights?.[0] || response.message }
      });
    } catch (error) {
      triggerHaptic('error');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <View style={styles.header}>
          <TouchableOpacity 
            onPress={() => router.back()}
            style={styles.backButton}
          >
            <ChevronLeft color={COLORS.textSecondary} size={24} />
          </TouchableOpacity>
          <Text style={styles.headerLabel}>Self Reflection</Text>
          <View style={{ width: 44 }} />
        </View>

        <MotiView 
          from={{ opacity: 0, translateY: 20 }}
          animate={{ opacity: 1, translateY: 0 }}
          style={styles.content}
        >
          <View style={styles.questionContainer}>
            <Text style={styles.question}>What is drawing your attention today?</Text>
            <Text style={styles.subtitle}>Be honest with yourself. There is no right answer.</Text>
          </View>
          
          <TextInput
            style={styles.input}
            placeholder="I feel like I'm avoiding..."
            placeholderTextColor={COLORS.textDim}
            multiline
            autoFocus
            value={reflection}
            onChangeText={setReflection}
            selectionColor={COLORS.primary}
          />

          <View style={styles.footer}>
            <View style={styles.hintContainer}>
              <Text style={styles.hint}>Your reflections are private and encrypted.</Text>
            </View>
            
            <TouchableOpacity 
              onPress={handleSubmit}
              disabled={!reflection.trim() || loading}
              style={[
                styles.submitButton, 
                (!reflection.trim() || loading) && styles.disabledButton
              ]}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <View style={styles.buttonInner}>
                  <Text style={styles.submitText}>Submit Reflection</Text>
                  <ArrowRight color="#fff" size={20} />
                </View>
              )}
            </TouchableOpacity>
          </View>
        </MotiView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  header: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-between', 
    paddingHorizontal: SPACING[4],
    paddingTop: SPACING[4]
  },
  backButton: {
    width: 44,
    height: 44,
    borderRadius: RADIUS.md,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.surface
  },
  headerLabel: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 10, letterSpacing: 2 },
  content: { flex: 1, padding: SPACING[6], paddingTop: SPACING[8] },
  questionContainer: { marginBottom: SPACING[8] },
  question: { ...TYPOGRAPHY.h2, color: COLORS.text, marginBottom: SPACING[2], lineHeight: 34 },
  subtitle: { ...TYPOGRAPHY.body, color: COLORS.textDim, fontSize: 15 },
  input: { 
    flex: 1, 
    ...TYPOGRAPHY.bodyLg, 
    color: COLORS.text, 
    textAlignVertical: 'top',
    paddingTop: 0,
    fontSize: 20
  },
  footer: { paddingBottom: SPACING[8], gap: SPACING[6] },
  hintContainer: {
    padding: SPACING[4],
    backgroundColor: 'rgba(255,255,255,0.02)',
    borderRadius: RADIUS.md,
    alignItems: 'center'
  },
  hint: { ...TYPOGRAPHY.caption, color: COLORS.textDim, fontSize: 11 },
  submitButton: { 
    backgroundColor: COLORS.primary, 
    height: 64, 
    borderRadius: RADIUS.xl, 
    alignItems: 'center', 
    justifyContent: 'center',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 15,
    elevation: 8
  },
  buttonInner: { flexDirection: 'row', alignItems: 'center', gap: SPACING[3] },
  disabledButton: { opacity: 0.4 },
  submitText: { ...TYPOGRAPHY.h3, color: '#fff', fontSize: 16 },
});
