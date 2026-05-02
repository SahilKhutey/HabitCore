# HabitCore v1.0.0

> **Behavioral Intelligence Platform** — A cross-platform habit-tracking ecosystem built on identity psychology, real-time analytics, and adaptive AI coaching.

---

## What is HabitCore?

HabitCore is not a simple habit tracker. It is a **behavioral intelligence system** designed around three core pillars:

| Pillar | Tab | Purpose |
|---|---|---|
| **Daily Habit Loop** | Today ⚡ | Complete habits with real-time XP, streak, and coin rewards |
| **Life Domain Tracking** | Life ❤️ | Monitor Physical, Mental, Work, Social & Sleep wellness scores |
| **Identity Psychology** | Insights 🧠 | Align behavior to your chosen archetype through ML pattern analysis |

---

## Architecture Overview

```
HabitCore/
├── backend/                   # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/routes/        # REST endpoints
│   │   │   ├── habits.py      # Habit CRUD + completion + state
│   │   │   ├── psychological.py   # Check-ins, life domains, patterns
│   │   │   ├── analytics.py   # Pulse, heatmap, weekly stats
│   │   │   ├── users.py       # Auth, archetype, referrals
│   │   │   ├── gamification.py    # XP, levels, shop
│   │   │   └── avatar_routes.py   # Avatar studio
│   │   ├── core/
│   │   │   └── habit_orchestrator.py  # Central behavioral engine
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── services/          # Business logic layer
│   │   └── main.py            # FastAPI app + CORS
│   └── requirements.txt
│
└── frontend/                  # Expo (React Native + Web)
    ├── app/
    │   ├── (tabs)/
    │   │   ├── index.tsx      # Today — Daily habit loop
    │   │   ├── wellness.tsx   # Life — Wellbeing & domains
    │   │   ├── intelligence.tsx   # Insights — Identity pulse
    │   │   ├── studio.tsx     # Evolve — Avatar & shop
    │   │   ├── profile.tsx    # Profile — Edit, stats, sign out
    │   │   └── coach.tsx      # Coach (hidden, accessible via Insights)
    │   ├── auth/              # Login / Register screens
    │   └── onboarding.tsx     # Archetype selector first-run
    └── src/
        ├── components/        # Reusable UI components
        ├── store/             # Zustand global state
        ├── api/               # API client
        ├── theme/             # Design system tokens
        └── hooks/             # useRewardSystem, useBehaviorTracking
```

---

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| API Framework | FastAPI 0.104+ |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | JWT Bearer tokens (python-jose) |
| AI Layer | Google Gemini via AI Service |
| Scheduling | APScheduler (behavioral nudges) |
| Server | Uvicorn ASGI |

### Frontend
| Layer | Technology |
|---|---|
| Framework | Expo SDK 51 / React Native |
| Navigation | Expo Router (file-based) |
| State | Zustand |
| Animations | Moti + React Native Reanimated |
| Icons | Lucide React Native |
| Fonts | SpaceGrotesk (Google Fonts) |
| Platform | iOS · Android · Web |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

### Frontend
```bash
cd frontend
npm install
npx expo start --web
```

Web app at: **http://localhost:8082**

---

## Core API Endpoints

### Authentication
```
POST /auth/register        Register new user
POST /auth/login           Login → returns JWT token
GET  /users/me             Current user profile
POST /users/set-archetype  Set identity archetype + seed habits
```

### Habits (Daily Loop)
```
GET  /habits/              List user habits
POST /habits/create        Create new habit
POST /habits/complete      Complete a habit (triggers rewards)
GET  /habits/state         Unified dashboard state
GET  /habits/activity      Recent completion feed
POST /habits/seed          Seed starter habits
```

### Psychological Intelligence
```
POST /psychological/checkin          Submit daily check-in (mood/energy/sleep)
GET  /psychological/today-checkin    Check if today's check-in is done
GET  /psychological/checkin/history  7-day mood history for charts
GET  /psychological/life-domains     Life domain scores (Physical/Mental/Work/Social/Sleep)
GET  /psychological/behavior/patterns  ML-derived behavioral patterns
GET  /psychological/daily-challenge  AI-generated daily challenge
```

### Analytics
```
GET  /analytics/pulse        Identity alignment score
GET  /analytics/weekly       7-day completion summary
GET  /analytics/heatmap      90-day activity calendar data
GET  /analytics/recommendations  AI coaching recommendations
```

### Gamification
```
GET  /gamification/shop      Shop inventory (Themes/Powerups/Boosters)
POST /gamification/purchase  Purchase a shop item
GET  /gamification/inventory User's owned items
```

---

## User Journey (v1.0.0)

### First Run
1. Register → Auto-routed to **Archetype Selector**
2. Choose identity: `Warrior` · `Monk` · `Builder` · `Explorer`
3. 3 starter habits seeded matching chosen archetype
4. Land on **Today** tab with habits ready to complete

### Daily Loop
1. **Today tab** → Morning Check-In banner prompts daily pulse (mood/energy/sleep)
2. Complete habits → XP burst + coin fly animations + streak update
3. Daily goal progress bar fills toward XP reward
4. **Life tab** → Life domain bars update from completions
5. **Insights tab** → Identity alignment % recalculates

### Weekly Growth
- **Life Domains** computed from 7-day habit completion rates
- **Behavioral patterns** surface best completion times, burnout risk
- **AI recommendations** personalize coaching based on patterns
- **Archetype** can be changed anytime from Insights or Profile

---

## Environment Configuration

### Backend `.env`
```env
SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///./habithero.db
GEMINI_API_KEY=your-gemini-api-key
ENVIRONMENT=development
```

### Frontend API URL
Edit `frontend/src/api/client.ts`:
```ts
const BASE_URL = 'http://localhost:8000';
```

For production, update to your deployed backend URL.

---

## Data Models

### User
| Field | Type | Description |
|---|---|---|
| `archetype` | str | warrior / monk / builder / explorer |
| `identity_goal` | str | Fit / Calm / Productive / Learner |
| `level` | int | Gamification level (starts at 1) |
| `xp` | int | Cumulative XP earned |
| `coins` | int | Currency for shop purchases |

### Habit
| Field | Type | Description |
|---|---|---|
| `name` | str | Habit display name |
| `difficulty` | str | easy / medium / hard |
| `time` | str | Suggested time (HH:MM) |

### DailyCheckin
| Field | Type | Description |
|---|---|---|
| `mood` | str | happy / excited / neutral / tired / sad / angry |
| `energy_morning` | str | high / medium / low |
| `sleep_quality` | int | 1–5 scale |
| `reflection` | str | Optional free-text |

---

## Design System

### Color Palette
| Token | Value | Usage |
|---|---|---|
| `COLORS.primary` | `#33ffd6` | CTAs, active states, progress |
| `COLORS.secondary` | `#a78bfa` | AI elements, insights |
| `COLORS.gold` | `#fbbf24` | Coins, rewards, warnings |
| `COLORS.background` | `#050d1a` | App background |
| `COLORS.surface` | `#0d1f35` | Card backgrounds |

### Typography
All text uses **SpaceGrotesk** (Google Fonts):
- `SpaceGrotesk_700Bold` — headings, values
- `SpaceGrotesk_600SemiBold` — labels, titles
- `SpaceGrotesk_500Medium` — body, descriptions

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

Or run the endpoint verification script:
```bash
python test_all_endpoints.py
```

---

## Known Limitations (v1.0.0)

- SQLite used for development; migrate to PostgreSQL for production
- Push notifications require native Expo build (not available on web)
- AI coaching requires a valid `GEMINI_API_KEY` in `.env`
- Life domain auto-tagging uses keyword matching (not ML classification)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ — HabitCore v1.0.0 — May 2026*
