# JanMitra

JanMitra is an Applied AI civic-tech project built for **India Innovates 2026** (World’s Largest Civic Tech Hackathon). The platform aims to help citizens and government teams convert fragmented, fast-moving public information into actionable intelligence — improving awareness, scheme discovery, and issue reporting at scale.

## Links

Demo Link - https://jan-mitra1.vercel.app

Demo Video - https://youtu.be/i6A30mjHDow

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

## Screenshots

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/4f9c1782-54ab-4cf4-9f0b-3772b11990d4" />

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/afe35b55-53d6-44b9-aad6-fed1c1605bb6" />

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/562dee9f-796b-45cb-8a8a-464f7822bbe3" />

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/dd69b71b-0f5c-4d6f-bc88-9905c5adb375" />

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/ece15672-5b58-401f-b483-4bca1493667b" />

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/567511f6-bb4e-4355-b967-171e5647d014" />

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/265b448a-84e4-459f-a6fe-d32686345c44" />

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/1d3f80d7-80c5-4dba-a26a-ffa15fc7d6f1" />

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/d216b0fa-8adf-461b-8245-371c7c68b3d6" />

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/9c38dddd-a8ae-4417-9db6-5edf6b18e908" />

<img width="1918" height="894" alt="image" src="https://github.com/user-attachments/assets/28abd263-f865-4f5e-84e0-2b44431ae03d" />


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



