import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from .llm_client import LLMClient
from .schemas import ItineraryDay, TripRequest

logger = logging.getLogger("voyageagent.agent.planner")


class PlannerAgent:
    """Creates a day-by-day plan using the selected city and MCP context."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client

    async def create_itinerary(self, request: TripRequest, context: Dict[str, Dict]) -> List[ItineraryDay]:
        logger.info("Planner Agent input city=%s budget=%s", request.destination, request.budget)
        if self.llm_client:
            itinerary = await self._create_itinerary_with_llm(request, context)
            if itinerary:
                logger.info("Planner Agent output days=%s via=llm", len(itinerary))
                return itinerary

        itinerary = self._create_static_itinerary(request, context)
        logger.info("Planner Agent output days=%s via=deterministic", len(itinerary))
        return itinerary

    async def _create_itinerary_with_llm(self, request: TripRequest, context: Dict[str, Dict]) -> List[ItineraryDay] | None:
        prompt = (
            f"Create a {self.estimate_days(request.start_date, request.end_date)} day itinerary for {request.destination}.\n"
            f"Budget hard cap: {request.budget if request.budget else 'not provided'} USD.\n"
            f"Preferences: {request.preferences or 'none'}.\n"
            f"Weather: {self._summarize_weather(context.get('weather', {}))}.\n"
            f"Events: {self._summarize_items(context.get('events', {}).get('events', []))}.\n"
            f"Ticketmaster attractions: {self._summarize_items(context.get('ticketmaster_attractions', {}).get('ticketmaster_attractions', []))}.\n"
            f"Places: {self._summarize_items(context.get('places', {}).get('places', []))}.\n"
            "Use only the selected destination city. Return valid JSON only: "
            "{\"days\":[{\"day\":1,\"summary\":\"...\",\"activities\":[\"...\"]}]}"
        )
        response = await self.llm_client.complete(prompt)
        data = self._parse_json(response)
        if not isinstance(data, dict) or not isinstance(data.get("days"), list):
            return None

        return [
            ItineraryDay(
                day=int(item.get("day", index + 1)),
                summary=str(item.get("summary", "Travel day")),
                activities=[str(activity) for activity in item.get("activities", [])],
            )
            for index, item in enumerate(data["days"])
        ]

    def _create_static_itinerary(self, request: TripRequest, context: Dict[str, Dict]) -> List[ItineraryDay]:
        destination = request.destination.strip()
        places = context.get("places", {}).get("places", [])
        events = context.get("events", {}).get("events", [])
        ticketmaster_attractions = context.get("ticketmaster_attractions", {}).get("ticketmaster_attractions", [])
        days_count = self.estimate_days(request.start_date, request.end_date)
        days: List[ItineraryDay] = []

        for day_number in range(1, days_count + 1):
            place = self._pick_name(places, day_number - 1, f"a well-reviewed attraction in {destination}")
            second_place = self._pick_name(places, day_number, f"a walkable area in {destination}")
            event = self._pick_event(events, day_number - 1)
            tm_attraction = self._pick_name(ticketmaster_attractions, day_number - 1, "")
            evening = event or tm_attraction or f"budget dinner and self-guided evening walk in {destination}"
            days.append(
                ItineraryDay(
                    day=day_number,
                    summary=f"{destination} day {day_number}",
                    activities=[
                        f"Morning: visit {place}",
                        f"Afternoon: explore {second_place}",
                        f"Evening: {evening}",
                    ],
                )
            )
        return days

    def estimate_days(self, start_date: str, end_date: str) -> int:
        # Dates are the source of truth; the frontend also sends duration for validation/display.
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            return max(1, (end - start).days + 1)
        except ValueError:
            return 1

    def _pick_name(self, items: List[Dict[str, Any]], index: int, fallback: str) -> str:
        if not items:
            return fallback
        item = items[index % len(items)]
        name = item.get("name") or fallback
        rating = f" (rating {item['rating']})" if item.get("rating") else ""
        return f"{name}{rating}"

    def _pick_event(self, events: List[Dict[str, Any]], index: int) -> str:
        if not events:
            return ""
        item = events[index % len(events)]
        venue = f" at {item['venue']}" if item.get("venue") else ""
        date = f" on {item['date']}" if item.get("date") else ""
        return f"{item.get('name', 'local event')}{venue}{date}"

    def _summarize_weather(self, weather: Dict[str, Any]) -> str:
        forecast = weather.get("forecast", [])
        if not forecast:
            return weather.get("note", "No live weather available")
        return "; ".join(f"{item.get('condition')} {item.get('temp_c')} C" for item in forecast[:3])

    def _summarize_items(self, items: List[Dict[str, Any]]) -> str:
        return ", ".join(str(item.get("name")) for item in items[:5]) or "none"

    def _parse_json(self, response: str) -> Any:
        if not response:
            return None
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end > start:
                try:
                    return json.loads(response[start : end + 1])
                except json.JSONDecodeError:
                    return None
            return None
