# HabitHero Backend 🧬

Production-grade, FastAPI-powered behavioral intelligence engine.

## 🏗️ Architecture: Deep Modules

HabitHero follows the "Deep Module" philosophy: **Small interfaces, rich behavior.**

### Core Orchestrators
- **`IdentityOrchestrator`**: Unified auth (Email, Social) with built-in rate limiting and session management.
- **`HabitEngine`**: Central lifecycle manager for completion, streaks, and adaptive difficulty.
- **`UserGuardian`**: Proactive user health monitoring (burnout detection, churn risk).
- **`HeroService`**: Premium gamification, milestone evaluation, and global leaderboards.
- **`PaymentOrchestrator`**: Stripe-integrated monetization loop.

## 🧪 Testing (TDD First)
All core orchestrators are verified using integration tests in `app/tests/`.
- `pytest` with `sqlite:///:memory:` for sub-second execution.
- High-coverage of social auth and payment webhook fulfillment.

## 🚀 Deployment
- **CI/CD**: Configured via `.github/workflows/ci.yml`.
- **Environment**: Requires `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, and `JWT_SECRET`.

---
Built with a focus on locality and AI-navigability.
