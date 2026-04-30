import React from 'react';
import { View, Text, FlatList, StyleSheet, SafeAreaView } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/client';
import { useUserStore } from '../../store/useUserStore';
import { GlassCard } from '../../components/GlassCard';
import { COLORS, SPACING, TYPOGRAPHY } from '../../theme/theme';
import { Trophy } from 'lucide-react-native';

export default function LeaderboardScreen() {
  const { token } = useUserStore();

  const { data: users, isLoading } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: () => api('/users/leaderboard', 'GET', null, token),
    enabled: !!token,
  });

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Trophy size={48} color={COLORS.accent} />
        <Text style={[TYPOGRAPHY.h1, styles.title]}>Global Heroes</Text>
      </View>
      
      <FlatList
        data={users}
        keyExtractor={(item) => item.id}
        renderItem={({ item, index }) => (
          <GlassCard style={styles.userCard}>
            <View style={styles.rankContainer}>
              <Text style={[TYPOGRAPHY.h2, styles.rankText]}>#{index + 1}</Text>
            </View>
            <View style={styles.userInfo}>
              <Text style={TYPOGRAPHY.body}>{item.email.split('@')[0]}</Text>
              <Text style={TYPOGRAPHY.caption}>Level {item.level}</Text>
            </View>
            <View style={styles.xpContainer}>
              <Text style={[TYPOGRAPHY.body, { color: COLORS.primary, fontWeight: '700' }]}>
                {item.xp} XP
              </Text>
            </View>
          </GlassCard>
        )}
        contentContainerStyle={styles.listContent}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    alignItems: 'center',
    paddingVertical: SPACING.xl,
  },
  title: {
    marginTop: SPACING.sm,
  },
  listContent: {
    paddingHorizontal: SPACING.md,
    paddingBottom: SPACING.xl,
  },
  userCard: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  rankContainer: {
    width: 50,
    alignItems: 'center',
  },
  rankText: {
    color: COLORS.accent,
  },
  userInfo: {
    flex: 1,
    marginLeft: SPACING.md,
  },
  xpContainer: {
    paddingHorizontal: SPACING.md,
  },
});
