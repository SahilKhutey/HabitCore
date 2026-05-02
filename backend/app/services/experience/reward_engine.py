"""
RewardEngine — v2 Experience Layer

v2 REFRAME: Rewards reinforce identity, not replace it.

REMOVED (v1 anti-patterns):
  ❌ random.choice() variable rewards (dopamine manipulation)
  ❌ Mystery reward boxes
  ❌ "COMBO x3 🔥" language
  ❌ Arbitrary coin spam
  ❌ Confetti on every action

KEPT and REFRAMED:
  ✅ XP (consistent, predictable, meaning-labeled)
  ✅ Coins (only at meaningful identity milestones)
  ✅ Streak acknowledgment (identity-anchored)
  ✅ Level progression (behavioral framing)
  ✅ Adaptive difficulty XP multiplier (earned, not random)

Language rule: ALL reward messages must be calm and identity-grounded.
  ❌ "🎉 +50 XP AMAZING!"
  ✅ "Consistent with your path. Progress recorded."
"""
from typing import Dict, Any, Optional
from app.services.core.state_engine import UserState, UserMode


# ── XP Calculation Constants ──────────────────────────────────────────────────

BASE_XP = {
    "easy":   10,
    "medium": 20,
    "hard":   35,
}

STREAK_BONUS_PER_DAY = 2      # +2 XP per streak day (capped)
STREAK_BONUS_CAP     = 30     # max +30 from streak

CONSISTENCY_MULTIPLIER_MAX = 1.5   # max 1.5x for 100% consistency
BURNOUT_XP_REDUCTION       = 0.5   # 50% XP in RECOVERY mode (lower pressure)

# Level progression: XP threshold = 100 * level^1.5
def xp_for_level(level: int) -> int:
    if level <= 1: return 0
    return int(100 * (level ** 1.5))

# Coin milestones — only at identity-meaningful thresholds
COIN_MILESTONES = {
    7:   {"coins": 10, "message": "7 days of discipline recorded."},
    14:  {"coins": 20, "message": "Two weeks of consistent behavior."},
    30:  {"coins": 50, "message": "30 days. Patterns at this frequency are consolidating."},
    60:  {"coins": 100, "message": "60 days of commitment. This is becoming structural."},
    100: {"coins": 200, "message": "100-day mark. Your behavioral baseline has shifted."},
}

# Identity messages by archetype — v2 tone compliant
ARCHETYPE_COMPLETION_MESSAGES = {
    "warrior":  "Disciplined execution. Consistent with the Warrior pattern.",
    "monk":     "Presence and consistency. The Monk path advances.",
    "builder":  "Another block placed. The Builder compounds daily.",
    "explorer": "Curiosity acted upon. The Explorer expands.",
    "pioneer":  "Progress noted. The Pioneer continues.",
}

# Level-up messages — v2 language
LEVEL_UP_MESSAGES = {
    range(1,   6):  "Behavioral patterns are beginning to establish.",
    range(6,  16):  "Consistency at this level is creating neural reinforcement.",
    range(16, 31):  "Your behavioral baseline is measurably different from when you began.",
    range(31, 101): "Long-term consistency. This is identity-level change.",
}


class RewardEngine:
    """
    Stateless reward calculation engine.
    All outputs are deterministic — no randomness.
    """

    @staticmethod
    def calculate_xp(
        difficulty: str,
        streak: int,
        consistency_rate: float,
        user_state: Optional[UserState] = None,
    ) -> Dict[str, Any]:
        """
        Calculate XP for a habit completion.
        Deterministic, not random. Based purely on behavioral metrics.

        Returns:
            {xp_earned, base_xp, streak_bonus, consistency_bonus, mode_modifier}
        """
        base_xp = BASE_XP.get(difficulty, 20)
        streak_bonus = min(streak * STREAK_BONUS_PER_DAY, STREAK_BONUS_CAP)
        consistency_bonus = int(base_xp * min(consistency_rate * 0.5, 0.5))  # max 50% bonus

        subtotal = base_xp + streak_bonus + consistency_bonus

        # Mode modifier: reduce XP pressure in recovery (de-stakes the experience)
        mode_modifier = 1.0
        if user_state and user_state.mode == UserMode.RECOVERY:
            mode_modifier = BURNOUT_XP_REDUCTION

        total_xp = int(subtotal * mode_modifier)

        return {
            "xp_earned":        total_xp,
            "base_xp":          base_xp,
            "streak_bonus":     streak_bonus,
            "consistency_bonus": consistency_bonus,
            "mode_modifier":    mode_modifier,
        }

    @staticmethod
    def get_completion_message(archetype: str, streak: int, difficulty: str) -> str:
        """
        Identity-anchored completion message.
        v2: calm, specific, NO exclamation marks.
        """
        base = ARCHETYPE_COMPLETION_MESSAGES.get(
            archetype.lower(),
            ARCHETYPE_COMPLETION_MESSAGES["pioneer"]
        )
        if streak > 0 and streak % 7 == 0:
            return f"{base} {streak} days of consecutive action."
        return base

    @staticmethod
    def calculate_level_up(current_xp: int, current_level: int) -> Dict[str, Any]:
        """
        Determine if XP crosses a level threshold.
        Returns level, whether leveled up, coins earned, and message.
        No random coins — coins only from defined milestones.
        """
        new_level = current_level
        while current_xp >= xp_for_level(new_level + 1):
            new_level += 1

        leveled_up = new_level > current_level
        level_message = None
        coins_awarded = 0

        if leveled_up:
            for level_range, msg in LEVEL_UP_MESSAGES.items():
                if new_level in level_range:
                    level_message = msg
                    break
            coins_awarded = new_level * 5   # small, predictable, not random

        return {
            "level":         new_level,
            "leveled_up":    leveled_up,
            "next_level_xp": xp_for_level(new_level + 1),
            "coins_awarded": coins_awarded if leveled_up else 0,
            "level_message": level_message,
            "xp_progress":   current_xp - xp_for_level(new_level),
            "xp_required":   xp_for_level(new_level + 1) - xp_for_level(new_level),
        }

    @staticmethod
    def check_streak_milestone(streak: int) -> Optional[Dict[str, Any]]:
        """
        Check if this streak count hits a coin milestone.
        Returns milestone data or None.
        Milestones are sparse and meaningful — not every 5 days.
        """
        return COIN_MILESTONES.get(streak)

    @staticmethod
    def get_xp_display_label(archetype: str) -> str:
        """
        v2: XP is always shown alongside identity context.
        Never just a raw number.
        """
        archetype_labels = {
            "warrior":  "Building Warrior identity",
            "monk":     "Advancing Monk practice",
            "builder":  "Compounding Builder discipline",
            "explorer": "Expanding Explorer capacity",
            "pioneer":  "Establishing behavioral baseline",
        }
        return archetype_labels.get(archetype.lower(), "Building behavioral identity")


# Singleton instance
reward_engine = RewardEngine()
