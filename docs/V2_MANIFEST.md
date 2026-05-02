# HabitCore V2.0 Component Manifest

This manifest tracks all new services and files introduced in the Intelligence Pipeline (V2) update.

## 1. Streaming & Infrastructure
| Service | Path | Role |
| :--- | :--- | :--- |
| **Kafka Broker** | `docker-compose.yml` | Real-time event bus |
| **Flink Job** | `streaming/flink/jobs/flink_job.py` | Stateful pattern detection |
| **Producer** | `streaming/producer.py` | Event ingestion entry point |
| **Consumer (DB/Redis)** | `streaming/event_consumer.py` | Syncing events to persistence |

## 2. Real-Time Memory (Redis)
| Component | Path | Role |
| :--- | :--- | :--- |
| **Context Manager** | `app/services/context_store/manager.py` | Redis orchestration |
| **Redis Store** | `docker-compose.yml` | High-speed feature store |

## 3. Intervention Engine
| Component | Path | Role |
| :--- | :--- | :--- |
| **Nudge Engine** | `nudge_engine/app/main.py` | Real-time intervention service |
| **Decision Logic** | `nudge_engine/app/decision.py` | Priority scoring & cooldowns |
| **Templates** | `nudge_engine/app/templates.py` | Behavioral nudge variants |

## 4. Real-Time API
| Component | Path | Role |
| :--- | :--- | :--- |
| **Real-Time Engine** | `realtime_engine/app/main.py` | Instant feature access |
| **Context Service** | `realtime_engine/app/context_service.py` | Sliding window management |

## 5. NLP & Intelligence
| Component | Path | Role |
| :--- | :--- | :--- |
| **NLP Microservice** | `nlp_service/app/main.py` | Cognitive signal extraction |
| **Answer Intel** | `backend/app/services/reflection_engine/answer_intelligence.py` | Text-to-signal logic |

## 6. Updated Data Models
| File | Changes |
| :--- | :--- |
| `intelligence_models.py` | Added `CognitiveSignal`, `Nudge`, `NudgeFeedback` |
| `routes.py` | Integrated async Kafka streaming in `/respond` |
