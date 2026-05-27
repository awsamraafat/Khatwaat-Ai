# Adaptive AI Assessment Platform
## Production-Level Architecture Documentation

# 1. SYSTEM OVERVIEW

## Project Goal
Build a scalable AI-powered adaptive assessment platform using:
- IRT (Item Response Theory)
- CAT (Computerized Adaptive Testing)
- AI Recommendation Engine
- Anti-Cheat AI
- Real-Time Analytics

The platform must support:
- Personalized adaptive exams
- AI-based ability estimation
- Track/career prediction
- Student analytics
- Academic recommendation systems
- Anti-cheating detection

---

# 2. HIGH LEVEL ARCHITECTURE

```text
                    ┌────────────────────┐
                    │   Google Sheets    │
                    │ Question Dataset   │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Data Processing AI │
                    │ Cleaning/Validation│
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │   Question Bank    │
                    └─────────┬──────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
 ┌──────────────┐    ┌──────────────┐    ┌────────────────┐
 │ IRT Engine   │    │ CAT Engine   │    │ Session Engine │
 └──────┬───────┘    └──────┬───────┘    └────────┬───────┘
        │                   │                     │
        └───────────────────┼─────────────────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Student Analytics AI │
                 └──────────┬───────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
 ┌──────────────┐  ┌────────────────┐  ┌────────────────┐
 │Recommendations│ │Track Classify  │ │ Anti-Cheat AI │
 └──────────────┘  └────────────────┘  └────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Dashboards & Reports │
                 └──────────────────────┘
```

---

# 3. TECH STACK

## Frontend
- Next.js
- TypeScript
- TailwindCSS
- Framer Motion

## Backend
- Supabase Edge Functions
- FastAPI (optional AI microservice)

## Database
- Supabase PostgreSQL

## Authentication
- Supabase Auth
- JWT

## AI/ML
- Python
- scikit-learn
- PyTorch
- NumPy
- pandas

## Realtime
- Supabase Realtime
- WebSockets

## Deployment
- Vercel
- Supabase
- Docker
- AWS (optional)

---

# 4. DATABASE DESIGN (SUPABASE)

## Tables
- users
- subjects
- questions
- exams
- exam_sessions
- answers
- analytics
- recommendations
- anti_cheat_logs

---

# 5. FOLDER STRUCTURE

```text
adaptive-ai-platform/

├── apps/
│   ├── web/
│   ├── admin/
│   └── ai-services/
│
├── packages/
│   ├── ui/
│   ├── shared/
│   └── configs/
│
├── ai/
│   ├── irt/
│   ├── cat/
│   ├── recommendations/
│   ├── anti_cheat/
│   ├── analytics/
│   └── preprocessing/
│
├── supabase/
│   ├── migrations/
│   ├── functions/
│   └── seed/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   └── diagrams/
│
├── docker/
│
└── scripts/
```

---

# 6. IRT ENGINE DESIGN

## Goal
Estimate student ability (θ) using probabilistic models.

## Supported Models
- 2PL
- 3PL

## Parameters
- Difficulty (b)
- Discrimination (a)
- Guessing (c)

## Formula

```text
P(θ) = c + (1 - c) / (1 + e^(-a(θ - b)))
```

---

# 7. CAT ENGINE DESIGN

## Goal
Adaptive question selection.

## Logic
- Correct answer → harder question
- Wrong answer → easier question

## Features
- stopping criteria
- confidence estimation
- question exposure control

---

# 8. ANTI-CHEAT AI

## Features
- tab switching detection
- copy/paste detection
- fullscreen monitoring
- abnormal timing detection
- answer similarity detection
- webcam monitoring (optional)

---

# 9. TRACK CLASSIFICATION ENGINE

## Tracks
1. Engineering & Computer Science
2. Medicine & Life Sciences
3. Business
4. Arts & Humanities

---

# 10. RECOMMENDATION ENGINE

## Short-Term Recommendations
- Frontend
- Backend
- AI
- Cybersecurity
- Data Science
- Mobile Development

## Long-Term Recommendations
- Computer Science
- Engineering
- Business
- Medicine
- Arts

---

# 11. ANALYTICS ENGINE

## Student Analytics
- strengths
- weaknesses
- progress
- speed
- accuracy

## Admin Analytics
- cheating alerts
- hardest questions
- easiest questions
- rankings

---

# 12. FRONTEND PAGES

## Student
- /dashboard
- /exams
- /analytics
- /recommendations

## Admin
- /admin
- /admin/students
- /admin/questions
- /admin/analytics

---

# 13. API DESIGN

## Auth
- POST /auth/login
- POST /auth/register

## Exam
- GET /exam/start
- POST /exam/answer
- GET /exam/result

## Analytics
- GET /analytics/student
- GET /analytics/admin

---

# 14. REALTIME SYSTEM

Use:
- Supabase Realtime
- WebSockets

For:
- live timers
- anti-cheat events
- live analytics

---

# 15. SECURITY

- JWT authentication
- RLS policies
- encrypted secrets
- audit logging
- rate limiting

---

# 16. DOCKER SETUP

```yaml
services:
  web:
  ai-service:
  supabase:
```

---

# 17. DEPLOYMENT

## Frontend
- Vercel

## Backend
- Supabase Edge Functions

## AI Services
- Railway / AWS

## Database
- Supabase PostgreSQL

---

# 18. DEVELOPMENT ROADMAP

## Phase 1
- authentication
- question bank
- basic exams

## Phase 2
- IRT
- CAT
- adaptive exams

## Phase 3
- recommendation engine
- track classification
- analytics

## Phase 4
- anti-cheat AI
- anomaly detection

## Phase 5
- scalability optimization

---

# 19. SCALABILITY

## Principles
- modular architecture
- isolated AI services
- horizontal scaling

## Optimization
- Redis caching
- async workers
- queue systems

---

# 20. FUTURE IMPROVEMENTS

- Bayesian IRT
- RL-based CAT
- AI-generated questions
- AI tutoring assistant
- personalized learning paths

---

# 21. SUCCESS CRITERIA

- unique adaptive exams
- reliable theta estimation
- working recommendations
- accurate anti-cheat system
- scalable university-level architecture
