import openai
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..core.config import settings

class AIService:
    def __init__(self, behavior_service=None):
        self.behavior_service = behavior_service
        self._cache = {}
        
        if settings.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            
    def get_personalized_advice(self, user_id: str, context: Dict[str, Any]) -> str:
        """Get cached advice or generate new one via AI"""
        # Create cache key
        context_key = f"{context.get('current_streak', 0)}_{context.get('recent_failures', 0)}"
        cache_key = f"{user_id}_{context_key}"
        
        # Check cache (6 hour freshness)
        if cache_key in self._cache:
            cached_data = self._cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(hours=6):
                return cached_data['advice']
        
        # Generate new advice
        advice = self._generate_ai_advice(user_id, context)
        
        # Save to cache
        self._cache[cache_key] = {
            'advice': advice,
            'timestamp': datetime.now()
        }
        
        return advice

    def _generate_ai_advice(self, user_id: str, context: Dict[str, Any]) -> str:
        """Internal generator for AI-powered personalized coaching"""
        if not self.behavior_service:
             return "Focus on one small habit at a time. Consistency beats perfection every day."

        patterns = self.behavior_service.get_user_patterns(user_id)
        burnout_score = self.behavior_service.calculate_burnout_score(user_id)
        
        prompt = self._build_coaching_prompt(patterns, burnout_score, context)
        
        if not self.client:
            return self._fallback_advice(patterns, burnout_score)
            
        return self._call_ai_api(prompt, patterns, burnout_score)

    def _call_ai_api(self, prompt: str, patterns: Dict[str, Any], burnout_score: float) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a compassionate behavioral coach. Provide brief, actionable advice based on user patterns. Max 2 sentences."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI Service error: {e}")
            return self._fallback_advice(patterns, burnout_score)

    def _build_coaching_prompt(self, patterns: Dict[str, Any], burnout_score: float, context: Dict[str, Any]) -> str:
        prompt_parts = []
        if patterns.get('best_time'):
            prompt_parts.append(f"Most productive at {patterns['best_time']['value']}")
        if burnout_score > 0.5:
            prompt_parts.append(f"Burnout risk: {burnout_score:.0%}")
        if context.get('current_streak', 0) > 0:
            prompt_parts.append(f"{context['current_streak']}-day streak")
        
        return "User patterns: " + ". ".join(prompt_parts) + ". Give one helpful suggestion."

    def _fallback_advice(self, patterns: Dict[str, Any], burnout_score: float) -> str:
        if burnout_score > 0.7:
            return "Consider taking a lighter day today. Your consistency will benefit from occasional rest."
        return "Keep focusing on small, consistent steps. You're building a powerful routine!"

    def analyze_behavior(self, data: dict) -> str:
        """Legacy method for backward compatibility"""
        return "AI analysis complete."

def get_ai_service(behavior_service=None):
    return AIService(behavior_service)
