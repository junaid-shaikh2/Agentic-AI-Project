# VoyageAgent MVP

VoyageAgent is a lightweight multi-agent travel planner built with the current FastAPI + static HTML stack.

## What Is Implemented

- Context Agent: calls MCP tools for weather, events, places, and travel advisory data.
- Planner Agent: creates the day-by-day itinerary for the exact selected destination city.
- Experience Agent: adds preference and weather-aware activity notes.
- Budget Agent: calculates hotel, food, transport, activity, and buffer budgets and keeps the total near the user budget.
- Notification Agent: sends itinerary emails with Gmail SMTP and includes a simple periodic advisory monitor.
- MCP Tool Layer: registered tool schemas, structured responses, tool call logging, and tool response logging.

## Files

```text
backend/app.py                 FastAPI routes, logging, email task, monitoring loop
backend/agents.py              VoyageAgent orchestrator
backend/context_agent.py       MCP context collection
backend/planner_agent.py       Itinerary creation
backend/budget_agent.py        Budget calculation and enforcement
backend/experience_agent.py    Preference/weather enhancements
backend/notification_agent.py  Gmail itinerary and warning emails
backend/tools.py               MCP-style tool registry and API clients
backend/schemas.py             Request/response models
backend/config.py              Environment variable settings
static/index.html              Basic frontend
.env.example                   API key template
```

## Exact Commands

```powershell
cd c:\AAi
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

Open:

```text
http://127.0.0.1:8000
```

## API Keys

Copy the template:

```powershell
Copy-Item .env.example .env
notepad .env
```

Put keys exactly here:

```text
OPENWEATHER_API_KEY=your_openweather_key
TICKETMASTER_API_KEY=your_ticketmaster_key
GEOAPIFY_API_KEY=your_geoapify_key
NEWS_API_KEY=your_newsapi_key
EMAIL_USER=yourgmail@gmail.com
EMAIL_PASS=your_gmail_app_password
LLM_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4o-mini
```

Without API keys, tools return clear `not-configured` responses instead of fake city data.

## Live Tool Behavior

- Weather: OpenWeatherMap forecast for the submitted destination city.
- Events: Ticketmaster events for the submitted destination city and selected date range.
- Ticketmaster Attractions: Ticketmaster artists, sports teams, packages, and plays from `/discovery/v2/attractions.json`.
- Places: Geoapify geocodes the submitted destination city, then fetches tourist attractions, museums, landmarks, and restaurants nearby.
- Travel Advisory: NewsAPI scan for wars, disasters, storms, extreme weather, warnings, and airport shutdowns.
- Email: Gmail SMTP sends the itinerary and later warning emails if monitoring detects danger.

For Gmail, enable 2-Step Verification on the Gmail account, create an App Password, and use that App Password as `EMAIL_PASS`. Do not use your normal Gmail password.

## Quick API Test

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

Invoke-RestMethod http://127.0.0.1:8000/api/plan -Method Post -ContentType "application/json" -Body $body
```

Tool registry:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/tools
```

## Notes

- Use a city like `Bergen`, `Oslo`, `Paris`, or `Tokyo`, not only a country, because event and places APIs work best with city names.
- Logs show selected city validation, MCP tool calls, MCP responses, and agent execution order.
- The monitor is deliberately simple: it runs inside the FastAPI process every hour for trips with an email address.
