import React from "react";
import { View, Text, StyleSheet, FlatList, SafeAreaView, TouchableOpacity } from "react-native";
import { COLORS, TYPOGRAPHY } from "../../theme/theme";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useUserStore } from "../../store/useUserStore";
import { Trophy, Lock, ArrowLeft, Flame, Target, Star, Zap } from "lucide-react-native";
import { GlassCard } from "../../components/GlassCard";

const ALL_BADGES = [
    { id: 'early_starter', name: 'Early Starter', desc: 'Reach a 3-day streak', icon: <Zap size={24} color="#FFD700" />, type: 'streak' },
    { id: 'consistency_rookie', name: 'Consistency Rookie', desc: 'Reach a 7-day streak', icon: <Flame size={24} color="#FF4500" />, type: 'streak' },
    { id: 'immortal', name: 'The Immortal', desc: 'Reach a 30-day streak', icon: <Star size={24} color="#00FFFF" />, type: 'streak' },
    { id: 'first_step', name: 'First Step', desc: 'Complete your first habit', icon: <Target size={24} color="#00FFCC" />, type: 'habit' },
    { id: 'habit_ten', name: 'Habit Ten', desc: 'Complete 10 total habits', icon: <Trophy size={24} color="#C0C0C0" />, type: 'habit' },
    { id: 'century_hero', name: 'Century Hero', desc: 'Complete 100 total habits', icon: <Trophy size={24} color="#FFD700" />, type: 'habit' },
];

export default function BadgesScreen({ navigation }: any) {
    const { token, id } = useUserStore();

    const { data: earnedBadges = [] } = useQuery({
        queryKey: ['user_badges', id],
        queryFn: () => api(`/gamification/badges/${id}`, 'GET', null, token),
        enabled: !!id && !!token,
    });

    const isEarned = (badgeId: string) => earnedBadges.some((b: any) => b.id === badgeId || b.name.toLowerCase().replace(' ', '_') === badgeId);

    const renderItem = ({ item }: { item: typeof ALL_BADGES[0] }) => {
        const earned = isEarned(item.id);
        return (
            <GlassCard style={[styles.badgeCard, !earned && styles.lockedCard]}>
                <View style={[styles.iconCircle, !earned && styles.lockedCircle]}>
                    {earned ? item.icon : <Lock size={20} color={COLORS.textDim} />}
                </View>
                <Text style={[styles.badgeName, !earned && { color: COLORS.textDim }]}>{item.name}</Text>
                <Text style={styles.badgeDesc}>{item.desc}</Text>
                {earned && <View style={styles.checkMark}><Text style={{fontSize: 10}}>✔</Text></View>}
            </GlassCard>
        );
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
                    <ArrowLeft size={24} color={COLORS.text} />
                </TouchableOpacity>
                <Text style={TYPOGRAPHY.h1}>Achievements</Text>
            </View>

            <FlatList
                data={ALL_BADGES}
                renderItem={renderItem}
                keyExtractor={item => item.id}
                numColumns={2}
                columnWrapperStyle={styles.row}
                contentContainerStyle={styles.list}
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
        flexDirection: 'row',
        alignItems: 'center',
        padding: 20,
        gap: 15,
    },
    backBtn: {
        padding: 5,
    },
    list: {
        padding: 10,
    },
    row: {
        justifyContent: 'space-between',
    },
    badgeCard: {
        width: '47%',
        alignItems: 'center',
        padding: 20,
        marginBottom: 15,
        borderRadius: 24,
    },
    lockedCard: {
        opacity: 0.6,
        borderColor: 'rgba(255,255,255,0.05)',
    },
    iconCircle: {
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: 'rgba(255,255,255,0.05)',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 12,
    },
    lockedCircle: {
        backgroundColor: 'rgba(0,0,0,0.2)',
    },
    badgeName: {
        color: COLORS.text,
        fontSize: 14,
        fontWeight: '800',
        textAlign: 'center',
    },
    badgeDesc: {
        color: COLORS.textDim,
        fontSize: 11,
        textAlign: 'center',
        marginTop: 4,
    },
    checkMark: {
        position: 'absolute',
        top: 10,
        right: 10,
        backgroundColor: COLORS.primary,
        width: 18,
        height: 18,
        borderRadius: 9,
        justifyContent: 'center',
        alignItems: 'center',
    }
});
