import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { COLORS } from "../theme/theme";

interface LevelHeaderProps {
  level: number;
  currentXP: number;
  nextLevelXP: number;
}

export const LevelHeader: React.FC<LevelHeaderProps> = ({ level, currentXP, nextLevelXP }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.levelText}>Level {level}</Text>
      <Text style={styles.xpText}>
        {currentXP} / {nextLevelXP} XP
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'flex-start',
    justifyContent: 'center',
  },
  levelText: {
    color: COLORS.text,
    fontSize: 24,
    fontWeight: '900',
  },
  xpText: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '600',
    marginTop: 2,
  },
});
