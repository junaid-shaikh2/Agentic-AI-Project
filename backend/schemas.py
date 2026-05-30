from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class TripRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: Optional[float] = None
    duration_days: Optional[int] = None
    email: Optional[EmailStr] = None
    preferences: Optional[str] = ""

    @model_validator(mode="after")
    def validate_dates(self):
        self.destination = self.destination.strip()
        if not self.destination:
            raise ValueError("destination is required")
        if self.end_date < self.start_date:
            raise ValueError("end_date must be the same as or later than start_date")
        if self.budget is not None and self.budget <= 0:
            raise ValueError("budget must be greater than zero")
        return self


class ItineraryDay(BaseModel):
    day: int
    summary: str
    activities: List[str]


class BudgetBreakdown(BaseModel):
    hotel: float = 0
    food: float = 0
    transport: float = 0
    activities: float = 0
    buffer: float = 0
    total: float = 0


class ItineraryPlan(BaseModel):
    destination: str
    trip_length_days: int
    title: str
    days: List[ItineraryDay]
    budget_estimate: float
    budget_breakdown: BudgetBreakdown = Field(default_factory=BudgetBreakdown)
    notes: Optional[str] = ""
    weather_summary: Optional[str] = ""
    events_summary: Optional[str] = ""
    attractions_summary: Optional[str] = ""
    ticketmaster_attractions_summary: Optional[str] = ""
    advisory_summary: Optional[str] = ""
    agent_trace: List[str] = Field(default_factory=list)
    raw_context: Dict[str, Any] = Field(default_factory=dict)
