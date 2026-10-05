import logging

from fastapi.testclient import TestClient

STATION_PAYLOAD = {
    "name": "Log Test Station",
    "chain": "Paz",
    "address": "Somewhere",
    "city": "Tel Aviv",
    "latitude": 32.0,
    "longitude": 34.0,
}


def test_create_station_logs_info(client: TestClient, caplog):
    with caplog.at_level(logging.INFO, logger="bathroom_grader.routers.stations"):
        response = client.post("/stations", json=STATION_PAYLOAD)

    assert response.status_code == 201
    assert any("Created station" in record.message for record in caplog.records)


def test_missing_station_logs_warning(client: TestClient, caplog):
    with caplog.at_level(logging.WARNING, logger="bathroom_grader.routers.stations"):
        response = client.get("/stations/999")

    assert response.status_code == 404
    assert any(record.levelname == "WARNING" for record in caplog.records)


def test_create_review_logs_info(client: TestClient, caplog):
    station = client.post("/stations", json=STATION_PAYLOAD).json()

    with caplog.at_level(logging.INFO, logger="bathroom_grader.routers.reviews"):
        response = client.post(
            f"/stations/{station['id']}/reviews",
            json={
                "bathroom_type": "women",
                "cleanliness": 4,
                "has_soap": True,
                "has_toilet_paper": True,
                "is_wheelchair_accessible": False,
                "has_baby_changing_table": True,
                "feels_safe": True,
            },
        )

    assert response.status_code == 201
    assert any("Created review" in record.message for record in caplog.records)
