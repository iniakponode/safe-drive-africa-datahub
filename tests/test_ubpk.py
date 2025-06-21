from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)

sample_data = {
    "dashboard_trip_metrics": [
        {
            "driverProfileId": "d1",
            "tripId": "t1",
            "start_time": "2024-06-03T10:00:00",
            "week": "2024-W23",
            "totalSensorDataCount": 10,
            "invalidSensorDataCount": 2,
            "validSensorDataCount": 8,
        },
        {
            "driverProfileId": "d1",
            "tripId": "t2",
            "start_time": "2024-05-27T10:00:00",
            "week": "2024-W22",
            "totalSensorDataCount": 8,
            "invalidSensorDataCount": 1,
            "validSensorDataCount": 7,
        },
        {
            "driverProfileId": "d2",
            "tripId": "t3",
            "start_time": "2024-06-03T11:00:00",
            "week": "2024-W23",
            "totalSensorDataCount": 6,
            "invalidSensorDataCount": 3,
            "validSensorDataCount": 3,
        },
        {
            "driverProfileId": "d2",
            "tripId": "t4",
            "start_time": "2024-05-27T11:00:00",
            "week": "2024-W22",
            "totalSensorDataCount": 6,
            "invalidSensorDataCount": 0,
            "validSensorDataCount": 6,
        },
    ]
}


def test_trip_metrics():
    with patch("app.cache.get_cached_data", return_value=sample_data):
        resp = client.get("/metrics/behavior/trip")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert body[0]["driverProfileId"] == "d1"
    assert "ubpk" in body[0]


def test_weekly_metrics():
    with patch("app.cache.get_cached_data", return_value=sample_data):
        resp = client.get("/metrics/behavior/weekly?week=2024-W23")
    assert resp.status_code == 200
    data = {item["driverProfileId"]: item for item in resp.json()}
    assert data["d1"]["numTrips"] == 1
    assert round(data["d2"]["ubpk"], 3) == 0.5


def test_improvement_analysis():
    with patch("app.cache.get_cached_data", return_value=sample_data):
        resp = client.get("/metrics/behavior/improvement?week=2024-W23")
    assert resp.status_code == 200
    body = resp.json()
    assert "p_value" in body and "mean_difference" in body
