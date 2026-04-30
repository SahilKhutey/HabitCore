import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Home, BarChart2, Trophy, ShoppingBag, User as UserIcon } from 'lucide-react-native';
import { COLORS } from '../theme/theme';

import HomeScreen from '../screens/Home/HomeScreen';
import StatsScreen from '../screens/Stats/StatsScreen';
import LeaderboardScreen from '../screens/Stats/LeaderboardScreen';
import ShopScreen from '../screens/Profile/ShopScreen';
import LoginScreen from '../screens/Auth/LoginScreen';
import OnboardingScreen from '../screens/Auth/OnboardingScreen';
import AddHabitScreen from '../screens/Home/AddHabitScreen';
import HabitDetailScreen from '../screens/Home/HabitDetailScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: COLORS.surface,
          borderTopColor: 'rgba(255,255,255,0.05)',
          paddingTop: 5,
        },
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.textSecondary,
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ tabBarIcon: ({ color }) => <Home color={color} size={24} /> }}
      />
      <Tab.Screen 
        name="Stats" 
        component={StatsScreen} 
        options={{ tabBarIcon: ({ color }) => <BarChart2 color={color} size={24} /> }}
      />
      <Tab.Screen 
        name="Rank" 
        component={LeaderboardScreen} 
        options={{ tabBarIcon: ({ color }) => <Trophy color={color} size={24} /> }}
      />
      <Tab.Screen 
        name="Shop" 
        component={ShopScreen} 
        options={{ tabBarIcon: ({ color }) => <ShoppingBag color={color} size={24} /> }}
      />
    </Tab.Navigator>
  );
}

export default function AppNavigator({ isAuthenticated }: { isAuthenticated: boolean }) {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!isAuthenticated ? (
        <>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Onboarding" component={OnboardingScreen} />
        </>
      ) : (
        <>
          <Stack.Screen name="Main" component={TabNavigator} />
          <Stack.Screen 
            name="AddHabit" 
            component={AddHabitScreen} 
            options={{ presentation: 'modal' }}
          />
          <Stack.Screen 
            name="HabitDetail" 
            component={HabitDetailScreen} 
          />
        </>
      )}
    </Stack.Navigator>
  );
}
