import { useState, useCallback } from 'react';
import { useUserStore } from '../store/useUserStore';
import { api } from '../api/client';

export const useOptimisticAI = () => {
  const [advice, setAdvice] = useState('');
  const [loading, setLoading] = useState(false);
  const { token } = useUserStore();

  const getAdviceOptimistically = useCallback(async (userData: any, isHindi = false) => {
    // Set optimistic fallback
    const fallback = isHindi 
      ? 'आपका दिन अच्छा चल रहा है! छोटे कदमों पर ध्यान दें।'
      : 'Your day is going well! Focus on small steps.';
    
    setAdvice(fallback);
    setLoading(true);

    try {
      const response = await api("/psychological/ai-coach/advice", "POST", userData, token!);
      setAdvice(response.advice);
      return response.advice;
    } catch (error) {
      console.error('AI Coach advice fetch failed:', error);
      // Keep fallback or set a generic error advice
      return fallback;
    } finally {
      setLoading(false);
    }
  }, [token]);

  return {
    advice,
    loading,
    getAdviceOptimistically
  };
};
