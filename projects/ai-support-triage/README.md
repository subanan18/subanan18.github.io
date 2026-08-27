# AI Support Triage API

A production-style FastAPI demo for classifying incoming support requests by urgency, category and suggested next action. It is designed around a pluggable analysis service so a local deterministic classifier can be swapped for an LLM provider without changing the API layer.

## Why this project

Recruiters can inspect concrete examples of:

- service-layer architecture
- typed API contracts
- explainable classification output
- confidence scoring
- async batch processing
- safe fallback behaviour
- unit/integration testing

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

## Endpoints

- `GET /health`
- `POST /triage`
- `POST /triage/batch`

## Example

Request:

```json
{
  "subject": "Payment failed but account charged",
  "message": "I was charged twice and cannot access my account. Please help urgently."
}
```

Response:

```json
{
  "category": "billing",
  "priority": "critical",
  "confidence": 0.95,
  "signals": ["charged", "twice", "urgent"],
  "suggested_action": "Escalate immediately to billing support"
}
```

The included engine is deterministic so the repository works without secrets or paid APIs. The `TriageEngine` interface makes it straightforward to add an OpenAI/Claude/local-model adapter later.
