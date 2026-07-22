"""backend/app 的 /custom-route、/attractions API smoke test。只驗證幾個關鍵情境
（合法請求／超過上限／未知 id／缺座標景點），不是窮舉所有輸入組合。
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# 從 data/attractions.json 挑的真實 id：kouri-tower / churaumi-aquarium 有座標，
# onna-kaihin-koen-nabee-beach（恩納海濱公園ナビービーチ）目前 lat/lng 是 null——
# scraper/fill_missing_coords.py 試過 OSM 快照比對跟 Nominatim 查詢都沒找到可信候選，
# 維持 null，不猜測填入（見 data/schema.md「不可用猜測值填入」）。
VALID_POI_A = "kouri-tower"
VALID_POI_B = "churaumi-aquarium"
POI_WITHOUT_COORDS = "onna-kaihin-koen-nabee-beach"


def _base_request(**overrides) -> dict:
    payload = {
        "attraction_ids": [VALID_POI_A, VALID_POI_B],
        "trip_days": 2,
        "start_date": "2026-01-07",
        "start": {"poi_id": VALID_POI_A},
    }
    payload.update(overrides)
    return payload


def test_attractions_endpoint_returns_public_shape():
    resp = client.get("/attractions")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) > 0
    sample = body[0]
    assert set(sample.keys()) == {
        "id", "name", "category", "region_group", "sub_area",
        "lat", "lng", "suggested_stay_duration", "kid_friendly",
        "recommendation_score", "budget_level",
    }
    # 內部欄位不該出現在公開清單裡
    assert "source_note" not in sample
    assert "description_for_embedding" not in sample


def test_valid_custom_route_returns_expected_shape():
    resp = client.post("/custom-route", json=_base_request())
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["days"]) == 2
    assert isinstance(body["total_travel_minutes"], float)
    assert body["excluded_attraction_ids"] == []

    all_stop_ids = {stop["id"] for day in body["days"] for stop in day["stops"]}
    assert all_stop_ids == {VALID_POI_A, VALID_POI_B}


def test_31_ids_rejected_by_schema_cap():
    resp = client.post("/custom-route", json=_base_request(attraction_ids=[VALID_POI_A] * 31))
    assert resp.status_code == 422


def test_unknown_attraction_id_rejected():
    resp = client.post("/custom-route", json=_base_request(attraction_ids=["not-a-real-id"]))
    assert resp.status_code == 422


def test_poi_missing_coords_is_excluded_not_fabricated():
    resp = client.post(
        "/custom-route",
        json=_base_request(attraction_ids=[VALID_POI_A, POI_WITHOUT_COORDS]),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert POI_WITHOUT_COORDS in body["excluded_attraction_ids"]
    all_stop_ids = {stop["id"] for day in body["days"] for stop in day["stops"]}
    assert POI_WITHOUT_COORDS not in all_stop_ids
    assert any("缺少座標" in w for w in body["warnings"])


def test_geo_anchor_requires_exactly_one_source():
    both_given = _base_request(start={"poi_id": VALID_POI_A, "lat": 26.1, "lng": 127.6})
    resp = client.post("/custom-route", json=both_given)
    assert resp.status_code == 422

    neither_given = _base_request(start={})
    resp = client.post("/custom-route", json=neither_given)
    assert resp.status_code == 422


def test_round_trip_same_start_and_end_poi_is_allowed():
    # 起訖點用同一個 POI 是合法情境（例如同一個機場進出），不該被擋——起訖點內部
    # 用不同的虛擬 id（__start__/__end__）表示，即使座標相同也不衝突。
    resp = client.post(
        "/custom-route",
        json=_base_request(end={"poi_id": VALID_POI_A}),
    )
    assert resp.status_code == 200
    body = resp.json()
    all_stop_ids = {stop["id"] for day in body["days"] for stop in day["stops"]}
    assert all_stop_ids == {VALID_POI_A, VALID_POI_B}
