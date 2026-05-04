import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { register, login, api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { COLORS, SPACING, TYPOGRAPHY } from '../../src/theme/theme';
import { GlassCard } from '../../src/components/GlassCard';
import { router } from 'expo-router';

export default function RegisterScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { setToken, identityGoal, mode } = useUserStore();

  const handleRegister = async () => {
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // 1. Register user
      await register(email, password);
      
      // 2. Login to get token
      const authRes = await login(email, password);
      const token = authRes.access_token;
      setToken(token);
      
      // 3. Apply onboarding data if exists
      if (mode) {
        try {
          await api('/users/set-archetype', 'POST', { 
            archetype: mode, 
            seed_habits: true 
          }, token);
        } catch (archetypeErr) {
          console.error('Failed to set archetype during registration:', archetypeErr);
          // Non-fatal, continue to dashboard
        }
      }
      
      router.replace('/(tabs)');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.content}>
        <Text style={[TYPOGRAPHY.h1, styles.title]}>HabitHero</Text>
        <Text style={[TYPOGRAPHY.caption, styles.subtitle]}>Create your account to start your journey.</Text>
        
        <GlassCard style={styles.card}>
          <TextInput 
            placeholder="Email" 
            placeholderTextColor={COLORS.textSecondary}
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
          />
          <TextInput 
            placeholder="Password" 
            placeholderTextColor={COLORS.textSecondary}
            secureTextEntry 
            style={styles.input}
            value={password}
            onChangeText={setPassword}
          />
          
          {error && <Text style={styles.errorText}>{error}</Text>}
          
          <TouchableOpacity 
            style={styles.button} 
            onPress={handleRegister}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <Text style={styles.buttonText}>Register</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.linkButton} 
            onPress={() => router.push('/auth/login')}
            disabled={loading}
          >
            <Text style={styles.linkText}>Already have an account? Login</Text>
          </TouchableOpacity>
        </GlassCard>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    padding: SPACING.lg,
  },
  content: {
    width: '100%',
  },
  title: {
    textAlign: 'center',
    fontSize: 40,
    color: COLORS.primary,
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: SPACING.xl,
    color: COLORS.textSecondary,
  },
  card: {
    width: '100%',
  },
  input: {
    height: 50,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 10,
    paddingHorizontal: SPACING.md,
    color: COLORS.text,
    marginBottom: SPACING.md,
  },
  button: {
    backgroundColor: COLORS.primary,
    height: 50,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: SPACING.sm,
  },
  buttonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '600',
  },
  errorText: {
    color: COLORS.danger,
    marginBottom: SPACING.sm,
    textAlign: 'center',
  },
  linkButton: {
    marginTop: SPACING.lg,
    alignItems: 'center',
  },
  linkText: {
    color: COLORS.primary,
    fontSize: 14,
  },
});
