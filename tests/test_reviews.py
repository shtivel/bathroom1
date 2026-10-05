from fastapi.testclient import TestClient

STATION_PAYLOAD = {
    "name": "Sonol Haifa",
    "chain": "Sonol",
    "address": "Hof HaCarmel",
    "city": "Haifa",
    "latitude": 32.79,
    "longitude": 34.97,
}

REVIEW_PAYLOAD = {
    "bathroom_type": "women",
    "cleanliness": 4,
    "has_soap": True,
    "has_toilet_paper": True,
    "is_wheelchair_accessible": False,
    "has_baby_changing_table": True,
    "feels_safe": True,
    "comment": "Pretty clean, could use more soap refills",
}


def _create_station(client: TestClient) -> dict:
    response = client.post("/stations", json=STATION_PAYLOAD)
    assert response.status_code == 201
    return response.json()


def test_create_review_for_existing_station(client: TestClient):
    station = _create_station(client)

    response = client.post(f"/stations/{station['id']}/reviews", json=REVIEW_PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert data["station_id"] == station["id"]
    assert data["bathroom_type"] == "women"
    assert data["cleanliness"] == 4
    assert data["comment"] == REVIEW_PAYLOAD["comment"]
    assert "id" in data
    assert "created_at" in data


def test_create_review_for_missing_station_returns_404(client: TestClient):
    response = client.post("/stations/999/reviews", json=REVIEW_PAYLOAD)
    assert response.status_code == 404


def test_cleanliness_out_of_range_is_rejected(client: TestClient):
    station = _create_station(client)

    response = client.post(
        f"/stations/{station['id']}/reviews",
        json={**REVIEW_PAYLOAD, "cleanliness": 7},
    )

    assert response.status_code == 422


def test_invalid_bathroom_type_is_rejected(client: TestClient):
    station = _create_station(client)

    response = client.post(
        f"/stations/{station['id']}/reviews",
        json={**REVIEW_PAYLOAD, "bathroom_type": "not_a_real_type"},
    )

    assert response.status_code == 422


def test_list_reviews_for_missing_station_returns_404(client: TestClient):
    response = client.get("/stations/999/reviews")
    assert response.status_code == 404


def test_list_reviews_filters_by_bathroom_type(client: TestClient):
    station = _create_station(client)
    client.post(
        f"/stations/{station['id']}/reviews", json={**REVIEW_PAYLOAD, "bathroom_type": "women"}
    )
    client.post(
        f"/stations/{station['id']}/reviews", json={**REVIEW_PAYLOAD, "bathroom_type": "men"}
    )

    response = client.get(f"/stations/{station['id']}/reviews?bathroom_type=women")
    data = response.json()
    assert len(data) == 1
    assert data[0]["bathroom_type"] == "women"
