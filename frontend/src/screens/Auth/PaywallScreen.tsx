import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, ScrollView } from "react-native";
import { COLORS } from "../../theme/theme";
import { CheckCircle2, X, Zap, Snowflake, BarChart3, Palette, ShieldCheck } from "lucide-react-native";
import { useUserStore } from "../../store/useUserStore";
import { api } from "../../api/client";
import { triggerHaptic } from "../../utils/animationManager";

export default function PaywallScreen({ navigation }: any) {
  const { token, setUserInfo } = useUserStore();

  const handleSubscribe = async () => {
    try {
      await api('/users/subscribe', 'POST', null, token);
      setUserInfo({ isPremium: true });
      triggerHaptic("level_up");
      navigation.goBack();
    } catch (err) {
      alert("Subscription failed. Please try again.");
    }
  };

  const features = [
    { title: "Unlimited Habits", icon: <CheckCircle2 color={COLORS.primary} size={20} />, desc: "Track as many habits as you need." },
    { title: "5 Streak Freezes", icon: <Snowflake color={COLORS.primary} size={20} />, desc: "Protect your momentum on tough days." },
    { title: "Exclusive Themes", icon: <Palette color={COLORS.primary} size={20} />, desc: "Personalize with Cyberpunk & Neon Glow." },
    { title: "Deep Analytics", icon: <BarChart3 color={COLORS.primary} size={20} />, desc: "Visualize your long-term growth trends." },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <TouchableOpacity style={styles.closeBtn} onPress={() => navigation.goBack()}>
        <X color={COLORS.textDim} size={24} />
      </TouchableOpacity>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.hero}>
          <ShieldCheck size={64} color={COLORS.primary} />
          <Text style={styles.title}>Unlock Your Potential</Text>
          <Text style={styles.subtitle}>Don't let anything stop your streak. Upgrade to Premium for the full experience.</Text>
        </View>

        <View style={styles.features}>
          {features.map((f, i) => (
            <View key={i} style={styles.featureItem}>
              <View style={styles.featureIcon}>{f.icon}</View>
              <View>
                <Text style={styles.featureTitle}>{f.title}</Text>
                <Text style={styles.featureDesc}>{f.desc}</Text>
              </View>
            </View>
          ))}
        </View>

        <View style={styles.pricing}>
          <View style={styles.pricingHeader}>
            <Zap size={16} color={COLORS.primary} fill={COLORS.primary} />
            <Text style={styles.pricingHeaderText}>LIMITED OFFER: 50% OFF</Text>
          </View>
          <View style={styles.priceRow}>
            <View style={styles.priceOption}>
                <Text style={styles.priceValue}>₹999 / year</Text>
                <Text style={styles.priceDetail}>Save 40%</Text>
            </View>
            <View style={[styles.priceOption, styles.activeOption]}>
                <Text style={styles.priceValue}>₹199 / month</Text>
                <Text style={styles.priceDetail}>Cancel anytime</Text>
            </View>
          </View>
        </View>

        <TouchableOpacity style={styles.subscribeBtn} onPress={handleSubscribe}>
          <Text style={styles.subscribeText}>Start Free Trial</Text>
        </TouchableOpacity>

        <Text style={styles.footerText}>Secure payment via App Store. Cancel anytime in settings.</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  closeBtn: {
    position: 'absolute',
    top: 50,
    right: 20,
    zIndex: 10,
    padding: 10,
  },
  content: {
    padding: 24,
    paddingTop: 60,
  },
  hero: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    color: COLORS.text,
    fontSize: 28,
    fontWeight: '900',
    textAlign: 'center',
    marginTop: 20,
  },
  subtitle: {
    color: COLORS.textDim,
    fontSize: 16,
    textAlign: 'center',
    marginTop: 10,
    lineHeight: 22,
  },
  features: {
    marginBottom: 40,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 20,
    gap: 15,
  },
  featureIcon: {
    backgroundColor: 'rgba(0, 255, 204, 0.1)',
    padding: 8,
    borderRadius: 12,
  },
  featureTitle: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: '700',
  },
  featureDesc: {
    color: COLORS.textDim,
    fontSize: 14,
    marginTop: 2,
  },
  pricing: {
    backgroundColor: COLORS.surface,
    padding: 20,
    borderRadius: 24,
    marginBottom: 30,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  pricingHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginBottom: 20,
  },
  pricingHeaderText: {
    color: COLORS.primary,
    fontSize: 12,
    fontWeight: '900',
    letterSpacing: 1,
  },
  priceRow: {
    flexDirection: 'row',
    gap: 10,
  },
  priceOption: {
    flex: 1,
    padding: 15,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#333',
    alignItems: 'center',
  },
  activeOption: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(0, 255, 204, 0.05)',
  },
  priceValue: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: '800',
  },
  priceDetail: {
    color: COLORS.textDim,
    fontSize: 12,
    marginTop: 4,
  },
  subscribeBtn: {
    backgroundColor: COLORS.primary,
    padding: 20,
    borderRadius: 20,
    alignItems: 'center',
    elevation: 5,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
  },
  subscribeText: {
    color: '#000',
    fontSize: 18,
    fontWeight: '900',
  },
  footerText: {
    color: COLORS.textDim,
    fontSize: 12,
    textAlign: 'center',
    marginTop: 20,
    opacity: 0.6,
  }
});
