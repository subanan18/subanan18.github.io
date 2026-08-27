# Realtime Collaborative Task Board

A recruiter-facing realtime backend demo built with FastAPI and WebSockets. Multiple browser clients can join the same workspace, create/update tasks, and receive changes instantly without polling.

## What it demonstrates

- FastAPI REST API design
- WebSocket connection management
- Realtime fan-out by workspace
- Typed Pydantic request/response models
- Async Python
- Testable service boundaries
- Clean API + realtime event architecture

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open API docs at `http://localhost:8000/docs`.

WebSocket endpoint:

```text
ws://localhost:8000/ws/{workspace_id}
```

## Example event

```json
{
  "type": "task.created",
  "workspace_id": "engineering",
  "data": {
    "id": "...",
    "title": "Ship realtime dashboard",
    "status": "todo"
  }
}
```

## API

- `GET /health`
- `GET /workspaces/{workspace_id}/tasks`
- `POST /workspaces/{workspace_id}/tasks`
- `PATCH /workspaces/{workspace_id}/tasks/{task_id}`
- `DELETE /workspaces/{workspace_id}/tasks/{task_id}`
- `WS /ws/{workspace_id}`

For portfolio/demo use the store is intentionally in-memory; replacing it with PostgreSQL/Redis is straightforward because storage and realtime fan-out are separated from route handling.
