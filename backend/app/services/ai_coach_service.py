import openai
from typing import Dict, Any, List
import json
from ..core.config import settings
from .behavior_memory_service import BehaviorMemoryService

class AICoachService:
    def __init__(self, behavior_service: BehaviorMemoryService):
        self.behavior_service = behavior_service
        # Use a mock client if API key is missing to avoid startup errors
        if settings.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
    
    def generate_personalized_advice(self, user_id: str, current_context: Dict[str, Any]) -> str:
        """Generate AI-powered personalized coaching"""
        patterns = self.behavior_service.get_user_patterns(user_id)
        burnout_score = self.behavior_service.calculate_burnout_score(user_id)
        
        prompt = self._build_coaching_prompt(patterns, burnout_score, current_context)
        
        if not self.client:
            return self._fallback_advice(patterns, burnout_score)
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a compassionate behavioral coach. Provide brief, actionable advice 
                        based on the user's patterns. Be encouraging, specific, and practical. Max 2 sentences."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI Coach error: {e}")
            return self._fallback_advice(patterns, burnout_score)
    
    def _build_coaching_prompt(self, patterns: Dict[str, Any], 
                             burnout_score: float, 
                             context: Dict[str, Any]) -> str:
        """Build context-aware prompt for AI coach"""
        prompt_parts = []
        
        if patterns.get('best_time'):
            prompt_parts.append(f"User is most productive at {patterns['best_time']['value']} (confidence: {patterns['best_time']['confidence']:.0%})")
        
        if patterns.get('worst_day'):
            prompt_parts.append(f"Struggles most on {patterns['worst_day']['value']} (success rate: {patterns['worst_day']['metadata'].get('success_rate', 0):.0%})")
        
        if burnout_score > 0.5:
            prompt_parts.append(f"Showing signs of burnout (score: {burnout_score:.0%})")
        
        if context.get('current_streak', 0) > 0:
            prompt_parts.append(f"Currently on a {context['current_streak']}-day streak")
        
        if context.get('recent_failures', 0) > 0:
            prompt_parts.append(f"Had {context['recent_failures']} recent habit failures")
        
        return "User behavior insights: " + ". ".join(prompt_parts) + ". Give one helpful suggestion."
    
    def _fallback_advice(self, patterns: Dict[str, Any], burnout_score: float) -> str:
        """Fallback advice if AI fails"""
        if burnout_score > 0.7:
            return "Consider taking a lighter day today. Your consistency will benefit from occasional rest."
        
        if patterns.get('worst_day'):
            return f"Since you often struggle on {patterns['worst_day']['value']}s, try scheduling easier habits those days."
        
        if patterns.get('best_time'):
            return f"Try scheduling important habits around {patterns['best_time']['value']} when you're most productive."
        
        return "Focus on one small habit at a time. Consistency beats perfection every day."
