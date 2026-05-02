import React from 'react';
import { Tabs } from 'expo-router';
import { Zap, Heart, Brain, Sparkles, User } from 'lucide-react-native';
import { COLORS } from '../../src/theme/theme';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.textDim,
        tabBarStyle: {
          backgroundColor: COLORS.background,
          borderTopColor: 'rgba(255, 255, 255, 0.05)',
          height: 70,
          paddingBottom: 15,
          paddingTop: 10,
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          elevation: 0,
          borderTopWidth: 1,
        },
        tabBarLabelStyle: {
          fontSize: 10,
          fontFamily: 'SpaceGrotesk_500Medium',
        },
      }}>

      {/* Tab 1: Today — Habit completion loop */}
      <Tabs.Screen
        name="index"
        options={{
          title: 'Today',
          tabBarIcon: ({ color, focused }) => (
            <Zap size={24} color={color} fill={focused ? color : 'transparent'} />
          ),
        }}
      />

      {/* Tab 2: Life — Life domains, mood check-in, wellbeing */}
      <Tabs.Screen
        name="wellness"
        options={{
          title: 'Life',
          tabBarIcon: ({ color }) => <Heart size={24} color={color} />,
        }}
      />

      {/* Tab 3: Insights — Intelligence + Psychology merged */}
      <Tabs.Screen
        name="intelligence"
        options={{
          title: 'Insights',
          tabBarIcon: ({ color }) => <Brain size={24} color={color} />,
        }}
      />

      {/* Tab 4: Evolve — Avatar studio + Archetype */}
      <Tabs.Screen
        name="studio"
        options={{
          title: 'Evolve',
          tabBarIcon: ({ color }) => <Sparkles size={24} color={color} />,
        }}
      />

      {/* Tab 5: Profile */}
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color }) => <User size={24} color={color} />,
        }}
      />

      {/* Hidden screens */}
      <Tabs.Screen name="coach" options={{ href: null }} />
      <Tabs.Screen name="shop" options={{ href: null }} />
    </Tabs>
  );
}
