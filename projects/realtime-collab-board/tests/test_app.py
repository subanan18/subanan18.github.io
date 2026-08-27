from fastapi.testclient import TestClient

from app.main import app, workspaces

client = TestClient(app)


def setup_function() -> None:
    workspaces.clear()


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_update_and_list_task() -> None:
    created = client.post(
        "/workspaces/engineering/tasks",
        json={"title": "Ship realtime dashboard"},
    )
    assert created.status_code == 201
    task_id = created.json()["id"]

    updated = client.patch(
        f"/workspaces/engineering/tasks/{task_id}",
        json={"status": "done"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"

    listed = client.get("/workspaces/engineering/tasks")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_websocket_receives_task_event() -> None:
    with client.websocket_connect("/ws/engineering") as websocket:
        connected = websocket.receive_json()
        assert connected["type"] == "workspace.connected"

        client.post(
            "/workspaces/engineering/tasks",
            json={"title": "Realtime event"},
        )
        event = websocket.receive_json()
        assert event["type"] == "task.created"
        assert event["data"]["title"] == "Realtime event"
