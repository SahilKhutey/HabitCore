import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, SafeAreaView,
  TouchableOpacity, RefreshControl, TextInput, Modal, Alert
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../../src/theme/theme';
import { useUserStore } from '../../src/store/useUserStore';
import { GlassCard } from '../../src/components/GlassCard';
import { api } from '../../src/api/client';
import {
  Trophy, Flame, Target, Star, Zap, ArrowUpRight,
  RefreshCw, Edit3, Check, X, LogOut, Bell, ChevronRight,
  Shield, Moon, Trash2
} from 'lucide-react-native';
import { MotiView, AnimatePresence } from 'moti';

const ARCHETYPE_META: Record<string, { emoji: string; color: string; desc: string }> = {
  warrior: { emoji: '⚔️', color: '#33ffd6', desc: 'Discipline, intensity & physical excellence.' },
  monk:    { emoji: '🧘', color: '#a78bfa', desc: 'Stillness, mindfulness & inner clarity.' },
  builder: { emoji: '🚀', color: '#38bdf8', desc: 'Deep work, creation & daily output.' },
  explorer:{ emoji: '🌿', color: '#f472b6', desc: 'Curiosity, connection & varied growth.' },
  pioneer: { emoji: '🌟', color: '#33ffd6', desc: 'Blazing your own trail forward.' },
};

const DIFFICULTY_COLOR: Record<string, string> = {
  hard: '#f87171', medium: '#fbbf24', easy: '#33ffd6',
};

export default function ProfileScreen() {
  const { email, level, currentXP, nextLevelXP, coins, token, setUserInfo, resetUser } = useUserStore();
  const [state, setState] = useState<any>(null);
  const [feed, setFeed] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  // Edit name state
  const [editingName, setEditingName] = useState(false);
  const [nameInput, setNameInput] = useState('');

  // Archetype sheet
  const [showArchetypeSheet, setShowArchetypeSheet] = useState(false);
  const [selectedArchetype, setSelectedArchetype] = useState('');

  // Toast
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [stateRes, feedRes] = await Promise.all([
        api('/habits/state', 'GET', null, token),
        api('/habits/activity', 'GET', null, token),
      ]);
      setState(stateRes?.user_state);
      setUserInfo({
        level: stateRes?.user_state?.level,
        currentXP: stateRes?.user_state?.xp % 100,
        nextLevelXP: 100,
        coins: stateRes?.user_state?.coins || 0,
      });
      setFeed(feedRes?.feed || []);
      setSelectedArchetype(stateRes?.user_state?.archetype || 'pioneer');
    } catch (e) {
      console.error('Profile fetch error:', e);
    }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const handleSaveName = async () => {
    if (!nameInput.trim()) { setEditingName(false); return; }
    try {
      // Optimistic update — store display name locally
      setUserInfo({ email: `${nameInput.trim()}@habitcore.app` });
      showToast('✓ Display name updated');
    } catch (e) { console.error(e); }
    setEditingName(false);
  };

  const handleArchetypeChange = async (archetype: string) => {
    try {
      await api('/users/set-archetype', 'POST', { archetype, seed_habits: false }, token!);
      setSelectedArchetype(archetype);
      setShowArchetypeSheet(false);
      showToast(`✓ Archetype changed to ${archetype.charAt(0).toUpperCase() + archetype.slice(1)}`);
      fetchData();
    } catch (e) { console.error(e); }
  };

  const handleLogout = () => {
    Alert.alert('Sign Out', 'Are you sure you want to sign out?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign Out', style: 'destructive', onPress: () => resetUser() },
    ]);
  };

  const streak = state?.current_streak ?? 0;
  const totalXP = state?.xp ?? 0;
  const archetype = selectedArchetype || state?.archetype || state?.identity_goal?.toLowerCase() || 'pioneer';
  const archetypeMeta = ARCHETYPE_META[archetype] || ARCHETYPE_META.pioneer;

  const rawName = email?.includes('@habitcore.app')
    ? email.split('@')[0]
    : email?.split('@')[0] ?? 'User';
  const displayName = nameInput && editingName ? nameInput : rawName;
  const initials = displayName.slice(0, 2).toUpperCase();

  const getStreakEmoji = (s: number) => s >= 30 ? '🔥🔥🔥' : s >= 14 ? '🔥🔥' : s >= 7 ? '🔥' : '⚡';

  const settingsRows = [
    { icon: <Bell size={18} color={COLORS.secondary} />, bg: 'rgba(167,139,250,0.1)', label: 'Notifications', value: 'On', onPress: () => showToast('Notification settings coming soon.') },
    { icon: <Moon size={18} color={COLORS.textDim} />, bg: 'rgba(255,255,255,0.05)', label: 'Dark Mode', value: 'Always', onPress: () => showToast('Dark mode is always active in HabitCore.') },
    { icon: <Shield size={18} color={COLORS.gold} />, bg: 'rgba(251,191,36,0.1)', label: 'Privacy & Data', value: '', onPress: () => showToast('Your data is stored locally and securely.') },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <MotiView key="t" from={{ opacity: 0, translateY: -10 }} animate={{ opacity: 1, translateY: 0 }} exit={{ opacity: 0 }} style={styles.toast}>
            <Check size={14} color={COLORS.primary} />
            <Text style={styles.toastText}>{toast}</Text>
          </MotiView>
        )}
      </AnimatePresence>

      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />}
      >
        {/* ── PROFILE HEADER ── */}
        <MotiView from={{ opacity: 0, translateY: -12 }} animate={{ opacity: 1, translateY: 0 }} transition={{ type: 'spring', duration: 700 }}>
          <View style={styles.profileHeader}>
            {/* Avatar */}
            <View style={styles.avatarContainer}>
              <View style={[styles.avatarRing, { borderColor: archetypeMeta.color }]}>
                <View style={styles.avatarInner}>
                  <Text style={[styles.avatarText, { color: archetypeMeta.color }]}>{initials}</Text>
                </View>
              </View>
              <View style={[styles.lvlBadge, { backgroundColor: archetypeMeta.color }]}>
                <Text style={styles.lvlBadgeText}>{level || 1}</Text>
              </View>
            </View>

            {/* Editable Name */}
            <View style={styles.nameRow}>
              {editingName ? (
                <View style={styles.nameEditRow}>
                  <TextInput
                    style={styles.nameInput}
                    value={nameInput}
                    onChangeText={setNameInput}
                    autoFocus
                    placeholder="Display name"
                    placeholderTextColor={COLORS.textDim}
                    onSubmitEditing={handleSaveName}
                  />
                  <TouchableOpacity onPress={handleSaveName} style={styles.nameActionBtn}>
                    <Check size={16} color={COLORS.primary} />
                  </TouchableOpacity>
                  <TouchableOpacity onPress={() => setEditingName(false)} style={styles.nameActionBtn}>
                    <X size={16} color={COLORS.textDim} />
                  </TouchableOpacity>
                </View>
              ) : (
                <TouchableOpacity style={styles.nameDisplayRow} onPress={() => { setNameInput(displayName); setEditingName(true); }}>
                  <Text style={styles.userName}>{displayName}</Text>
                  <Edit3 size={14} color={COLORS.textDim} style={{ marginLeft: 8 }} />
                </TouchableOpacity>
              )}
            </View>

            {/* Archetype badge — tappable */}
            <TouchableOpacity style={[styles.archetypeBadge, { borderColor: `${archetypeMeta.color}40`, backgroundColor: `${archetypeMeta.color}10` }]} onPress={() => setShowArchetypeSheet(true)}>
              <Text style={styles.archetypeEmoji}>{archetypeMeta.emoji}</Text>
              <Text style={[styles.archetypeText, { color: archetypeMeta.color }]}>{archetype.toUpperCase()} ARCHETYPE</Text>
              <Edit3 size={10} color={archetypeMeta.color} />
            </TouchableOpacity>

            <Text style={styles.archetypeDesc}>{archetypeMeta.desc}</Text>
          </View>
        </MotiView>

        {/* ── XP BAR ── */}
        <GlassCard style={styles.xpCard}>
          <View style={styles.xpRow}>
            <Text style={styles.xpLabel}>Level {level || 1}</Text>
            <Text style={styles.xpValue}>{totalXP} XP · {coins} 🪙</Text>
          </View>
          <View style={styles.xpBarBg}>
            <View style={[styles.xpBarFill, { width: `${((currentXP || 0) / (nextLevelXP || 100)) * 100}%` }]} />
          </View>
          <Text style={styles.xpHint}>{currentXP || 0} / {nextLevelXP || 100} XP to Level {(level || 1) + 1}</Text>
        </GlassCard>

        {/* ── STATS ── */}
        <View style={styles.statsGrid}>
          <GlassCard style={styles.statItem}>
            <Flame size={22} color="#fb923c" />
            <Text style={styles.statVal}>{streak}</Text>
            <Text style={styles.statLabel}>STREAK</Text>
            <Text style={styles.statEmoji}>{getStreakEmoji(streak)}</Text>
          </GlassCard>
          <GlassCard style={styles.statItem}>
            <Zap size={22} color={COLORS.secondary} />
            <Text style={styles.statVal}>{totalXP}</Text>
            <Text style={styles.statLabel}>TOTAL XP</Text>
          </GlassCard>
          <GlassCard style={styles.statItem}>
            <Trophy size={22} color={COLORS.gold} />
            <Text style={styles.statVal}>{feed.length}</Text>
            <Text style={styles.statLabel}>COMPLETED</Text>
          </GlassCard>
        </View>

        {/* ── SETTINGS ── */}
        <Text style={styles.sectionTitle}>PREFERENCES</Text>
        <GlassCard style={styles.settingsCard}>
          {/* Change Archetype row */}
          <TouchableOpacity style={styles.settingRow} onPress={() => setShowArchetypeSheet(true)}>
            <View style={[styles.settingIcon, { backgroundColor: `${archetypeMeta.color}18` }]}>
              <Text style={{ fontSize: 16 }}>{archetypeMeta.emoji}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.settingLabel}>Identity Archetype</Text>
              <Text style={styles.settingValue}>{archetype.charAt(0).toUpperCase() + archetype.slice(1)}</Text>
            </View>
            <ChevronRight size={16} color={COLORS.textDim} />
          </TouchableOpacity>

          <View style={styles.divider} />

          {settingsRows.map((row, i) => (
            <View key={i}>
              <TouchableOpacity style={styles.settingRow} onPress={row.onPress}>
                <View style={[styles.settingIcon, { backgroundColor: row.bg }]}>{row.icon}</View>
                <Text style={[styles.settingLabel, { flex: 1 }]}>{row.label}</Text>
                {row.value ? <Text style={styles.settingValue}>{row.value}</Text> : null}
                <ChevronRight size={16} color={COLORS.textDim} />
              </TouchableOpacity>
              {i < settingsRows.length - 1 && <View style={styles.divider} />}
            </View>
          ))}
        </GlassCard>

        {/* ── ACTIVITY FEED ── */}
        <View style={styles.feedHeader}>
          <Text style={styles.sectionTitle}>ACTIVITY FEED</Text>
          <TouchableOpacity onPress={onRefresh}>
            <RefreshCw size={14} color={COLORS.primary} />
          </TouchableOpacity>
        </View>

        {feed.length === 0 ? (
          <GlassCard style={styles.emptyCard}>
            <Target size={28} color={COLORS.textDim} />
            <Text style={styles.emptyText}>Complete your first habit to build your activity feed.</Text>
          </GlassCard>
        ) : (
          feed.map((item, i) => (
            <MotiView key={item.id || i} from={{ opacity: 0, translateX: -16 }} animate={{ opacity: 1, translateX: 0 }} transition={{ delay: i * 50 }}>
              <GlassCard style={styles.activityItem}>
                <View style={[styles.activityIcon, { backgroundColor: `${DIFFICULTY_COLOR[item.difficulty] || COLORS.primary}18` }]}>
                  <Star size={18} color={DIFFICULTY_COLOR[item.difficulty] || COLORS.primary} />
                </View>
                <View style={{ flex: 1 }}>
                  <View style={styles.activityRowTop}>
                    <Text style={styles.activityTitle}>{item.habit_name}</Text>
                    <Text style={styles.activityTime}>{item.time_ago}</Text>
                  </View>
                  <Text style={styles.activityDesc}>+{item.xp_earned} XP · {item.difficulty?.toUpperCase()}</Text>
                </View>
                <ArrowUpRight size={14} color={COLORS.textDim} />
              </GlassCard>
            </MotiView>
          ))
        )}

        {/* ── SIGN OUT ── */}
        <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
          <LogOut size={16} color="#f87171" />
          <Text style={styles.logoutText}>Sign Out</Text>
        </TouchableOpacity>
      </ScrollView>

      {/* ── ARCHETYPE CHANGE SHEET ── */}
      <Modal visible={showArchetypeSheet} animationType="slide" transparent onRequestClose={() => setShowArchetypeSheet(false)}>
        <View style={styles.sheetBg}>
          <View style={styles.sheet}>
            <View style={styles.sheetHandle} />
            <Text style={styles.sheetTitle}>Change Identity Archetype</Text>
            <Text style={styles.sheetSub}>Reshapes your AI coaching, habit suggestions, and identity goals.</Text>
            {Object.entries(ARCHETYPE_META).map(([id, meta]) => (
              <TouchableOpacity key={id} style={[styles.archCard, { borderColor: `${meta.color}40`, backgroundColor: selectedArchetype === id ? `${meta.color}10` : 'rgba(255,255,255,0.02)' }]} onPress={() => handleArchetypeChange(id)}>
                <Text style={styles.archEmoji}>{meta.emoji}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={[styles.archName, { color: meta.color }]}>{id.charAt(0).toUpperCase() + id.slice(1)}</Text>
                  <Text style={styles.archDesc}>{meta.desc}</Text>
                </View>
                {selectedArchetype === id && <Check size={18} color={meta.color} />}
              </TouchableOpacity>
            ))}
            <TouchableOpacity style={styles.cancelBtn} onPress={() => setShowArchetypeSheet(false)}>
              <Text style={styles.cancelText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  content: { padding: SPACING.margin, paddingBottom: 120 },

  toast: { position: 'absolute', top: 56, left: 16, right: 16, zIndex: 999, flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: 'rgba(15,23,42,0.97)', borderWidth: 1, borderColor: 'rgba(51,255,214,0.3)', borderRadius: 14, padding: 14, elevation: 8 },
  toastText: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 13, color: COLORS.text, flex: 1 },

  // Header
  profileHeader: { alignItems: 'center', marginBottom: SPACING.lg },
  avatarContainer: { position: 'relative', marginBottom: 16 },
  avatarRing: { width: 108, height: 108, borderRadius: 54, borderWidth: 2.5, alignItems: 'center', justifyContent: 'center', padding: 4 },
  avatarInner: { width: 96, height: 96, borderRadius: 48, backgroundColor: COLORS.surfaceLight, alignItems: 'center', justifyContent: 'center' },
  avatarText: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 34 },
  lvlBadge: { position: 'absolute', bottom: -2, right: -2, width: 30, height: 30, borderRadius: 15, alignItems: 'center', justifyContent: 'center', borderWidth: 2, borderColor: COLORS.background },
  lvlBadgeText: { color: '#000', fontWeight: '900', fontSize: 12 },

  // Name edit
  nameRow: { marginBottom: 10 },
  nameDisplayRow: { flexDirection: 'row', alignItems: 'center' },
  userName: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 26, color: COLORS.text },
  nameEditRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  nameInput: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 22, color: COLORS.text, borderBottomWidth: 1.5, borderBottomColor: COLORS.primary, paddingVertical: 4, paddingHorizontal: 8, minWidth: 140 },
  nameActionBtn: { padding: 6 },

  // Archetype badge
  archetypeBadge: { flexDirection: 'row', alignItems: 'center', gap: 6, borderRadius: 20, paddingHorizontal: 14, paddingVertical: 7, borderWidth: 1, marginTop: 4 },
  archetypeEmoji: { fontSize: 14 },
  archetypeText: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 10, letterSpacing: 1.5 },
  archetypeDesc: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 12, color: COLORS.textDim, marginTop: 8, textAlign: 'center', lineHeight: 18 },

  // XP bar
  xpCard: { padding: SPACING.md, marginBottom: SPACING.lg },
  xpRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 10 },
  xpLabel: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 13, color: COLORS.text },
  xpValue: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 12, color: COLORS.textSecondary },
  xpBarBg: { height: 6, backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden', marginBottom: 6 },
  xpBarFill: { height: '100%', backgroundColor: COLORS.primary, borderRadius: 3 },
  xpHint: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 10, color: COLORS.textDim },

  // Stats
  statsGrid: { flexDirection: 'row', gap: 10, marginBottom: SPACING.lg },
  statItem: { flex: 1, alignItems: 'center', paddingVertical: 16, gap: 6 },
  statVal: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 22, color: COLORS.text },
  statLabel: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 8, color: COLORS.textDim, letterSpacing: 1 },
  statEmoji: { fontSize: 14 },

  // Section title
  sectionTitle: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 9, color: COLORS.textDim, letterSpacing: 2, marginBottom: 12, marginTop: 4 },

  // Settings
  settingsCard: { padding: 0, marginBottom: SPACING.lg, overflow: 'hidden' },
  settingRow: { flexDirection: 'row', alignItems: 'center', gap: 14, paddingHorizontal: 16, paddingVertical: 14 },
  settingIcon: { width: 38, height: 38, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  settingLabel: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 14, color: COLORS.text },
  settingValue: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 12, color: COLORS.textDim, marginRight: 6 },
  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.04)', marginLeft: 68 },

  // Feed
  feedHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  emptyCard: { alignItems: 'center', padding: SPACING.xl, gap: 12 },
  emptyText: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 14, color: COLORS.textSecondary, textAlign: 'center', lineHeight: 20 },
  activityItem: { flexDirection: 'row', alignItems: 'center', padding: 14, marginBottom: 10 },
  activityIcon: { width: 40, height: 40, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginRight: 14 },
  activityRowTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  activityTitle: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 13, color: COLORS.text, flex: 1 },
  activityTime: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 10, color: COLORS.textDim },
  activityDesc: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 12, color: COLORS.textSecondary },

  // Logout
  logoutBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10, marginTop: SPACING.xl, padding: 16, borderRadius: 16, borderWidth: 1, borderColor: 'rgba(248,113,113,0.25)', backgroundColor: 'rgba(248,113,113,0.06)' },
  logoutText: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 14, color: '#f87171' },

  // Archetype sheet
  sheetBg: { flex: 1, backgroundColor: 'rgba(0,0,0,0.65)', justifyContent: 'flex-end' },
  sheet: { backgroundColor: COLORS.surfaceLight, borderTopLeftRadius: 28, borderTopRightRadius: 28, padding: SPACING.lg, paddingBottom: 44 },
  sheetHandle: { width: 40, height: 4, backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: 2, alignSelf: 'center', marginBottom: 20 },
  sheetTitle: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 20, color: COLORS.text, marginBottom: 6 },
  sheetSub: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 13, color: COLORS.textSecondary, marginBottom: 20, lineHeight: 19 },
  archCard: { flexDirection: 'row', alignItems: 'center', gap: 14, padding: 14, borderWidth: 1, borderRadius: 16, marginBottom: 10 },
  archEmoji: { fontSize: 26 },
  archName: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 16 },
  archDesc: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 11, color: COLORS.textSecondary, marginTop: 2 },
  cancelBtn: { marginTop: 4, padding: 14, alignItems: 'center' },
  cancelText: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 14, color: COLORS.textDim },
});
