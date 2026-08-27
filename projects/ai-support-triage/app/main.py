import asyncio

from fastapi import FastAPI

from .models import Ticket, TriageResult
from .service import TriageEngine

app = FastAPI(title="AI Support Triage API", version="1.0.0")
engine = TriageEngine()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ai-support-triage"}


@app.post("/triage", response_model=TriageResult)
def triage(ticket: Ticket) -> TriageResult:
    return engine.analyse(ticket)


@app.post("/triage/batch", response_model=list[TriageResult])
async def triage_batch(tickets: list[Ticket]) -> list[TriageResult]:
    return await asyncio.gather(*(asyncio.to_thread(engine.analyse, ticket) for ticket in tickets))
