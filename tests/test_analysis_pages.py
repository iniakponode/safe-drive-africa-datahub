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
    ]
}


def test_trend_endpoint_json():
    with patch("app.cache.get_cached_data", return_value=sample_data):
        resp = client.get("/analysis/driver/d1/trend?week=2024-W23", headers={"accept": "application/json"})
    assert resp.status_code == 200
    assert resp.json()["ubpk"] == 0.2


def test_history_page():
    with patch("app.cache.get_cached_data", return_value=sample_data):
        resp = client.get("/analysis/driver/d1/history")
    assert resp.status_code == 200
    assert "UBPK History" in resp.text


def test_dashboard_table_columns():
    with patch("app.cache.get_cached_data", return_value=sample_data):
        resp = client.get("/")
    assert resp.status_code == 200
    assert "Driver ID" in resp.text and "Week" in resp.text
    assert "/analysis/driver/d1" in resp.text


def test_driver_analysis_page_selector():
    with patch("app.cache.get_cached_data", return_value=sample_data):
        resp = client.get("/analysis/driver/d1")
    assert resp.status_code == 200
    assert "id=\"week-select\"" in resp.text
    assert f"/metrics/behavior/driver/d1/history" in resp.text


def test_trip_analysis_page():
    with patch("app.cache.get_cached_data", return_value=sample_data):
        resp = client.get("/analysis/trip/t1")
    assert resp.status_code == 200
    assert "Trip t1 Analysis" in resp.text
    assert "/analysis/driver/d1" in resp.text
