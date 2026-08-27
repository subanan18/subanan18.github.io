from collections import defaultdict
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from .models import Task, TaskCreate, TaskUpdate

app = FastAPI(title="Realtime Collaborative Task Board", version="1.0.0")

workspaces: dict[str, dict[str, Task]] = defaultdict(dict)
connections: dict[str, set[WebSocket]] = defaultdict(set)


async def broadcast(workspace_id: str, event: dict) -> None:
    stale: list[WebSocket] = []
    for socket in connections[workspace_id].copy():
        try:
            await socket.send_json(event)
        except Exception:
            stale.append(socket)
    for socket in stale:
        connections[workspace_id].discard(socket)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "realtime-collab-board"}


@app.get("/workspaces/{workspace_id}/tasks", response_model=list[Task])
def list_tasks(workspace_id: str) -> list[Task]:
    return list(workspaces[workspace_id].values())


@app.post("/workspaces/{workspace_id}/tasks", response_model=Task, status_code=201)
async def create_task(workspace_id: str, payload: TaskCreate) -> Task:
    task = Task(id=str(uuid4()), workspace_id=workspace_id, **payload.model_dump())
    workspaces[workspace_id][task.id] = task
    await broadcast(workspace_id, {
        "type": "task.created",
        "workspace_id": workspace_id,
        "data": task.model_dump(mode="json"),
    })
    return task


@app.patch("/workspaces/{workspace_id}/tasks/{task_id}", response_model=Task)
async def update_task(workspace_id: str, task_id: str, payload: TaskUpdate) -> Task:
    current = workspaces[workspace_id].get(task_id)
    if not current:
        raise HTTPException(status_code=404, detail="Task not found")

    updated = current.model_copy(update=payload.model_dump(exclude_none=True))
    workspaces[workspace_id][task_id] = updated
    await broadcast(workspace_id, {
        "type": "task.updated",
        "workspace_id": workspace_id,
        "data": updated.model_dump(mode="json"),
    })
    return updated


@app.delete("/workspaces/{workspace_id}/tasks/{task_id}", status_code=204)
async def delete_task(workspace_id: str, task_id: str) -> None:
    if task_id not in workspaces[workspace_id]:
        raise HTTPException(status_code=404, detail="Task not found")
    del workspaces[workspace_id][task_id]
    await broadcast(workspace_id, {
        "type": "task.deleted",
        "workspace_id": workspace_id,
        "data": {"id": task_id},
    })


@app.websocket("/ws/{workspace_id}")
async def workspace_socket(websocket: WebSocket, workspace_id: str) -> None:
    await websocket.accept()
    connections[workspace_id].add(websocket)
    await websocket.send_json({
        "type": "workspace.connected",
        "workspace_id": workspace_id,
        "data": {"active_connections": len(connections[workspace_id])},
    })
    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        connections[workspace_id].discard(websocket)
