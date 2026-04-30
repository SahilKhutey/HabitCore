# HabitCore 🧬

**The Elite "Habit-First" Behavioral Ecosystem**

HabitCore is a production-grade, high-performance habit tracking platform designed to prioritize momentum and long-term consistency. Built with a "Habit-First" philosophy, it strips away gamification clutter to focus on what matters: **frictionless completion and behavioral growth.**

## 🚀 Key Features

### 🧠 The Intelligence Layer
- **Smart Reminders**: Dynamically calculates the optimal notification time based on your historical completion patterns.
- **Adaptive Difficulty Scaling**: A self-adjusting "Coach" system that suggests leveling up when you're consistent or scaling back to prevent burnout.
- **Behavioral Insights**: Smart analysis of your routine (e.g., "You perform best at night") provided as actionable feedback.

### 🔥 Momentum-First UX
- **1-Tap Completion**: Zero-friction habit logging with satisfying haptic feedback and bounce animations.
- **Micro-Reward Loop**: Non-intrusive Floating XP system for immediate positive reinforcement without distracting from the task.
- **Visual Memory**: GitHub-style consistency grids and yearly heatmaps to visualize your long-term transformation.

### 📈 Retention & Growth
- **Robust Streak Engine**: Handles edge cases (late-night usage, missed days) to keep your momentum alive.
- **Viral Share Loop**: Integrated social sharing to celebrate streaks and drive community growth.
- **Global Leaderboard**: Competitive weekly rankings based on total habit completions.

## 🛠️ Technology Stack

### Frontend (React Native + Expo)
- **State Management**: Zustand (`useUserStore`) for global profile and preferences.
- **Data Fetching**: TanStack Query (React Query) for robust server-side synchronization.
- **Animations**: React Native Reanimated for high-performance, fluid UI interactions.
- **Notifications**: Expo Notifications for the smart reminder system.
- **Icons**: Lucide-React-Native for a clean, professional aesthetic.

### Backend (FastAPI + SQLAlchemy)
- **Database**: SQL-driven logic for complex analytics and completion logging.
- **Authentication**: Secure JWT-based auth with user-specific data isolation.
- **Analytics Engine**: Advanced algorithms for streak calculation, completion rates, and smart-time detection.
- **Task Scheduling**: Integrated scheduler for daily resets and notification triggers.

## 📦 Getting Started

### Prerequisites
- Node.js & npm
- Python 3.9+
- Expo CLI

### Frontend Setup
1. `cd frontend`
2. `npm install`
3. `npx expo start`

### Backend Setup
1. `cd backend`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload`

## 🎨 Design Philosophy
- **Dark Mode Default**: Sleek `#000` background with vibrant `#00ffcc` accents.
- **High Clarity**: Minimal text, high-impact iconography.
- **Frictionless**: Every primary action is reachable within a single tap.

---

Built by **Antigravity** with a focus on Behavioral Science and Elite Engineering.
