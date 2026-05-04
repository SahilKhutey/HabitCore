import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, SafeAreaView,
  TouchableOpacity, RefreshControl, TextInput, Alert
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, RADIUS, SHADOWS } from '../../src/theme/theme';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { api } from '../../src/api/client';
import {
  Trophy, Flame, Target, Zap, 
  RefreshCw, Edit3, Check, X, LogOut, Bell, ChevronRight,
  Shield, Moon
} from 'lucide-react-native';
import { MotiView, AnimatePresence } from 'moti';
import { triggerHaptic } from '../../src/utils/animationManager';

export default function ProfileScreen() {
  const { email, level, xp, coins, token, setUserInfo, resetUser } = useUserStore();
  const [state, setState] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [editingName, setEditingName] = useState(false);
  const [nameInput, setNameInput] = useState('');

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const stateRes = await api('/habits/state', 'GET', null, token);
      setState(stateRes?.user_state);
      setUserInfo({
        level: stateRes?.user_state?.level,
        xp: stateRes?.user_state?.xp,
        coins: stateRes?.user_state?.coins || 0,
      });
    } catch (e) {
      console.error('Profile fetch error:', e);
    }
  }, [token, setUserInfo]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const handleLogout = () => {
    triggerHaptic('impactMedium');
    Alert.alert('Sign Out', 'Are you sure you want to exit your cognitive sanctuary?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign Out', style: 'destructive', onPress: () => resetUser() },
    ]);
  };

  const streak = state?.current_streak ?? 0;
  const rawName = email?.split('@')[0] ?? 'Explorer';
  const displayName = nameInput && editingName ? nameInput : rawName;
  const initials = displayName.slice(0, 2).toUpperCase();

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />}
      >
        <MotiView from={{ opacity: 0, translateY: -10 }} animate={{ opacity: 1, translateY: 0 }}>
          <View style={styles.profileHeader}>
            <View style={styles.avatarContainer}>
               <View style={styles.avatarInner}>
                 <Text style={styles.avatarText}>{initials}</Text>
               </View>
               <View style={styles.lvlBadge}>
                 <Text style={styles.lvlBadgeText}>{level}</Text>
               </View>
            </View>

            <Text style={styles.userName}>{displayName}</Text>
            <Text style={styles.userEmail}>{email}</Text>
          </View>
        </MotiView>

        <GlassCard style={styles.xpCard}>
          <View style={styles.xpRow}>
            <Text style={styles.xpLabel}>Level Progress</Text>
            <Text style={styles.xpValue}>{xp % 100} / 100 XP</Text>
          </View>
          <View style={styles.xpBarBg}>
            <View style={[styles.xpBarFill, { width: `${xp % 100}%` }]} />
          </View>
        </GlassCard>

        <View style={styles.statsGrid}>
          <GlassCard style={styles.statItem}>
            <Flame size={20} color={COLORS.warning} />
            <Text style={styles.statVal}>{streak}</Text>
            <Text style={styles.statLabel}>STREAK</Text>
          </GlassCard>
          <GlassCard style={styles.statItem}>
            <Zap size={20} color={COLORS.primary} />
            <Text style={styles.statVal}>{coins}</Text>
            <Text style={styles.statLabel}>TREASURY</Text>
          </GlassCard>
          <GlassCard style={styles.statItem}>
            <Trophy size={20} color={COLORS.identity.awareness} />
            <Text style={styles.statVal}>{level}</Text>
            <Text style={styles.statLabel}>LEVEL</Text>
          </GlassCard>
        </View>

        <Text style={styles.sectionTitle}>SYSTEM PREFERENCES</Text>
        <GlassCard style={styles.settingsCard}>
          <TouchableOpacity style={styles.settingRow}>
            <Bell size={18} color={COLORS.textDim} />
            <Text style={styles.settingLabel}>Notifications</Text>
            <ChevronRight size={16} color={COLORS.border} />
          </TouchableOpacity>
          <View style={styles.divider} />
          <TouchableOpacity style={styles.settingRow}>
            <Shield size={18} color={COLORS.textDim} />
            <Text style={styles.settingLabel}>Privacy & Security</Text>
            <ChevronRight size={16} color={COLORS.border} />
          </TouchableOpacity>
        </GlassCard>

        <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
          <LogOut size={18} color={COLORS.danger} />
          <Text style={styles.logoutText}>Sign Out</Text>
        </TouchableOpacity>
        
        <Text style={styles.versionText}>HabitCore v2.4.0 (Production Build)</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  content: { padding: SPACING[5], paddingBottom: 100 },
  profileHeader: { alignItems: 'center', marginBottom: SPACING[8], marginTop: SPACING[4] },
  avatarContainer: { marginBottom: SPACING[4], position: 'relative' },
  avatarInner: { 
    width: 100, 
    height: 100, 
    borderRadius: 50, 
    backgroundColor: COLORS.surface, 
    alignItems: 'center', 
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: COLORS.primary
  },
  avatarText: { ...TYPOGRAPHY.h1, fontSize: 36, color: COLORS.primary },
  lvlBadge: { 
    position: 'absolute', 
    bottom: 0, 
    right: 0, 
    backgroundColor: COLORS.primary, 
    width: 32, 
    height: 32, 
    borderRadius: 16, 
    alignItems: 'center', 
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: COLORS.background
  },
  lvlBadgeText: { color: '#fff', fontWeight: 'bold', fontSize: 12 },
  userName: { ...TYPOGRAPHY.h2, color: COLORS.text, marginBottom: 2 },
  userEmail: { ...TYPOGRAPHY.body, color: COLORS.textDim, fontSize: 14 },
  
  xpCard: { padding: SPACING[5], borderRadius: RADIUS.lg, marginBottom: SPACING[6], backgroundColor: COLORS.surface },
  xpRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 10 },
  xpLabel: { ...TYPOGRAPHY.label, fontSize: 10, color: COLORS.textSecondary },
  xpValue: { ...TYPOGRAPHY.caption, color: COLORS.textDim },
  xpBarBg: { height: 6, backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: RADIUS.full, overflow: 'hidden' },
  xpBarFill: { height: '100%', backgroundColor: COLORS.primary, borderRadius: RADIUS.full },
  
  statsGrid: { flexDirection: 'row', gap: SPACING[3], marginBottom: SPACING[8] },
  statItem: { flex: 1, alignItems: 'center', padding: SPACING[5], borderRadius: RADIUS.lg, backgroundColor: COLORS.surface },
  statVal: { ...TYPOGRAPHY.h2, fontSize: 24, color: COLORS.text, marginTop: 4 },
  statLabel: { ...TYPOGRAPHY.label, fontSize: 8, color: COLORS.textDim, marginTop: 2, letterSpacing: 1.5 },
  
  sectionTitle: { ...TYPOGRAPHY.label, color: COLORS.textDim, fontSize: 10, letterSpacing: 2, marginBottom: SPACING[4] },
  settingsCard: { padding: 0, borderRadius: RADIUS.xl, overflow: 'hidden', backgroundColor: COLORS.surface },
  settingRow: { flexDirection: 'row', alignItems: 'center', gap: SPACING[4], padding: SPACING[5] },
  settingLabel: { ...TYPOGRAPHY.body, color: COLORS.text, flex: 1, fontSize: 15 },
  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.03)', marginLeft: SPACING[12] },
  
  logoutBtn: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'center', 
    gap: SPACING[3], 
    marginTop: SPACING[8], 
    padding: SPACING[5], 
    borderRadius: RADIUS.xl, 
    borderWidth: 1, 
    borderColor: 'rgba(248,113,113,0.2)',
    backgroundColor: 'rgba(248,113,113,0.05)'
  },
  logoutText: { ...TYPOGRAPHY.h3, color: COLORS.danger, fontSize: 16 },
  versionText: { ...TYPOGRAPHY.caption, color: COLORS.textDim, textAlign: 'center', marginTop: SPACING[10], fontSize: 10 }
});
