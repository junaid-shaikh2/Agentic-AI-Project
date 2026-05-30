import logging
from typing import Dict, List

from .llm_client import LLMClient
from .schemas import ItineraryDay, TripRequest

logger = logging.getLogger("voyageagent.agent.experience")


class ExperienceAgent:
    """Adds preference-aware practical notes without changing the selected city."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client

    async def enhance(self, request: TripRequest, days: List[ItineraryDay], context: Dict) -> List[ItineraryDay]:
        logger.info("Experience Agent input city=%s", request.destination)
        preferences = (request.preferences or "").lower()
        weather = context.get("weather", {}).get("forecast", [])
        rainy_or_snowy = any(
            word in str(item.get("condition", "")).lower()
            for item in weather
            for word in ("rain", "snow", "storm")
        )

        if not days:
            return days

        if "food" in preferences:
            days[0].activities.append("Preference match: try local markets, bakeries, and casual regional restaurants.")
        if "natural" in preferences or "scenery" in preferences:
            days[0].activities.append("Preference match: reserve daylight for scenic viewpoints, waterfronts, parks, or nearby nature routes.")
        if rainy_or_snowy:
            days[0].activities.append("Weather adjustment: keep an indoor backup because the forecast shows rain, snow, or storms.")

        logger.info("Experience Agent output days=%s", len(days))
        return days
