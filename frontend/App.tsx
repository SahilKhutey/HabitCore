import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppNavigator from './src/navigation/AppNavigator';
import { useUserStore } from './src/store/useUserStore';
import { StatusBar } from 'expo-status-bar';

const queryClient = new QueryClient();

export default function App() {
  const token = useUserStore((s) => s.token);
  const isAuthenticated = !!token;

  return (
    <QueryClientProvider client={queryClient}>
      <NavigationContainer>
        <AppNavigator isAuthenticated={isAuthenticated} />
        <StatusBar style="light" />
      </NavigationContainer>
    </QueryClientProvider>
  );
}
