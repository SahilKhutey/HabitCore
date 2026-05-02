"""
AICoachService — v2 Intelligence Layer

v2 REFRAME: This is NOT a motivator.

Old (v1): "Keep going! You got this! 🔥"
New (v2): "Your sleep pattern correlates with your performance drop. Adjust load."

The AICoachService is a Cognitive Guide:
  - Grounds every response in real behavioral data
  - Calibrates tone to UserState (StateEngine output)
  - Uses BehavioralInsights as primary context
  - Supports Gemini (primary) and OpenAI (fallback)
  - Falls back gracefully to rule-based responses if no API key

v2 Language Rules (enforced in system prompt):
  ✅ Specific and evidence-referenced
  ✅ Calm, second-person present tense
  ✅ Identity-anchored ("your patterns", "your system")
  ❌ No exclamation marks
  ❌ No motivational filler ("You got this", "Amazing job")
  ❌ No vague generics ("Keep trying", "Stay consistent")
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.services.core.state_engine import UserState, UserMode


# ── System Prompt Templates (v2 Cognitive Guide) ──────────────────────────────

_BASE_SYSTEM_PROMPT = """You are a behavioral analyst and cognitive guide for HabitCore, a behavioral operating system.

Your role is to analyze behavioral patterns and provide specific, evidence-based guidance.

STRICT LANGUAGE RULES:
- Never use exclamation marks
- Never use motivational filler phrases ("You got this", "Amazing", "Keep it up", "You're doing great")
- Never give vague advice ("Stay consistent", "Keep trying")
- Always ground advice in the user's actual data provided
- Speak in calm, second-person present tense
- Maximum 3 sentences per response
- Always end with one specific, actionable suggestion

TONE CALIBRATION (follow the tone directive provided):
- gentle: Acknowledge the user's state with compassion. Suggest minimal action. No pressure.
- supportive: Validate progress. Suggest one small, achievable next step.
- analytical: Provide behavioral pattern analysis. Be specific about what the data shows.
- challenging: The user is performing well. Suggest ambitious next steps with data backing.
"""

_TONE_SUPPLEMENTS = {
    "gentle": "The user is in a difficult state. Keep the response under 2 sentences. Focus on rest and self-regulation.",
    "supportive": "The user is recovering. Acknowledge what is working, then suggest one recovery-aligned action.",
    "analytical": "Lead with what the data shows. Then suggest the highest-leverage behavioral change.",
    "challenging": "The user's metrics are strong. Suggest expanding capacity or refining an existing behavior.",
}


class AICoachService:
    """
    v2 Cognitive Guide. Stateless — receives context per call.
    Requires behavioral context to generate non-generic responses.
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._client = None
        self._provider = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize AI client from available API keys."""
        try:
            from app.core.config import settings

            if hasattr(settings, "GEMINI_API_KEY") and settings.GEMINI_API_KEY:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._client = genai.GenerativeModel("gemini-1.5-flash")
                self._provider = "gemini"
                return

            if hasattr(settings, "OPENAI_API_KEY") and settings.OPENAI_API_KEY:
                import openai
                self._client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                self._provider = "openai"
                return

        except Exception as e:
            print(f"[AICoachService] Client init error: {e}")

        self._provider = "fallback"

    # ── Public API ────────────────────────────────────────────────────────────

    def get_guidance(
        self,
        user_id: str,
        user_state: UserState,
        insights: List[Dict[str, Any]] = None,
        checkin_summary: Dict[str, Any] = None,
        habit_completion_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate behavioral guidance grounded in real user data.

        Args:
            user_id:                    The authenticated user ID
            user_state:                 Current UserState from StateEngine
            insights:                   Recent BehavioralInsights (list of dicts)
            checkin_summary:            Today's or recent check-in data
            habit_completion_context:   Context from the triggering habit completion

        Returns:
            {"message": str, "tone": str, "source": str, "cached": bool}
        """
        cache_key = self._make_cache_key(user_id, user_state, insights)

        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if datetime.now() - entry["ts"] < timedelta(hours=4):
                return {**entry["response"], "cached": True}

        context = self._build_behavioral_context(
            user_state, insights, checkin_summary, habit_completion_context
        )

        if self._provider == "fallback":
            response = self._rule_based_guidance(user_state, insights)
        elif self._provider == "gemini":
            response = self._call_gemini(user_state, context)
        else:
            response = self._call_openai(user_state, context)

        result = {
            "message":  response,
            "tone":     user_state.ai_tone,
            "source":   self._provider,
            "cached":   False,
            "mode":     user_state.mode.value,
        }

        self._cache[cache_key] = {"response": result, "ts": datetime.now()}
        return result

    # ── Context Builder ───────────────────────────────────────────────────────

    def _build_behavioral_context(
        self,
        state: UserState,
        insights: Optional[List[Dict]] = None,
        checkin: Optional[Dict] = None,
        completion: Optional[Dict] = None,
    ) -> str:
        """Serialize behavioral context into a structured prompt string."""
        parts = []

        parts.append(f"USER MODE: {state.mode.value.upper()}")
        parts.append(f"Burnout score: {state.burnout_score:.0%}")
        parts.append(f"Completion rate (7d): {state.completion_rate:.0%}")
        parts.append(f"Current streak: {state.streak} days")
        parts.append(f"Energy level: {state.energy_level}")

        if checkin:
            parts.append(f"Today's mood: {checkin.get('mood', 'unknown')}")
            parts.append(f"Today's energy: {checkin.get('energy', 'unknown')}")
            parts.append(f"Sleep quality: {checkin.get('sleep_quality', 'unknown')}/5")

        if completion:
            parts.append(f"Just completed: {completion.get('habit_name', 'a habit')}")
            parts.append(f"Difficulty: {completion.get('difficulty', 'medium')}")

        if insights:
            top = insights[:3]
            parts.append("Recent behavioral insights:")
            for ins in top:
                parts.append(f"  [{ins.get('type','').upper()}] {ins.get('message','')}")

        return "\n".join(parts)

    # ── AI Providers ──────────────────────────────────────────────────────────

    def _call_gemini(self, state: UserState, context: str) -> str:
        try:
            tone_supplement = _TONE_SUPPLEMENTS.get(state.ai_tone, "")
            full_prompt = (
                f"{_BASE_SYSTEM_PROMPT}\n\n"
                f"TONE DIRECTIVE: {state.ai_tone.upper()} — {tone_supplement}\n\n"
                f"BEHAVIORAL CONTEXT:\n{context}\n\n"
                f"Provide behavioral guidance based on this context:"
            )
            response = self._client.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[AICoachService][Gemini] Error: {e}")
            return self._rule_based_guidance(state)

    def _call_openai(self, state: UserState, context: str) -> str:
        try:
            tone_supplement = _TONE_SUPPLEMENTS.get(state.ai_tone, "")
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"{_BASE_SYSTEM_PROMPT}\n\nTONE: {state.ai_tone} — {tone_supplement}"},
                    {"role": "user",   "content": f"BEHAVIORAL CONTEXT:\n{context}\n\nProvide guidance:"},
                ],
                max_tokens=150,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AICoachService][OpenAI] Error: {e}")
            return self._rule_based_guidance(state)

    # ── Rule-Based Fallback ───────────────────────────────────────────────────

    def _rule_based_guidance(
        self,
        state: UserState,
        insights: Optional[List[Dict]] = None,
    ) -> str:
        """
        Deterministic fallback responses keyed to UserMode.
        v2 language compliant — no hype, no filler.
        """
        if state.mode == UserMode.BURNOUT:
            if state.burnout_score >= 0.85:
                return (
                    "Your behavioral load exceeds your current capacity. "
                    "Reduce to one core habit and prioritize sleep above all other inputs."
                )
            return (
                f"Burnout indicators are present at {state.burnout_score:.0%}. "
                "Reduce your active habit count and add one restorative activity."
            )

        if state.mode == UserMode.RECOVERY:
            return (
                "Your system is in recovery. Two habits per day is the correct load. "
                "Maintain this level for 2–3 days before expanding."
            )

        if state.mode == UserMode.HIGH_PERF:
            return (
                f"Your streak of {state.streak} days reflects stable behavioral patterns. "
                f"With {state.completion_rate:.0%} consistency, you have capacity to refine one existing behavior."
            )

        # NORMAL — use top insight if available
        if insights:
            top = insights[0]
            if top.get("type") == "warning":
                return top.get("action_hint") or top.get("message", "Adjust your approach based on recent patterns.")
            return top.get("message", "Your behavioral patterns are within a normal range.")

        if state.burnout_score > 0.40:
            return (
                "Early fatigue signals are present. Maintain current habit load "
                "and avoid adding new commitments this week."
            )

        return (
            f"Completion at {state.completion_rate:.0%} over the past week. "
            "Consistent execution at this level is sufficient — focus on quality over quantity."
        )

    # ── Cache Utils ───────────────────────────────────────────────────────────

    def _make_cache_key(
        self,
        user_id: str,
        state: UserState,
        insights: Optional[List],
    ) -> str:
        top_insight_id = insights[0].get("id", "") if insights else ""
        return f"{user_id}_{state.mode}_{state.streak}_{top_insight_id}"


# ── Module-level instance for dependency injection ────────────────────────────
ai_coach_service = AICoachService()
