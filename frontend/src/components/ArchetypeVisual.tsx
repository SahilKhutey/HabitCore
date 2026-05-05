import React from 'react';
import { StyleSheet, View, Dimensions } from 'react-native';
import { MotiView } from 'moti';
import { COLORS } from '../theme/theme';

const { width } = Dimensions.get('window');

interface ArchetypeVisualProps {
  archetype: 'pioneer' | 'sage' | 'architect' | 'monk' | string;
}

export const ArchetypeVisual: React.FC<ArchetypeVisualProps> = ({ archetype }) => {
  const renderMonk = () => (
    <View style={StyleSheet.absoluteFill}>
      {[1, 2, 3].map((i) => (
        <MotiView
          key={i}
          from={{ opacity: 0, scale: 0.2 }}
          animate={{ opacity: 0.1, scale: 2 }}
          transition={{
            loop: true,
            type: 'timing',
            duration: 6000 + i * 2000,
            delay: i * 1000
          }}
          style={[styles.ring, { borderColor: '#FBBF24', borderRadius: width }]}
        />
      ))}
    </View>
  );

  const renderPioneer = () => (
    <View style={StyleSheet.absoluteFill}>
      {[1, 2, 3].map((i) => (
        <MotiView
          key={i}
          from={{ opacity: 0, scale: 0.8, rotate: '0deg' }}
          animate={{ opacity: 0.1, scale: 1.2, rotate: '360deg' }}
          transition={{
            loop: true,
            type: 'timing',
            duration: 5000 + i * 2000,
          }}
          style={[styles.shape, { borderColor: COLORS.primary, borderRadius: 20 }]}
        />
      ))}
    </View>
  );

  const renderSage = () => (
    <View style={StyleSheet.absoluteFill}>
      {[1, 2, 3].map((i) => (
        <MotiView
          key={i}
          from={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 0.15, scale: 1.5 }}
          transition={{
            loop: true,
            type: 'timing',
            duration: 4000 + i * 1500,
          }}
          style={[styles.blob, { backgroundColor: COLORS.identity.awareness, top: 20 * i, left: 10 * i }]}
        />
      ))}
    </View>
  );

  const renderArchitect = () => (
    <View style={StyleSheet.absoluteFill}>
      <View style={styles.gridContainer}>
        {[1, 2, 3, 4, 5].map((i) => (
          <MotiView
            key={i}
            from={{ opacity: 0, translateY: -20 }}
            animate={{ opacity: 0.1, translateY: 20 }}
            transition={{
              loop: true,
              type: 'timing',
              duration: 3000,
              delay: i * 500,
            }}
            style={[styles.gridLine, { top: i * 40 }]}
          />
        ))}
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      {archetype === 'monk' && renderMonk()}
      {archetype === 'pioneer' && renderPioneer()}
      {archetype === 'sage' && renderSage()}
      {archetype === 'architect' && renderArchitect()}
      {/* Fallback for unknown archetypes */}
      {!['pioneer', 'sage', 'architect', 'monk'].includes(archetype) && renderPioneer()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
  },
  shape: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderWidth: 1,
  },
  ring: {
    position: 'absolute',
    width: 300,
    height: 300,
    borderWidth: 1,
  },
  blob: {
    position: 'absolute',
    width: 150,
    height: 150,
    borderRadius: 75,
  },
  gridContainer: {
    width: '100%',
    height: '100%',
  },
  gridLine: {
    position: 'absolute',
    width: '100%',
    height: 1,
    backgroundColor: COLORS.primary,
  },
});
