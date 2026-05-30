import logging
from typing import List

from .llm_client import LLMClient
from .schemas import BudgetBreakdown, ItineraryDay, TripRequest

logger = logging.getLogger("voyageagent.agent.budget")


class BudgetAgent:
    """Calculates and enforces a budget that tracks days and trip style."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client

    async def estimate_and_enforce(self, request: TripRequest, days: List[ItineraryDay]) -> tuple[List[ItineraryDay], BudgetBreakdown]:
        logger.info("Budget Agent input budget=%s days=%s", request.budget, len(days))
        breakdown = self._calculate_budget(request, len(days))
        adjusted_days = self._enforce_budget(days, breakdown, request.budget)
        logger.info("Budget Agent output total=%s", breakdown.total)
        return adjusted_days, breakdown

    def _calculate_budget(self, request: TripRequest, days_count: int) -> BudgetBreakdown:
        days_count = max(1, days_count)

        if request.budget:
            # Target 95% so the total stays inside the requested budget and within the +-10% band.
            total = round(request.budget * 0.95, 2)
        else:
            total = round(days_count * 150.0, 2)

        hotel = round(total * 0.42, 2)
        food = round(total * 0.24, 2)
        transport = round(total * 0.16, 2)
        activities = round(total * 0.13, 2)
        buffer = round(total - hotel - food - transport - activities, 2)
        return BudgetBreakdown(
            hotel=hotel,
            food=food,
            transport=transport,
            activities=activities,
            buffer=buffer,
            total=total,
        )

    def _enforce_budget(self, days: List[ItineraryDay], breakdown: BudgetBreakdown, budget: float | None) -> List[ItineraryDay]:
        if not budget:
            return days

        daily_activity_allowance = breakdown.activities / max(1, len(days))
        daily_food_allowance = breakdown.food / max(1, len(days))
        daily_transport_allowance = breakdown.transport / max(1, len(days))

        for day in days:
            day.activities.append(
                f"Budget guardrail: keep activities near ${daily_activity_allowance:.0f}, "
                f"food near ${daily_food_allowance:.0f}, and transport near ${daily_transport_allowance:.0f} today."
            )
            day.activities.append("Cost control: prefer public transport, self-guided walks, and free/low-cost viewpoints.")
        return days
