import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { login } from '../../api/client';
import { useUserStore } from '../../store/useUserStore';
import { COLORS, SPACING, TYPOGRAPHY } from '../../theme/theme';
import { GlassCard } from '../../components/GlassCard';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const setToken = useUserStore((s) => s.setToken);

  const handleLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await login(email, password);
      setToken(res.access_token);
    } catch (err: any) {
      setError(err.message || 'Login failed');
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
            onPress={handleLogin}
            disabled={loading}
          >
            <Text style={styles.buttonText}>{loading ? 'Loading...' : 'Login'}</Text>
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
    color: COLORS.error,
    marginBottom: SPACING.sm,
    textAlign: 'center',
  },
});
