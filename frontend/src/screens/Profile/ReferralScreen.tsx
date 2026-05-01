import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Share, SafeAreaView } from "react-native";
import { COLORS, TYPOGRAPHY } from "../../theme/theme";
import { useUserStore } from "../../store/useUserStore";
import { Gift, Copy, Share2, ArrowLeft, Users } from "lucide-react-native";
import { triggerHaptic } from "../../utils/animationManager";

export default function ReferralScreen({ navigation }: any) {
    const { id } = useUserStore();
    const referralCode = `HERO${id?.substring(0, 5).toUpperCase()}`;

    const handleShare = async () => {
        try {
            await Share.share({
                message: `Join HabitHero and become the best version of yourself! Use my code ${referralCode} to get 50 bonus coins. 🚀\n\nDownload now: https://habithero.app`,
            });
            triggerHaptic("coins");
        } catch (error) {
            console.log(error);
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()}>
                    <ArrowLeft size={24} color={COLORS.text} />
                </TouchableOpacity>
                <Text style={TYPOGRAPHY.h1}>Refer & Earn</Text>
            </View>

            <View style={styles.content}>
                <View style={styles.hero}>
                    <Gift size={80} color={COLORS.primary} />
                    <Text style={styles.heroTitle}>Give 50, Get 50</Text>
                    <Text style={styles.heroSub}>
                        Invite your friends to HabitHero. When they join using your code, both of you get 50 coins to spend in the Hero Shop!
                    </Text>
                </View>

                <View style={styles.codeBox}>
                    <Text style={styles.codeLabel}>YOUR REFERRAL CODE</Text>
                    <View style={styles.codeRow}>
                        <Text style={styles.codeText}>{referralCode}</Text>
                        <TouchableOpacity 
                            style={styles.copyBtn}
                            onPress={() => triggerHaptic("impactLight")}
                        >
                            <Copy size={20} color={COLORS.primary} />
                        </TouchableOpacity>
                    </View>
                </View>

                <TouchableOpacity style={styles.shareBtn} onPress={handleShare}>
                    <Share2 size={20} color="#000" />
                    <Text style={styles.shareText}>Invite Friends</Text>
                </TouchableOpacity>

                <View style={styles.stats}>
                    <View style={styles.statItem}>
                        <Users size={20} color={COLORS.textDim} />
                        <Text style={styles.statValue}>0</Text>
                        <Text style={styles.statLabel}>Invited</Text>
                    </View>
                    <View style={styles.statItem}>
                        <Gift size={20} color={COLORS.textDim} />
                        <Text style={styles.statValue}>0</Text>
                        <Text style={styles.statLabel}>Coins Earned</Text>
                    </View>
                </View>
            </View>
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
    content: {
        padding: 24,
        alignItems: 'center',
    },
    hero: {
        alignItems: 'center',
        marginBottom: 40,
    },
    heroTitle: {
        color: COLORS.text,
        fontSize: 28,
        fontWeight: '900',
        marginTop: 20,
    },
    heroSub: {
        color: COLORS.textDim,
        fontSize: 15,
        textAlign: 'center',
        marginTop: 10,
        lineHeight: 22,
        paddingHorizontal: 10,
    },
    codeBox: {
        width: '100%',
        backgroundColor: COLORS.surface,
        padding: 20,
        borderRadius: 24,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.05)',
        marginBottom: 20,
    },
    codeLabel: {
        color: COLORS.textDim,
        fontSize: 12,
        fontWeight: '800',
        letterSpacing: 1,
        textAlign: 'center',
        marginBottom: 10,
    },
    codeRow: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 15,
    },
    codeText: {
        color: COLORS.primary,
        fontSize: 32,
        fontWeight: '900',
        letterSpacing: 2,
    },
    copyBtn: {
        padding: 10,
        backgroundColor: 'rgba(0, 255, 204, 0.1)',
        borderRadius: 12,
    },
    shareBtn: {
        backgroundColor: COLORS.primary,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20,
        borderRadius: 20,
        width: '100%',
        gap: 12,
        shadowColor: COLORS.primary,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 10,
        elevation: 5,
    },
    shareText: {
        color: '#000',
        fontSize: 18,
        fontWeight: '800',
    },
    stats: {
        flexDirection: 'row',
        width: '100%',
        marginTop: 40,
        gap: 20,
    },
    statItem: {
        flex: 1,
        backgroundColor: 'rgba(255,255,255,0.02)',
        padding: 20,
        borderRadius: 20,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.05)',
    },
    statValue: {
        color: COLORS.text,
        fontSize: 20,
        fontWeight: '800',
        marginTop: 5,
    },
    statLabel: {
        color: COLORS.textDim,
        fontSize: 12,
        fontWeight: '600',
    }
});
