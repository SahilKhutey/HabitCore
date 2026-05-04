"""
ConfigEngine — v2 Live Ops Layer

Dynamic configuration system. No redeployment needed.
Config values stored in DB and cached in memory.

Controls:
  - XP multipliers (event-based)
  - Reward frequency
  - Feature flags (A/B testing gates)
  - AI temperature and verbosity
  - Notification frequency overrides
  - Recovery mode global toggle

Architecture:
  ConfigEngine reads from config_settings table (or falls back to defaults).
  All layer services query ConfigEngine before applying their logic.
  Example: RewardEngine checks config["xp_multiplier"] before returning XP.
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone


# ── Default Configuration (production-safe) ──────────────────────────────────

DEFAULT_CONFIG: Dict[str, Any] = {
    # Reward layer
    "xp_multiplier":           1.0,    # float: 1.0 = normal, 1.5 = event bonus
    "coin_multiplier":         1.0,
    "reward_frequency":        "normal",  # "minimal" | "normal" | "elevated"

    # Insight engine
    "insight_dedup_days":      3,      # days before same insight re-surfaces
    "max_insights_per_feed":   10,
    "insight_generation_enabled": True,

    # AI coach
    "ai_enabled":              True,
    "ai_max_tokens":           150,
    "ai_cache_hours":          4,

    # State engine
    "burnout_threshold":       0.60,   # v2 lowered from 0.70
    "recovery_clear_threshold": 0.30,

    # Gamification controls
    "streak_pressure_enabled": True,   # disabled globally in burnout events
    "gamification_tone":       "calm", # "calm" | "energetic"

    # Feature flags
    "features": {
        "ai_coach":             True,
        "behavioral_insights":  True,
        "prediction_engine":    False,  # v2.1
        "social_layer":         False,  # v2.2
        "experimentation":      False,  # v2.1
    },

    # Live event
    "event_active":            False,
    "event_name":              None,
    "event_end_date":          None,

    # System
    "maintenance_mode":        False,
    "updated_at":              datetime.now(timezone.utc).isoformat(),
}


class ConfigEngine:
    """
    In-memory config cache with DB persistence.
    Falls back to DEFAULT_CONFIG if DB unavailable.

    Usage:
        config = ConfigEngine()
        xp_mult = config.get("xp_multiplier", 1.0)
        if config.feature("ai_coach"):
            ...
    """

    _instance: Optional["ConfigEngine"] = None
    _cache: Dict[str, Any] = {}
    _loaded_at: Optional[datetime] = None
    CACHE_TTL_MINUTES = 5

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = dict(DEFAULT_CONFIG)
        return cls._instance

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value by key. Returns default if not found."""
        return self._cache.get(key, default)

    def feature(self, flag: str) -> bool:
        """Check if a feature flag is enabled."""
        features = self._cache.get("features", {})
        return bool(features.get(flag, False))

    def get_all(self) -> Dict[str, Any]:
        """Return full config snapshot. Used by admin endpoints."""
        return dict(self._cache)

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update config values in memory (and optionally persist to DB).
        Only keys present in DEFAULT_CONFIG can be updated (safety guard).
        """
        for key, value in updates.items():
            if key in DEFAULT_CONFIG:
                if key == "features" and isinstance(value, dict):
                    self._cache["features"].update(value)
                else:
                    self._cache[key] = value
        self._cache["updated_at"] = datetime.now(timezone.utc).isoformat()

    def reload_from_db(self, db) -> None:
        """
        Reload config from database ConfigSetting model.
        Called on startup and every CACHE_TTL_MINUTES.
        If DB has no config, defaults are used.
        """
        now = datetime.now(timezone.utc)
        if (
            self._loaded_at
            and (now - self._loaded_at) < timedelta(minutes=self.CACHE_TTL_MINUTES)
        ):
            return

        try:
            from app.models.config_setting import ConfigSetting
            rows = db.query(ConfigSetting).all()
            for row in rows:
                try:
                    self._cache[row.key] = json.loads(row.value)
                except (json.JSONDecodeError, TypeError):
                    self._cache[row.key] = row.value
            self._loaded_at = now
        except Exception as e:
            print(f"[ConfigEngine] DB reload failed, using defaults: {e}")
            self._loaded_at = now

    def is_maintenance(self) -> bool:
        return bool(self._cache.get("maintenance_mode", False))


# Singleton
config_engine = ConfigEngine()
