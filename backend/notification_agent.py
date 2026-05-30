import json
import logging
from typing import Dict

from .emailer import EmailClient
from .schemas import ItineraryPlan, TripRequest
from .tools import MCPToolClient

logger = logging.getLogger("voyageagent.agent.notification")


class NotificationAgent:
    """Sends itinerary emails and provides a simple advisory check hook."""

    def __init__(self, email_client: EmailClient, tool_client: MCPToolClient):
        self.email_client = email_client
        self.tool_client = tool_client

    async def send_itinerary(self, request: TripRequest, plan: ItineraryPlan) -> Dict[str, str]:
        if not request.email:
            return {"status": "skipped", "reason": "No email provided."}

        logger.info("Notification Agent sending itinerary to=%s", request.email)
        text = f"Your VoyageAgent itinerary for {request.destination}\n\n{json.dumps(plan.model_dump(), indent=2)}"
        html = f"<h1>{plan.title}</h1><pre>{json.dumps(plan.model_dump(), indent=2)}</pre>"
        return await self.email_client.send_email(
            str(request.email),
            f"VoyageAgent itinerary for {request.destination}",
            text,
            html,
        )

    async def monitor_destination_once(self, request: TripRequest) -> Dict[str, str]:
        """One lightweight monitoring pass; call periodically from a simple scheduler."""
        advisory = await self.tool_client.call_tool("travel_advisory", {"location": request.destination.strip()})
        if not request.email or not advisory.get("danger_detected"):
            return {"status": "no-warning"}

        subject = f"VoyageAgent travel warning for {request.destination}"
        body = "Potential travel risk detected. Please review your itinerary and consider replanning.\n\n"
        body += json.dumps(advisory, indent=2)
        return await self.email_client.send_email(str(request.email), subject, body, f"<pre>{body}</pre>")
