import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, ScrollView, TouchableOpacity } from 'react-native';
import { Trophy, Award, Crown, ShieldCheck } from 'lucide-react-native';
import { useUserStore } from '../../store/useUserStore';
import { getLeaderboard, getMyBadges } from '../../api/client';

const HeroScreen = () => {
  const { user, isPremium } = useUserStore();
  const [leaderboard, setLeaderboard] = useState([]);
  const [badges, setBadges] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const lb = await getLeaderboard();
      const b = await getMyBadges();
      setLeaderboard(lb);
      setBadges(b);
    } catch (e) {
      console.error(e);
    }
  };

  const renderBadge = ({ item }) => (
    <View style={styles.badgeCard}>
      <Award color={item.is_premium_exclusive ? "#FFD700" : "#00ffcc"} size={32} />
      <Text style={styles.badgeName}>{item.name}</Text>
      <Text style={styles.badgeDate}>{new Date(item.earned_at).toLocaleDateString()}</Text>
    </View>
  );

  const renderLeader = ({ item, index }) => (
    <View style={[styles.leaderRow, item.id === user.id && styles.myRow]}>
      <Text style={styles.rank}>#{index + 1}</Text>
      <View style={styles.userInfo}>
        <Text style={styles.userName}>{item.email.split('@')[0]}</Text>
        {item.is_premium && <Crown size={14} color="#FFD700" style={{ marginLeft: 5 }} />}
      </View>
      <Text style={styles.xp}>{item.xp} XP</Text>
    </View>
  );

  if (!isPremium) {
    return (
      <View style={styles.upsellContainer}>
        <Crown color="#FFD700" size={64} />
        <Text style={styles.upsellTitle}>Join the Hall of Heroes</Text>
        <Text style={styles.upsellText}>
          Unlock global leaderboards, exclusive badges, and premium themes.
        </Text>
        <TouchableOpacity style={styles.upsellButton}>
          <Text style={styles.buttonText}>Upgrade to Premium</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <ShieldCheck color="#FFD700" size={48} />
        <Text style={styles.title}>Hall of Heroes</Text>
        <Text style={styles.subtitle}>Welcome back, Immortal Hero.</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Global Leaderboard</Text>
        {leaderboard.map((item, index) => renderLeader({ item, index }))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Your Achievements</Text>
        <FlatList
          data={badges}
          renderItem={renderBadge}
          horizontal
          showsHorizontalScrollIndicator={false}
          keyExtractor={(item) => item.id}
        />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', padding: 20 },
  header: { alignItems: 'center', marginVertical: 30 },
  title: { color: '#fff', fontSize: 32, fontWeight: 'bold', marginTop: 10 },
  subtitle: { color: '#888', fontSize: 16 },
  section: { marginBottom: 30 },
  sectionTitle: { color: '#fff', fontSize: 20, fontWeight: 'bold', marginBottom: 15 },
  leaderRow: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    backgroundColor: '#111', 
    padding: 15, 
    borderRadius: 12, 
    marginBottom: 10 
  },
  myRow: { borderColor: '#FFD700', borderWidth: 1 },
  rank: { color: '#888', fontSize: 18, width: 40 },
  userInfo: { flex: 1, flexDirection: 'row', alignItems: 'center' },
  userName: { color: '#fff', fontSize: 16 },
  xp: { color: '#00ffcc', fontWeight: 'bold' },
  badgeCard: { 
    backgroundColor: '#111', 
    padding: 20, 
    borderRadius: 16, 
    alignItems: 'center', 
    marginRight: 15,
    width: 140
  },
  badgeName: { color: '#fff', fontSize: 14, fontWeight: 'bold', marginTop: 10, textAlign: 'center' },
  badgeDate: { color: '#555', fontSize: 10, marginTop: 5 },
  upsellContainer: { flex: 1, backgroundColor: '#000', justifyContent: 'center', alignItems: 'center', padding: 40 },
  upsellTitle: { color: '#fff', fontSize: 24, fontWeight: 'bold', marginVertical: 20 },
  upsellText: { color: '#888', textAlign: 'center', lineHeight: 22, marginBottom: 30 },
  upsellButton: { backgroundColor: '#FFD700', paddingVertical: 15, paddingHorizontal: 40, borderRadius: 30 },
  buttonText: { color: '#000', fontWeight: 'bold', fontSize: 16 }
});

export default HeroScreen;
