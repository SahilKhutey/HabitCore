# HabitHero Domain Glossary

## Core Concepts

- **Habit** — A recurring task a user wants to perform (e.g., "Drink Water", "Code").
- **Habit Log** — A record of a completed habit on a specific date.
- **Streak** — The number of consecutive days a habit has been completed.
- **Streak Freeze** — An item that protects a streak when a day is missed.
- **Burnout** — A state of low engagement or inconsistency detected by the system.
- **Gamification** — The system of rewards (XP, Levels, Coins) for consistency.

## Architectural Seams

- **Habit Engine** — The core module responsible for the lifecycle of habit completion and progression.
- **User Guardian** — The protection layer that monitors for burnout and manages retention insurance.
- **Identity Orchestrator** — The unified authentication layer for cross-platform identity management.
