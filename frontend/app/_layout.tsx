import React, { useEffect } from 'react';
import { DarkTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'expo-status-bar';
import { 
  useFonts, 
  SpaceGrotesk_400Regular, 
  SpaceGrotesk_500Medium, 
  SpaceGrotesk_600SemiBold, 
  SpaceGrotesk_700Bold 
} from '@expo-google-fonts/space-grotesk';
import { 
  Inter_400Regular, 
  Inter_500Medium, 
  Inter_600SemiBold 
} from '@expo-google-fonts/inter';
import 'react-native-reanimated';
import NudgeToast from '../src/components/NudgeToast';

import { useUserStore } from '../src/store/useUserStore';
import { useRouter, useSegments } from 'expo-router';
import { realtimeService } from '../src/services/RealtimeService';

// Prevent the splash screen from auto-hiding
SplashScreen.preventAutoHideAsync();

const queryClient = new QueryClient();

export default function RootLayout() {
  const { token } = useUserStore();
  const segments = useSegments();
  const router = useRouter();

  const [fontsLoaded, fontError] = useFonts({
    SpaceGrotesk_400Regular,
    SpaceGrotesk_500Medium,
    SpaceGrotesk_600SemiBold,
    SpaceGrotesk_700Bold,
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
  });

  useEffect(() => {
    if (fontError) throw fontError;
  }, [fontError]);

  useEffect(() => {
    if (fontsLoaded) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded]);

  // Auth Redirection & Real-time Connectivity
  useEffect(() => {
    if (!fontsLoaded) return;

    const inAuthGroup = segments[0] === 'auth';
    const inOnboarding = segments[0] === 'onboarding';

    if (!token && !inAuthGroup && !inOnboarding) {
      router.replace('/auth/login');
      realtimeService.stop();
    } else if (token && (inAuthGroup || inOnboarding)) {
      router.replace('/(tabs)');
      realtimeService.start(token);
    } else if (token) {
      realtimeService.start(token);
    }
  }, [token, segments, fontsLoaded]);

  if (!fontsLoaded) {
    return null;
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider value={DarkTheme}>
          <StatusBar style="light" />
          <Stack screenOptions={{ headerShown: false }}>
            <Stack.Screen name="onboarding" />
            <Stack.Screen name="auth/login" />
            <Stack.Screen name="(tabs)" />
            <Stack.Screen name="reflection" options={{ presentation: 'fullScreenModal' }} />
            <Stack.Screen name="insight" options={{ presentation: 'transparentModal', animation: 'fade' }} />
            <Stack.Screen name="modal" options={{ presentation: 'modal', headerShown: true }} />
          </Stack>
          <NudgeToast />
        </ThemeProvider>
      </QueryClientProvider>
    </GestureHandlerRootView>
  );
}
