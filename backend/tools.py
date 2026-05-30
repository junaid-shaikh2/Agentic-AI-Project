import logging
from typing import Any, Dict, List

import httpx

from .config import settings

logger = logging.getLogger("voyageagent.mcp")


class MCPToolClient:
    """Small MCP-style client used by agents to call registered tools.

    This is intentionally lightweight: each tool has a schema, a single async
    handler, structured output, and logs around calls/responses.
    """

    def __init__(self):
        self.httpx_timeout = 15
        self.tools = {
            "weather": {
                "description": "Live weather forecast for the selected destination city.",
                "required": ["location"],
                "handler": self.fetch_weather,
            },
            "events": {
                "description": "Local events from Ticketmaster Discovery API.",
                "required": ["location", "start_date", "end_date"],
                "handler": self.fetch_events,
            },
            "ticketmaster_attractions": {
                "description": "Ticketmaster attractions such as artists, sports teams, packages, and plays.",
                "required": ["location"],
                "handler": self.fetch_ticketmaster_attractions,
            },
            "places": {
                "description": "Tourist attractions, museums, landmarks, and restaurants from Geoapify Places API.",
                "required": ["location"],
                "handler": self.fetch_places,
            },
            "travel_advisory": {
                "description": "Safety and disruption signals from NewsAPI.",
                "required": ["location"],
                "handler": self.fetch_travel_advisory,
            },
        }

    def registry(self) -> Dict[str, Any]:
        return {
            name: {
                "description": meta["description"],
                "required": meta["required"],
                "response_shape": "JSON object with source, note, and tool-specific data.",
            }
            for name, meta in self.tools.items()
        }

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in self.tools:
            raise ValueError(f"Unknown MCP tool: {tool_name}")

        self._validate_required(tool_name, params)
        logger.info("MCP tool call: %s params=%s", tool_name, self._safe_params(params))
        try:
            result = await self.tools[tool_name]["handler"](params)
        except httpx.HTTPError as exc:
            result = {"source": "external-api-error", "note": f"{tool_name} API call failed: {exc}"}
        logger.info("MCP tool response: %s source=%s", tool_name, result.get("source"))
        return result

    def _validate_required(self, tool_name: str, params: Dict[str, Any]) -> None:
        missing = [key for key in self.tools[tool_name]["required"] if not params.get(key)]
        if missing:
            raise ValueError(f"{tool_name} missing required params: {', '.join(missing)}")

    def _safe_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in params.items() if "key" not in key.lower()}

    async def fetch_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        location = params["location"].strip()
        if not settings.openweather_api_key:
            return {
                "source": "not-configured",
                "location": location,
                "forecast": [],
                "note": "OPENWEATHER_API_KEY is missing. Add it to .env for live weather.",
            }

        url = "https://api.openweathermap.org/data/2.5/forecast"
        query = {"q": location, "appid": settings.openweather_api_key, "units": "metric"}
        async with httpx.AsyncClient(timeout=self.httpx_timeout) as client:
            response = await client.get(url, params=query)
            response.raise_for_status()
            payload = response.json()

        forecast = [
            {
                "when": item.get("dt_txt"),
                "condition": item.get("weather", [{}])[0].get("description"),
                "temp_c": item.get("main", {}).get("temp"),
            }
            for item in payload.get("list", [])[:8]
        ]
        return {"source": "openweathermap", "location": location, "forecast": forecast, "note": ""}

    async def fetch_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        location = params["location"].strip()
        if not settings.ticketmaster_api_key:
            return {
                "source": "not-configured",
                "location": location,
                "events": [],
                "note": "TICKETMASTER_API_KEY is missing. Add it to .env for live city events.",
            }

        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        query = {
            "apikey": settings.ticketmaster_api_key,
            "city": location,
            "startDateTime": f"{params['start_date']}T00:00:00Z",
            "endDateTime": f"{params['end_date']}T23:59:59Z",
            "size": 8,
            "sort": "date,asc",
        }
        async with httpx.AsyncClient(timeout=self.httpx_timeout) as client:
            response = await client.get(url, params=query)
            response.raise_for_status()
            payload = response.json()

        events = []
        for item in payload.get("_embedded", {}).get("events", []):
            venue = item.get("_embedded", {}).get("venues", [{}])[0]
            events.append(
                {
                    "name": item.get("name"),
                    "date": item.get("dates", {}).get("start", {}).get("localDate"),
                    "type": item.get("classifications", [{}])[0].get("segment", {}).get("name"),
                    "venue": venue.get("name"),
                    "url": item.get("url"),
                }
            )
        note = "" if events else f"No Ticketmaster events found for {location} in the selected dates."
        return {"source": "ticketmaster", "location": location, "events": events, "note": note}

    async def fetch_ticketmaster_attractions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        location = params["location"].strip()
        if not settings.ticketmaster_api_key:
            return {
                "source": "not-configured",
                "location": location,
                "ticketmaster_attractions": [],
                "note": "TICKETMASTER_API_KEY is missing. In Ticketmaster, use your app Consumer Key as this value.",
            }

        url = "https://app.ticketmaster.com/discovery/v2/attractions.json"
        query = {
            "apikey": settings.ticketmaster_api_key,
            # Ticketmaster attraction search is name/keyword based, not tourist-place based.
            "keyword": location,
            "size": 8,
            "sort": "name,asc",
        }
        async with httpx.AsyncClient(timeout=self.httpx_timeout) as client:
            response = await client.get(url, params=query)
            response.raise_for_status()
            payload = response.json()

        attractions = []
        for item in payload.get("_embedded", {}).get("attractions", []):
            attractions.append(
                {
                    "name": item.get("name"),
                    "type": item.get("type"),
                    "url": item.get("url"),
                    "segment": item.get("classifications", [{}])[0].get("segment", {}).get("name"),
                    "genre": item.get("classifications", [{}])[0].get("genre", {}).get("name"),
                }
            )
        note = "" if attractions else f"No Ticketmaster attractions found for keyword '{location}'."
        return {
            "source": "ticketmaster",
            "location": location,
            "ticketmaster_attractions": attractions,
            "note": note,
        }

    async def fetch_places(self, params: Dict[str, Any]) -> Dict[str, Any]:
        location = params["location"].strip()
        if not settings.geoapify_api_key:
            return {
                "source": "not-configured",
                "location": location,
                "places": [],
                "note": "GEOAPIFY_API_KEY is missing. Add it to .env for live attractions, museums, landmarks, and restaurants.",
            }

        coordinates = await self._geocode_city(location)
        if not coordinates:
            return {
                "source": "geoapify",
                "location": location,
                "places": [],
                "note": f"Geoapify could not geocode '{location}'. Try a more specific city name.",
            }

        url = "https://api.geoapify.com/v2/places"
        query = {
            "categories": ",".join(
                [
                    "tourism.attraction",
                    "tourism.sights",
                    "entertainment.museum",
                    "heritage",
                    "building.historic",
                    "catering.restaurant",
                ]
            ),
            "filter": f"circle:{coordinates['lon']},{coordinates['lat']},12000",
            "bias": f"proximity:{coordinates['lon']},{coordinates['lat']}",
            "limit": 12,
            "apiKey": settings.geoapify_api_key,
        }
        async with httpx.AsyncClient(timeout=self.httpx_timeout) as client:
            response = await client.get(url, params=query)
            response.raise_for_status()
            payload = response.json()

        places = []
        for feature in payload.get("features", []):
            props = feature.get("properties", {})
            places.append(
                {
                    "name": props.get("name") or props.get("address_line1") or "Unnamed place",
                    "address": props.get("formatted"),
                    "categories": props.get("categories", []),
                    "lon": props.get("lon"),
                    "lat": props.get("lat"),
                    "distance_m": props.get("distance"),
                    "website": props.get("website"),
                }
            )
        note = "" if places else f"No Geoapify places found for {location}."
        return {
            "source": "geoapify",
            "location": location,
            "center": coordinates,
            "places": places,
            "note": note,
        }

    async def _geocode_city(self, location: str) -> Dict[str, float] | None:
        """Resolve the selected city to coordinates before calling Geoapify Places."""
        url = "https://api.geoapify.com/v1/geocode/search"
        query = {
            "text": location,
            "type": "city",
            "limit": 1,
            "format": "json",
            "apiKey": settings.geoapify_api_key,
        }
        async with httpx.AsyncClient(timeout=self.httpx_timeout) as client:
            response = await client.get(url, params=query)
            response.raise_for_status()
            payload = response.json()

        results = payload.get("results", [])
        if not results:
            return None
        first = results[0]
        return {"lat": first.get("lat"), "lon": first.get("lon")}

    async def fetch_travel_advisory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        location = params["location"].strip()
        if not settings.news_api_key:
            return {
                "source": "not-configured",
                "location": location,
                "alerts": [],
                "danger_detected": False,
                "note": "NEWS_API_KEY is missing. Add it to .env for live advisory monitoring.",
            }

        terms = " OR ".join(["war", "disaster", "storm", "airport shutdown", "extreme weather", "travel warning"])
        url = "https://newsapi.org/v2/everything"
        query = {
            "apiKey": settings.news_api_key,
            "q": f"{location} ({terms})",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
        }
        async with httpx.AsyncClient(timeout=self.httpx_timeout) as client:
            response = await client.get(url, params=query)
            response.raise_for_status()
            payload = response.json()

        alerts = [
            {
                "title": article.get("title"),
                "source": article.get("source", {}).get("name"),
                "url": article.get("url"),
                "published_at": article.get("publishedAt"),
            }
            for article in payload.get("articles", [])
        ]
        danger_detected = self._danger_detected(alerts)
        return {
            "source": "newsapi",
            "location": location,
            "alerts": alerts,
            "danger_detected": danger_detected,
            "note": "Potential travel risk found." if danger_detected else "",
        }

    def _danger_detected(self, alerts: List[Dict[str, Any]]) -> bool:
        danger_words = ("war", "storm", "disaster", "shutdown", "warning", "extreme")
        text = " ".join(str(alert.get("title", "")).lower() for alert in alerts)
        return any(word in text for word in danger_words)
