import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { login } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import { COLORS, SPACING, TYPOGRAPHY } from '../../src/theme/theme';
import { GlassCard } from '../../src/components/GlassCard';
import { router } from 'expo-router';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { setToken, setUserInfo } = useUserStore();

  const handleLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await login(email, password);
      setToken(res.access_token);
      setUserInfo({ email: res.email });
      router.replace('/(tabs)');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await login('sim_v2_0@simulator.com', 'sim_password_123');
      setToken(res.access_token);
      setUserInfo({ email: res.email });
      router.replace('/(tabs)');
    } catch (err: any) {
      setError('Demo login failed');
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
        <Text style={[TYPOGRAPHY.caption, styles.subtitle]}>Become the hero of your own life.</Text>
        
        <GlassCard style={styles.card}>
          <TextInput 
            placeholder="Email" 
            placeholderTextColor={COLORS.textDim}
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
          />
          <TextInput 
            placeholder="Password" 
            placeholderTextColor={COLORS.textDim}
            secureTextEntry 
            style={styles.input}
            value={password}
            onChangeText={setPassword}
          />
          
          {error && <Text style={styles.errorText}>{error}</Text>}
          
          <TouchableOpacity 
            style={styles.button} 
            onPress={handleLogin}
            disabled={loading}
          >
            <Text style={styles.buttonText}>{loading ? 'Loading...' : 'Login'}</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.demoButton} 
            onPress={handleDemoLogin}
            disabled={loading}
          >
            <Text style={styles.demoButtonText}>Demo Experience</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.linkButton} 
            onPress={() => router.push('/auth/register' as any)}
            disabled={loading}
          >
            <Text style={styles.linkText}>Don't have an account? Register</Text>
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
    backgroundColor: COLORS.surface,
  },
  input: {
    height: 50,
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
    paddingHorizontal: SPACING.md,
    color: COLORS.text,
    marginBottom: SPACING.md,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  button: {
    backgroundColor: COLORS.primary,
    height: 50,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: SPACING.sm,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '700',
  },
  demoButton: {
    height: 50,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: SPACING.md,
    borderWidth: 1.5,
    borderColor: COLORS.primary,
  },
  demoButtonText: {
    color: COLORS.primary,
    fontSize: 16,
    fontWeight: '700',
  },
  errorText: {
    color: COLORS.danger,
    marginBottom: SPACING.sm,
    textAlign: 'center',
    fontWeight: '600',
  },
  linkButton: {
    marginTop: SPACING.xl,
    alignItems: 'center',
  },
  linkText: {
    color: COLORS.textSecondary,
    fontSize: 14,
    fontWeight: '500',
  },
});
