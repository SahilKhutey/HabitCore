import { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useUserStore } from '../store/useUserStore';
import { api } from '../api/client';

export const useBehaviorTracking = () => {
  const [patterns, setPatterns] = useState<any>({});
  const [burnoutScore, setBurnoutScore] = useState(0);
  const { token, user } = useUserStore();

  const logEvent = async (event_type: string, event_data: any, context = {}) => {
    const event = {
      timestamp: new Date().toISOString(),
      event_type,
      event_data,
      context
    };

    try {
      // Always try to sync directly first if we have a token
      if (token) {
        await api("/psychological/behavior/log", "POST", event, token);
      } else {
        // Queue for later
        const queue = JSON.parse(await AsyncStorage.getItem('behavior_queue') || '[]');
        queue.push(event);
        await AsyncStorage.setItem('behavior_queue', JSON.stringify(queue));
      }
    } catch (error) {
      // If sync fails, queue it
      const queue = JSON.parse(await AsyncStorage.getItem('behavior_queue') || '[]');
      queue.push(event);
      await AsyncStorage.setItem('behavior_queue', JSON.stringify(queue));
    }
  };

  const syncQueue = async () => {
    if (!token) return;
    
    const queue = JSON.parse(await AsyncStorage.getItem('behavior_queue') || '[]');
    if (queue.length === 0) return;

    try {
      // For now, sync events one by one or modify backend to accept bulk
      for (const event of queue) {
        await api("/psychological/behavior/log", "POST", event, token);
      }
      await AsyncStorage.removeItem('behavior_queue');
    } catch (error) {
      console.error('Failed to sync behavior queue:', error);
    }
  };

  const loadPatterns = async () => {
    if (!token) return;
    try {
      const response = await api("/psychological/behavior/patterns", "GET", null, token);
      setPatterns(response.patterns || {});
      setBurnoutScore(response.burnout_score || 0);
    } catch (error) {
      console.error('Failed to load patterns:', error);
    }
  };

  useEffect(() => {
    if (token) {
      syncQueue();
      loadPatterns();
    }
  }, [token]);

  return {
    patterns,
    burnoutScore,
    logEvent,
    loadPatterns,
    syncQueue
  };
};
