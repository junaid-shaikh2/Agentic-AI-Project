# 🌍 VoyageAgent

### Multi-Agent AI Travel Planner Powered by MCP Tools

> **Plan smarter. Travel better. Adapt instantly.**
>
> VoyageAgent is an intelligent multi-agent travel planning system that combines real-time weather, local events, attractions, budgeting, travel advisories, and automated notifications into a single AI-powered travel experience.

---

## ✨ Why VoyageAgent?

Traditional travel planners generate static itineraries.

**VoyageAgent creates living travel plans.**

Instead of relying on a single AI workflow, VoyageAgent uses a team of specialized agents that collaborate to:

* Understand destination context
* Analyze weather conditions
* Discover local attractions and events
* Optimize spending
* Personalize activities
* Monitor travel risks
* Send proactive travel updates

The result is a travel itinerary that feels like it was prepared by an entire travel agency rather than a single application.

---

# 🧠 Multi-Agent Architecture

```text
                    ┌─────────────────┐
                    │   User Request  │
                    └────────┬────────┘
                             │
                             ▼
                 ┌─────────────────────┐
                 │   Voyage Orchestrator │
                 └────────┬────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼

 ┌────────────┐   ┌────────────┐   ┌──────────────┐
 │ Context    │   │ Planner    │   │ Experience   │
 │ Agent      │   │ Agent      │   │ Agent        │
 └─────┬──────┘   └─────┬──────┘   └─────┬────────┘
       │                │                │
       ▼                ▼                ▼

 Weather        Day-by-Day Plan    Personalized
 Events         Route Building     Recommendations
 Places          Scheduling        Weather Awareness

        ┌─────────────────┐
        ▼                 ▼

 ┌────────────┐   ┌─────────────────┐
 │ Budget     │   │ Notification    │
 │ Agent      │   │ Agent           │
 └────────────┘   └─────────────────┘

 Cost Optimization   Email Alerts
 Budget Enforcement  Travel Warnings
```

---

# 🚀 Core Capabilities

## 🌦 Context Agent

Collects real-world travel intelligence using MCP tools.

### Data Sources

* Weather forecasts
* Local events
* Tourist attractions
* Restaurants
* Museums
* Landmarks
* Travel advisories

### Purpose

Before planning begins, VoyageAgent understands what's happening in the destination city.

---

## 🗺 Planner Agent

Generates the complete itinerary.

### Responsibilities

* Day-by-day planning
* Attraction sequencing
* Activity distribution
* Trip structure optimization

Every generated plan is tailored specifically to the selected destination and travel dates.

---

## 🎯 Experience Agent

Adds personalization and context awareness.

### Enhancements

* Weather-aware suggestions
* Preference-based recommendations
* Activity tips
* Local experience improvements

Example:

Instead of simply recommending a park visit, the agent can suggest indoor alternatives when rain is expected.

---

## 💰 Budget Agent

Keeps travel costs realistic.

### Cost Categories

| Category   | Included                |
| ---------- | ----------------------- |
| Hotel      | Accommodation estimates |
| Food       | Daily meal budget       |
| Transport  | Local transportation    |
| Activities | Attractions & events    |
| Buffer     | Emergency reserve       |

### Goal

Maintain a travel plan that remains as close as possible to the user-defined budget.

---

## 📬 Notification Agent

Provides continuous travel awareness.

### Features

* Itinerary email delivery
* Travel warning notifications
* Periodic destination monitoring
* Automated advisory alerts

Users receive updates even after the itinerary has been generated.

---

# 🔧 MCP Tool Ecosystem

VoyageAgent follows an MCP-inspired tool architecture.

### Registered Tool Categories

| Tool        | Purpose                        |
| ----------- | ------------------------------ |
| Weather     | Forecast retrieval             |
| Events      | Ticketmaster integration       |
| Attractions | Activity discovery             |
| Places      | Geoapify location intelligence |
| Advisory    | Risk monitoring                |
| Email       | Notification delivery          |

### Additional Features

* Structured tool schemas
* Tool-call logging
* Response logging
* Error handling
* Configuration validation

---

# 📁 Project Structure

```text
VoyageAgent/
│
├── backend/
│   ├── app.py
│   ├── agents.py
│   ├── context_agent.py
│   ├── planner_agent.py
│   ├── budget_agent.py
│   ├── experience_agent.py
│   ├── notification_agent.py
│   ├── tools.py
│   ├── schemas.py
│   └── config.py
│
├── static/
│   └── index.html
│
├── .env.example
│
└── README.md
```

---

# ⚙️ Installation

## 1. Clone Repository

```powershell
git clone <repository-url>
cd VoyageAgent
```

## 2. Activate Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```powershell
python -m pip install -r backend\requirements.txt
```

## 4. Start Server

```powershell
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

---

# 🌐 Launch Application

Open:

```text
http://127.0.0.1:8000
```

---

# 🔑 Environment Configuration

Create configuration file:

```powershell
Copy-Item .env.example .env
notepad .env
```

Add credentials:

```env
OPENWEATHER_API_KEY=
TICKETMASTER_API_KEY=
GEOAPIFY_API_KEY=
NEWS_API_KEY=

EMAIL_USER=
EMAIL_PASS=

LLM_API_KEY=
LLM_MODEL=gpt-4o-mini
```

---

# 🌎 Real-Time Data Integrations

## OpenWeather

Provides destination forecasts.

### Used For

* Weather awareness
* Activity recommendations
* Planning optimization

---

## Ticketmaster

Provides live event discovery.

### Includes

* Concerts
* Sports events
* Theatre shows
* Attractions
* Entertainment packages

---

## Geoapify

Provides geographic intelligence.

### Includes

* Museums
* Restaurants
* Tourist attractions
* Landmarks
* City exploration

---

## NewsAPI

Monitors destination risks.

### Detects

* Severe weather
* Natural disasters
* Airport closures
* Safety advisories
* Major disruptions

---

# 📡 API Testing

## Generate Travel Plan

```powershell
$body = @{
  destination = "Bergen"
  start_date = "2026-06-01"
  end_date = "2026-06-04"
  duration_days = 4
  budget = 1000
  preferences = "budget food and natural scenery"
  email = $null
} | ConvertTo-Json

Invoke-RestMethod `
http://127.0.0.1:8000/api/plan `
-Method Post `
-ContentType "application/json" `
-Body $body
```

---

## View Registered Tools

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/tools
```

---

# 📈 System Observability

VoyageAgent provides transparent execution logging.

### Logged Operations

* Agent execution order
* Tool invocations
* Tool responses
* City validation
* Monitoring actions
* Notification delivery

This makes debugging and agent analysis significantly easier during development.

---

# 🛡 Fail-Safe Design

Missing API credentials never produce fabricated travel information.

Instead, VoyageAgent returns explicit:

```text
not-configured
```

responses, ensuring transparency and predictable behavior.

---

# 🔮 Future Roadmap

* Memory-enabled traveler profiles
* Multi-city trip planning
* Flight integration
* Hotel booking integration
* Interactive travel maps
* Agent-to-agent reasoning traces
* Autonomous itinerary refinement
* Real-time travel disruption recovery

---

# 🏆 Built With

* FastAPI
* Python
* MCP-style Tool Architecture
* OpenAI Models
* OpenWeather API
* Ticketmaster API
* Geoapify API
* NewsAPI
* Gmail SMTP

---

## The Vision

VoyageAgent is not just a travel planner.

It is an early step toward autonomous travel intelligence systems where specialized AI agents collaborate, reason, monitor, and adapt in real time to create personalized travel experiences.
