# JanMitra

JanMitra is an Applied AI civic-tech project built for **India Innovates 2026** (World’s Largest Civic Tech Hackathon). The platform aims to help citizens and government teams convert fragmented, fast-moving public information into actionable intelligence — improving awareness, scheme discovery, and issue reporting at scale.

## Links

## Problem / Domain
This repository aligns with the **Digital Democracy / Smart Public Service** direction, focusing on:
- citizen grievances & reporting
- fact-checking and trusted information delivery
- scheme matching and personalized advisories
- decision support dashboards for governance

## What we built
JanMitra provides two experiences: **Citizen** and **Government**.

### Citizen App
- Registration/Login + onboarding
- Personalized dashboard
- Alerts & advisories
- Scheme navigator (real schemes dataset)
- Fact checker
- Issue/report submission and tracking
- AI chatbot (multiple modes)

### Government Dashboard
- Command center dashboard
- Predictions list + detail pages
- Citizen reports dashboard
- Analytics & insights
- Real-time stats
- Dark theme

## Core AI / Intelligence capabilities
- Collects articles from **20+ sources**
- AI processing (Groq-based pipeline in current implementation)
- Entity extraction
- Knowledge-graph construction
- Crisis prediction / early warning logic
- Fact-checking flow
- Scheme matching (currently **15 schemes**)
- Location/occupation-based alert generation
- Auto-verification of citizen reports

## Tech stack (high level)
- **Backend:** Flask API, SQLAlchemy ORM, JWT auth, migrations, scheduled jobs
- **Frontend:** Web UI for Citizen + Government experiences
- **Data/Automation:** hourly data collection + trend computation

## Repository structure
```
.
├── backend/
├── frontend/
├── README.md
├── WHATSAPP_BOT_SETUP.md
└── FRONTEND_WHATSAPP_INTEGRATION.md
```

## Current progress snapshot
- 100+ articles auto-collected
- 30+ entities extracted
- 70+ relationships mapped
- 15 government schemes loaded

## Roadmap (India Innovates 2026 readiness)
These are the key upgrades planned before the finale.

### High priority
- Email notifications (alerts, password reset, weekly digest)
- SMS alerts for critical notifications
- Real-time map visualization (heatmaps, issue layers; Leaflet/Mapbox)

### Medium priority
- Advanced analytics (time-series, accuracy tracking, response effectiveness)
- Admin panel (moderation, configuration)

### Low priority
- Performance optimization (Redis, CDN, indexes)
- Security hardening (rate limiting, CAPTCHA, 2FA)
- Testing + CI/CD

## Team

Sourav Kumar

Sarvesh Shahane

Rahul

Abhishek Gupta

---

**Note:** This repository is being prepared for submission and demo at India Innovates 2026.

