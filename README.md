# JanMitra

JanMitra is an Applied AI civic-tech project built for **India Innovates 2026** (World’s Largest Civic Tech Hackathon). The platform aims to help citizens and government teams convert fragmented, fast-moving public information into actionable intelligence — improving awareness, scheme discovery, and issue reporting at scale.

> **Event:** India Innovates 2026
> **Organizer / Track:** Hackathons (Applied AI)
> **Host Organization:** Municipal Corporation of Delhi (MCD)
> **Finale Venue:** Bharat Mandapam, New Delhi, Delhi, India
> **Team Size:** 3–6

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
- 250+ articles auto-collected
- 30+ entities extracted
- 70+ relationships mapped
- 15 government schemes loaded

## Roadmap (India Innovates 2026 readiness)
These are the key upgrades planned before the finale.

### High priority
- Photo upload in citizen reports (backend upload endpoint + frontend image picker + storage)
- WhatsApp bot integration (webhooks, automated fact-check responses, alert forwarding)
- Email notifications (alerts, password reset, weekly digest)
- SMS alerts for critical notifications
- Real-time map visualization (heatmaps, issue layers; Leaflet/Mapbox)

### Medium priority
- Advanced analytics (time-series, accuracy tracking, response effectiveness)
- Export reports (PDF/CSV/Excel)
- Multilingual support (Hindi + regional languages)
- Mobile app (React Native)
- Admin panel (moderation, configuration)
- Search & filters + saved searches
- Social sharing

### Low priority
- Voice input
- Gamification
- Public API docs (Swagger/OpenAPI)
- Performance optimization (Redis, CDN, indexes)
- Security hardening (rate limiting, CAPTCHA, 2FA)
- Testing + CI/CD

## India Innovates 2026 — stages & timeline
All dates below are **2026** (IST).

- **Round 1 – PPT Submission:** 24 Jan, 05:21 PM → 10 Mar, 11:59 PM
  - Submit PPT/PDF in format: `TeamName_DomainName.ppt` or `.pdf`
  - Not an elimination round; best solutions may receive exhibition space
- **Evaluation:** 11 Mar, 12:00 AM → 15 Mar, 11:59 PM
- **Grand Finale (Live Showcase):** 28 Mar, 09:00 AM → 11:59 PM
  - Venue: Bharat Mandapam, New Delhi
  - Expo timings: 9:00 AM – 7:00 PM

## Prizes
Total prize pool: **₹10,05,000** (as listed in the challenge).

## How to run (local)
> Add detailed run instructions here (backend + frontend) once finalized.

## Team
Add team member names + roles here.

## Links
- Unstop challenge page: (add link)
- Official WhatsApp community: https://chat.whatsapp.com/Lrfd4LgqOScGkotc8HkDQ8
- Instagram: https://www.instagram.com/indiainnovates2026

---

**Note:** This repository is being prepared for submission and demo at India Innovates 2026.
