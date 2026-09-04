from datetime import date, datetime, timedelta
from types import SimpleNamespace

from fastapi.testclient import TestClient
import pytest

from tests.conftest import mysql_available, requires_mysql


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@requires_mysql
def test_asset_crud(client: TestClient) -> None:
    dept = client.post("/api/departments", json={"name": "Test Dept", "code": "TST", "description": "d"}).json()
    created = client.post(
        "/api/assets",
        json={
            "asset_code": "TST-ASSET-1",
            "asset_type": "track",
            "name": "Test rail",
            "section": "JP-AII",
            "department_id": dept["id"],
            "criticality": "HIGH",
            "status": "OPERATIONAL",
        },
    )
    assert created.status_code == 201, created.text
    asset_id = created.json()["id"]
    fetched = client.get(f"/api/assets/{asset_id}")
    assert fetched.status_code == 200
    updated = client.put(f"/api/assets/{asset_id}", json={"condition_score": 55})
    assert updated.status_code == 200
    assert updated.json()["condition_score"] == 55
    missing = client.get("/api/assets/999999")
    assert missing.status_code == 404


@requires_mysql
def test_maintenance_crud(client: TestClient) -> None:
    dept = client.post("/api/departments", json={"name": "Test Dept 2", "code": "TS2"}).json()
    asset = client.post(
        "/api/assets",
        json={
            "asset_code": "TST-ASSET-2",
            "asset_type": "signal",
            "name": "Sig",
            "section": "JP-AII",
            "department_id": dept["id"],
        },
    ).json()
    created = client.post(
        "/api/maintenance/tasks",
        json={
            "task_code": "TST-TASK-1",
            "asset_id": asset["id"],
            "department_id": dept["id"],
            "source_system": "INTERNAL",
            "task_type": "inspection",
            "section": "JP-AII",
            "priority": "HIGH",
            "estimated_duration_minutes": 60,
        },
    )
    assert created.status_code == 201, created.text
    task_id = created.json()["id"]
    assert client.get(f"/api/maintenance/tasks/{task_id}").status_code == 200
    updated = client.put(f"/api/maintenance/tasks/{task_id}", json={"status": "IN_PROGRESS"})
    assert updated.json()["status"] == "IN_PROGRESS"


@requires_mysql
def test_train_schedule_retrieval(client: TestClient) -> None:
    train = client.post(
        "/api/trains",
        json={
            "train_number": "99999",
            "train_name": "Test",
            "train_type": "EXPRESS",
            "priority": "HIGH",
        },
    )
    assert train.status_code == 201, train.text
    sched = client.post(
        "/api/schedules",
        json={
            "train_id": train.json()["id"],
            "section": "JP-AII",
            "arrival_time": "2026-09-05T10:00:00",
            "departure_time": "2026-09-05T10:12:00",
            "schedule_date": "2026-09-05",
        },
    )
    assert sched.status_code == 201
    listed = client.get("/api/schedules", params={"section": "JP-AII", "schedule_date": "2026-09-05"})
    assert listed.status_code == 200
    assert any(row["train_id"] == train.json()["id"] for row in listed.json())


@requires_mysql
def test_maintenance_overview(client: TestClient) -> None:
    response = client.get("/api/maintenance-overview", params={"section": "JP-AII", "horizon": "weekly"})
    assert response.status_code == 200
    body = response.json()
    assert body["section"] == "JP-AII"
    assert "tasks" in body
    assert "available_windows" in body
    assert "summary" in body


@requires_mysql
def test_prioritized_tasks_api(client: TestClient) -> None:
    response = client.get("/api/prioritized-tasks", params={"section": "JP-AII", "weather": "normal"})
    assert response.status_code in {200, 503}
    if response.status_code == 200:
        body = response.json()
        assert "tasks" in body
        if body["tasks"]:
            assert "rank" in body["tasks"][0]
            assert "risk_score" in body["tasks"][0]


@requires_mysql
def test_weekly_and_monthly_plan(client: TestClient) -> None:
    weekly = client.get("/api/weekly-plan", params={"section": "JP-AII", "weather": "NORMAL"})
    assert weekly.status_code in {200, 503}
    monthly = client.get("/api/monthly-plan", params={"section": "JP-AII"})
    assert monthly.status_code == 200
    assert "weeks" in monthly.json()


@requires_mysql
def test_scenario_comparison(client: TestClient) -> None:
    response = client.get("/api/scenario", params={"section": "JP-AII", "type": "ai"})
    assert response.status_code in {200, 503}
    if response.status_code == 200:
        body = response.json()
        assert "comparison" in body
        for key in ("manual", "coordinated", "ai"):
            assert key in body["comparison"]
            assert "total_block_hours" in body["comparison"][key]


@requires_mysql
def test_weather_reschedule(client: TestClient) -> None:
    for weather in ("NORMAL", "HEAVY_RAIN", "HEATWAVE", "FOG"):
        response = client.post(
            "/api/weather/reschedule",
            json={"section": "JP-AII", "date": "2026-09-05", "weather": weather},
        )
        assert response.status_code in {200, 503}, weather
        if response.status_code == 200:
            body = response.json()
            assert body["weather_condition"] == weather
            assert "reason" in body
