import logging
from typing import Any, Dict, List

from .budget_agent import BudgetAgent
from .context_agent import ContextAgent
from .emailer import EmailClient
from .experience_agent import ExperienceAgent
from .llm_client import LLMClient
from .notification_agent import NotificationAgent
from .planner_agent import PlannerAgent
from .schemas import ItineraryPlan, TripRequest
from .tools import MCPToolClient

logger = logging.getLogger("voyageagent")


class VoyageAgent:
    """Coordinates the lightweight multi-agent workflow."""

    def __init__(self):
        self.tool_client = MCPToolClient()
        self.llm_client = LLMClient()
        self.context_agent = ContextAgent(self.tool_client)
        self.planner_agent = PlannerAgent(self.llm_client)
        self.experience_agent = ExperienceAgent(self.llm_client)
        self.budget_agent = BudgetAgent(self.llm_client)
        self.notification_agent = NotificationAgent(EmailClient(), self.tool_client)

    async def build_plan(self, request: TripRequest) -> ItineraryPlan:
        destination = request.destination.strip()
        logger.info("VoyageAgent request destination city=%s", destination)

        context = await self.context_agent.enrich(request)
        days = await self.planner_agent.create_itinerary(request, context)
        days = await self.experience_agent.enhance(request, days, context)
        days, budget = await self.budget_agent.estimate_and_enforce(request, days)

        agent_trace = [
            f"Context Agent fetched MCP context for {destination}.",
            "Planner Agent created the day-by-day itinerary.",
            "Experience Agent adjusted activities for preferences and weather.",
            f"Budget Agent enforced a total estimate of ${budget.total:.2f}.",
        ]

        return ItineraryPlan(
            destination=destination,
            trip_length_days=len(days),
            title=f"VoyageAgent itinerary for {destination}",
            days=days,
            budget_estimate=budget.total,
            budget_breakdown=budget,
            notes="Budget is enforced as a hard cap when the user provides one.",
            weather_summary=self._format_weather_summary(context.get("weather", {})),
            events_summary=self._format_events_summary(context.get("events", {})),
            attractions_summary=self._format_places_summary(context.get("places", {})),
            ticketmaster_attractions_summary=self._format_ticketmaster_attractions_summary(
                context.get("ticketmaster_attractions", {})
            ),
            advisory_summary=self._format_advisory_summary(context.get("travel_advisory", {})),
            agent_trace=agent_trace,
            raw_context=context,
        )

    def tool_registry(self) -> Dict[str, Any]:
        return self.tool_client.registry()

    def _format_weather_summary(self, weather: Dict[str, Any]) -> str:
        forecast = weather.get("forecast", [])
        if not forecast:
            return weather.get("note", "No weather data available.")
        first = forecast[0]
        return f"{first.get('condition')} at {first.get('temp_c')} C in {weather.get('location', 'selected city')}."

    def _format_events_summary(self, events: Dict[str, Any]) -> str:
        event_list = events.get("events", [])
        if not event_list:
            return events.get("note", "No events found.")
        return ", ".join(self._names(event_list))

    def _format_places_summary(self, places: Dict[str, Any]) -> str:
        place_list = places.get("places", [])
        if not place_list:
            return places.get("note", "No attractions found.")
        return ", ".join(self._names(place_list))

    def _format_ticketmaster_attractions_summary(self, payload: Dict[str, Any]) -> str:
        attraction_list = payload.get("ticketmaster_attractions", [])
        if not attraction_list:
            return payload.get("note", "No Ticketmaster attractions found.")
        return ", ".join(self._names(attraction_list))

    def _format_advisory_summary(self, advisory: Dict[str, Any]) -> str:
        if advisory.get("danger_detected"):
            return advisory.get("note", "Potential travel risk detected.")
        if advisory.get("alerts"):
            return "No major danger detected in recent advisory scan."
        return advisory.get("note", "No advisory data available.")

    def _names(self, items: List[Dict[str, Any]]) -> List[str]:
        return [str(item.get("name", "Unnamed")) for item in items[:5]]
