# HabitCore Intelligence Pipeline (Version 2.0)

## Overview
Version 2.0 transforms HabitCore from a static tracking application into a **Reactive Behavioral Intelligence Ecosystem**. It introduces real-time event streaming, stateful behavioral analysis, and autonomous intervention capabilities.

## Key Architectural Upgrades

### 1. Real-Time Streaming Infrastructure (Kafka)
- **Purpose**: Decouples heavy NLP and behavioral analysis from the core API.
- **Components**: 
  - `behavioral_events`: High-throughput topic for raw behavioral signals.
  - `patterns_stream`: Topic for high-confidence detected behavioral loops.
  - `user_text_events`: Topic for raw user reflection text.

### 2. Stateful Pattern Engine (Apache Flink)
- **Purpose**: Detects complex behavioral patterns that unfold over time.
- **Capabilities**:
  - **Sliding Windows**: Tracks rolling distraction and focus metrics.
  - **Stateful Detection**: Identifies "Avoidance Cycles" by tracking user state across multiple consecutive events.

### 3. Behavioral Context Store (Redis)
- **Purpose**: Sub-millisecond behavioral memory for the intervention layer.
- **Features**:
  - **Online Feature Store**: Maintains a "live" profile of user metrics (focus, distraction).
  - **Behavior Flags**: Instant boolean signals for the decision engine.
  - **Anti-Spam Protocol**: Redis-based cooldowns to prevent notification fatigue.

### 4. Reactive Nudge Engine (FastAPI)
- **Purpose**: Autonomous decision-making and delivery of interventions.
- **Logic**: 
  - **Priority Scoring**: Context-aware selection of the most impactful nudge.
  - **Intervention Types**: Interrupt, Redirect, Reflective, and Reinforcement.

### 5. Answer Intelligence (NLP Service)
- **Purpose**: Extracting structured cognitive signals from messy human text.
- **Output**: Detects emotions, cognitive distortions, and behavioral intents.

## Deployment Stack
Version 2.0 is fully containerized via `docker-compose.yml`:
- **Kafka / Zookeeper**: Event backbone.
- **Flink (Job/Task Manager)**: Stream processing.
- **Redis**: Real-time memory.
- **Nudge Engine**: Intervention service.
- **Real-Time Engine**: Feature store API.

---
*Note: Version 1.0 architecture (Static CRUD & Basic Analytics) remains supported as the foundation for these real-time layers.*
