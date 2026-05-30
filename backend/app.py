import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .agents import VoyageAgent
from .schemas import ItineraryPlan, TripRequest

BASE_DIR = Path(__file__).resolve().parent.parent
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")

app = FastAPI(title="VoyageAgent MVP")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

voyage_agent = VoyageAgent()
monitored_trips: list[TripRequest] = []


@app.on_event("startup")
async def start_monitoring_service():
    asyncio.create_task(_monitor_trips_periodically())


async def _monitor_trips_periodically():
    """Simple in-process monitoring loop for demo deployments."""
    while True:
        await asyncio.sleep(3600)
        for request in monitored_trips:
            await voyage_agent.notification_agent.monitor_destination_once(request)


@app.get("/", response_class=HTMLResponse)
async def homepage():
    index_path = BASE_DIR / "static" / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/api/plan", response_model=ItineraryPlan)
async def create_plan(request: TripRequest, background_tasks: BackgroundTasks):
    request.destination = request.destination.strip()
    logging.getLogger("voyageagent.api").info("API received selected destination city=%s", request.destination)
    plan = await voyage_agent.build_plan(request)
    if request.email:
        background_tasks.add_task(voyage_agent.notification_agent.send_itinerary, request, plan)
        monitored_trips.append(request)
    return plan


@app.get("/api/tools")
async def list_tools():
    return {"protocol": "MCP-style JSON tool interface", "tools": voyage_agent.tool_registry()}


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
