import logging
from typing import Dict

from .schemas import TripRequest
from .tools import MCPToolClient

logger = logging.getLogger("voyageagent.agent.context")


class ContextAgent:
    """Fetches live context through MCP tools before itinerary planning."""

    def __init__(self, tool_client: MCPToolClient):
        self.tool_client = tool_client

    async def enrich(self, request: TripRequest) -> Dict:
        destination = request.destination.strip()
        logger.info("Context Agent selected destination city=%s", destination)

        context = {
            "weather": await self.tool_client.call_tool("weather", {"location": destination}),
            "events": await self.tool_client.call_tool(
                "events",
                {
                    "location": destination,
                    "start_date": request.start_date,
                    "end_date": request.end_date,
                },
            ),
            "ticketmaster_attractions": await self.tool_client.call_tool(
                "ticketmaster_attractions",
                {"location": destination},
            ),
            "places": await self.tool_client.call_tool("places", {"location": destination}),
            "travel_advisory": await self.tool_client.call_tool("travel_advisory", {"location": destination}),
        }
        logger.info("Context Agent completed tools for city=%s", destination)
        return context
