from fastapi.testclient import TestClient

STATION_PAYLOAD = {
    "name": "Paz Ayalon",
    "chain": "Paz",
    "address": "Ayalon Highway",
    "city": "Tel Aviv",
    "latitude": 32.05,
    "longitude": 34.78,
}


def _create_station(client: TestClient, **overrides) -> dict:
    payload = {**STATION_PAYLOAD, **overrides}
    response = client.post("/stations", json=payload)
    assert response.status_code == 201
    return response.json()


def _post_review(client: TestClient, station_id: int, **overrides) -> dict:
    payload = {
        "bathroom_type": "women",
        "cleanliness": 3,
        "has_soap": True,
        "has_toilet_paper": True,
        "is_wheelchair_accessible": False,
        "has_baby_changing_table": False,
        "feels_safe": True,
        **overrides,
    }
    response = client.post(f"/stations/{station_id}/reviews", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_station_returns_full_station_with_id(client: TestClient):
    station = _create_station(client)
    assert station["id"] is not None
    assert station["name"] == STATION_PAYLOAD["name"]
    assert station["city"] == STATION_PAYLOAD["city"]


def test_get_station_not_found(client: TestClient):
    response = client.get("/stations/999")
    assert response.status_code == 404


def test_new_station_has_no_reviews_yet(client: TestClient):
    station = _create_station(client)
    response = client.get(f"/stations/{station['id']}")
    data = response.json()
    assert data["review_count"] == 0
    assert data["average_cleanliness"] is None


def test_station_stats_average_across_all_bathroom_types(client: TestClient):
    station = _create_station(client)
    _post_review(client, station["id"], bathroom_type="women", cleanliness=4)
    _post_review(client, station["id"], bathroom_type="men", cleanliness=2)

    response = client.get(f"/stations/{station['id']}")
    data = response.json()
    assert data["review_count"] == 2
    assert data["average_cleanliness"] == 3.0


def test_station_stats_filtered_by_bathroom_type(client: TestClient):
    station = _create_station(client)
    _post_review(client, station["id"], bathroom_type="women", cleanliness=4)
    _post_review(client, station["id"], bathroom_type="men", cleanliness=2)

    women_only = client.get(f"/stations/{station['id']}?bathroom_type=women").json()
    assert women_only["review_count"] == 1
    assert women_only["average_cleanliness"] == 4.0

    accessible_only = client.get(f"/stations/{station['id']}?bathroom_type=accessible").json()
    assert accessible_only["review_count"] == 0
    assert accessible_only["average_cleanliness"] is None


def test_list_stations_filters_by_city(client: TestClient):
    _create_station(client, name="Tel Aviv Station", city="Tel Aviv")
    _create_station(client, name="Haifa Station", city="Haifa")

    response = client.get("/stations?city=Haifa")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Haifa Station"


def test_list_stations_without_filter_returns_all(client: TestClient):
    _create_station(client, name="Station A")
    _create_station(client, name="Station B")

    response = client.get("/stations")
    assert len(response.json()) == 2
