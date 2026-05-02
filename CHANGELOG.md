# Changelog

All notable changes to HabitCore are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-05-02

### 🚀 Initial Production Release

This is the first stable release of HabitCore — a full-stack behavioral intelligence platform.

---

### Added — Frontend

#### Navigation
- **5-tab architecture**: Today ⚡ · Life ❤️ · Insights 🧠 · Evolve ✨ · Profile 👤
- Replaced legacy 4-tab layout with identity-driven user journey structure
- Tab icons: Zap, Heart, Brain, Sparkles, User (Lucide)

#### Today Tab (`index.tsx`)
- **Morning Check-In banner** — pink pulse card prompts daily mood logging; auto-hides after completion
- **ArchetypeSelector first-run gate** — modal triggers for new users with no archetype set; presents 4 identity cards
- **Quick-add habit grid** — 6 one-tap habit categories (Meditation, Deep Work, Exercise, Reading, Journaling, Sleep) for friction-free first habit creation
- Habit completion cards with difficulty badges and XP display
- Daily goal progress bar with animated fill

#### Life Tab (`wellness.tsx`) — *new screen*
- **Today's Pulse card** — shows check-in status with mood emoji, energy level, and sleep quality inline
- **Life Score** — computed 0–100 wellness score with animated progress bar
- **5 Life Domains** — Physical 💪 / Mental 🧠 / Work 💼 / Social 💞 / Sleep 😴 each with pixel-animated progress bar and color-coded percentage
- **7-Day Mood Trend** — `MoodChart` component renders bar chart from check-in history
- **Restoration Strategies** — 3 actionable cards: Neural Reset, Dopamine Detox, Recovery Protocol with interactive toasts
- Full pull-to-refresh support with backend re-sync

#### Insights Tab (`intelligence.tsx`) — *rebuilt*
- **Identity Pulse card** — flat layout with large 64px `%` number, animated alignment bar, 3 chip stats (Completions / Burnout Risk / This Week); removed broken floating SVG ring overlay
- **Archetype change sheet** — bottom sheet with 4 archetype cards; live API call to update identity
- **Daily Check-In prompt** — surfaces if no check-in done today (disappears after completion)
- **Weekly Stats** — 3 boxes: This Week count, Success Rate %, Burnout level with color-coded border
- **Behavioral Story** — best completion day, strongest habit, improvement area, coach tip
- **Activity Calendar** — 90-day heatmap via `HabitHeatmap` component
- **Pattern Recognition** — ML-derived patterns (best time of day, habit correlations)
- **AI Optimization** — 3 coaching insights derived from recent check-in and behavioral data

#### Profile Tab (`profile.tsx`) — *fully rebuilt*
- **Editable display name** — tap pencil icon → inline `TextInput` with ✓ / ✕ confirmation
- **Archetype badge** — tappable; opens bottom sheet with all 5 archetypes + current selection checkmark + descriptions
- **Dynamic avatar ring** — border color matches current archetype color
- **XP Progress bar** — shows Level N, current/next XP, coin count
- **Stats grid** — Streak / Total XP / Completed habits
- **PREFERENCES section** — settings rows: Identity Archetype (→ opens archetype sheet), Notifications, Dark Mode, Privacy & Data
- **Activity feed** — recent habit completions with difficulty color coding and relative timestamps
- **Sign Out button** — red bordered button with `Alert.alert` confirmation dialog
- **Toast notifications** — animated success feedback for all actions
- Archetype selector bottom sheet with emoji, name, description per archetype

#### New Components
- `ArchetypeSelector.tsx` — 4-card identity selector used in first-run onboarding and Today tab gate
- `MoodChart.tsx` — 7-day animated bar chart, calendar-aligned, with mood emoji labels and legend
- `HabitHeader.tsx` — XP bar with level, streak, coins display reused across Today and Profile
- `HabitHeatmap.tsx` — 90-day activity calendar grid with intensity color coding
- `AddHabitModal.tsx` — slide-up habit creation form with category chips and quick-add grid

---

### Added — Backend

#### New Endpoints

**`GET /psychological/life-domains`**
- Computes 5 life domain scores (Physical, Mental, Work, Social, Sleep) from past 7-day habit completions and check-in history
- Uses keyword-based `classify_habit_domain()` to tag habits to domains
- Returns `{ domains: [...], overall_score: float }`

**`GET /psychological/checkin/history?days=7`**
- Returns last N days of daily check-ins for the mood trend chart
- Returns `{ checkins: [...], total: int }`

**`GET /psychological/today-checkin`**
- Fast boolean check: has the user already submitted a check-in today?
- Returns `{ done: bool, checkin: object | null }`

**`POST /users/set-archetype`**
- Sets user's `archetype` column and derives matching `identity_goal`
- Optional `seed_habits: bool` flag auto-creates 3 archetype-matched starter habits
- Returns `{ status, archetype, identity_goal, habits_seeded }`

#### Updated Endpoints
- **`GET /habits/state`** — now includes `archetype`, `daily_habit_goal` in `user_state` response; used by frontend for first-run gate detection

---

### Changed

- **Tab navigation** — renamed from (Dashboard / Intelligence / Wellness / Studio / Profile) to (Today / Life / Insights / Evolve / Profile)
- **`useUserStore`** — added `identityGoal` field alongside `identity_goal` for consistency with new screens
- **`wellness.tsx` animations** — replaced `as any` percentage-string widths (crashed on web) with pixel-computed widths using `useWindowDimensions`
- **`MoodChart.tsx` animations** — replaced `height: '80%' as any` with pixel-calculated height (80px track × ratio)
- **`intelligence.tsx`** — removed `XPProgressRing` import and SVG ring overlay; replaced with flat stat layout

---

### Fixed

- **Insights screen overlay bug** — `XPProgressRing` SVG was absolutely positioned inside an unconstrained `ringWrapper`, causing it to float over adjacent content; removed entirely and replaced with clean flat card design
- **Animated width/height crash on web** — Moti/Reanimated does not support string percentage values in `animate` props on web platform; all percentage-based animated dimensions converted to pixel values
- **Profile screen no-edit state** — Profile had no way to change name, archetype, or settings; fully rebuilt with editable fields
- **Duplicate `});` in `index.tsx`** — removed extra closing brace from `StyleSheet.create` block
- **`_layout.tsx` stale tab config** — `coach` tab was previously visible; now hidden (`href: null`)

---

### Infrastructure

#### Project Structure Cleanup
- Removed deprecated screen files: `App.tsx`, `two.tsx`, legacy `src/screens/` directory
- Removed redundant service files: `adaptive_service.py`, `ai_coach_service.py`, `challenge_service.py`, `churn_service.py`, `coach_service.py`, `habit_engine.py`, `habit_service.py`, `cached_ai_service.py`, `protection_service.py`, `rule_service.py`, `notification_service.py`
- Removed unused route: `habit_routes.py`

#### Test Files Added
- `backend/test_all_endpoints.py` — comprehensive endpoint verification script
- `backend/test_new_endpoints.py` — targeted tests for psychological + archetype endpoints
- `backend/tests/test_avatar_evolution.py` — avatar progression tests

---

### Known Limitations

- SQLite used in development; production should use PostgreSQL
- Push notifications require a native Expo build (not web)
- AI coaching requires `GEMINI_API_KEY` in backend `.env`
- Life domain classification uses keyword matching, not ML classification
- `Evolve` tab (avatar studio) UI polish deferred to v1.1.0

---

## [Unreleased] — Upcoming in v1.1.0

- Evolve tab full avatar progression system
- Push notification scheduling via APScheduler
- Social habit challenges (multi-user)
- PostgreSQL migration guide
- Onboarding tutorial overlay

---

*HabitCore — Behavioral Intelligence Platform*
