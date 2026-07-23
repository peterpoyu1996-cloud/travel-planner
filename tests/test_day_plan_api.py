"""backend/app 的 /day-plan API smoke test。核心情境：使用者自己分天選景點，
程式檢查天序順不順、必要時建議更好的天序，但不動使用者選的景點組合。
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# 真實 KB id，涵蓋北/中/南三區，都有座標：
NORTH = ["kouri-tower", "churaumi-aquarium"]
CENTRAL = ["aeon-mall-okinawa-rycom"]
SOUTH = ["tomari-fish-market", "kokusai-street"]
NO_COORDS = "onna-kaihin-koen-nabee-beach"

NAHA_AIRPORT_ANCHOR = {"lat": 26.1958, "lng": 127.6455, "label": "那霸機場"}


def _base_request(
    days: list[list[str]],
    deadlines: dict[str, str] | None = None,
    start_times: list[str] | None = None,
    **overrides,
) -> dict:
    deadlines = deadlines or {}
    day_payloads = []
    for i, ids in enumerate(days):
        day_payload = {"stops": [{"attraction_id": aid, "must_arrive_by": deadlines.get(aid)} for aid in ids]}
        if start_times:
            day_payload["start_time"] = start_times[i]
        day_payloads.append(day_payload)

    payload = {
        "days": day_payloads,
        "start_date": "2026-01-07",
        "start": NAHA_AIRPORT_ANCHOR,
    }
    payload.update(overrides)
    return payload


def test_zigzag_day_order_gets_a_suggestion():
    # 使用者選的天序：北 -> 南 -> 中，來回跑，應該被建議調整
    resp = client.post("/day-plan", json=_base_request([NORTH, SOUTH, CENTRAL]))
    assert resp.status_code == 200
    body = resp.json()

    assert len(body["chosen_days"]) == 3
    # chosen 的每一天景點組合要維持使用者原本選的，不會被搬動
    assert {s["id"] for s in body["chosen_days"][0]["stops"]} == set(NORTH)
    assert {s["id"] for s in body["chosen_days"][1]["stops"]} == set(SOUTH)
    assert {s["id"] for s in body["chosen_days"][2]["stops"]} == set(CENTRAL)

    assert body["suggested_order"] is not None
    assert body["suggested_total_minutes"] < body["chosen_total_minutes"]
    assert body["minutes_saved"] > 0

    # suggested 的每一天景點組合是 chosen 那幾包的重新排列，不會出現新景點或漏掉景點
    # （排序用 sorted(tuple) 而不是 str(set)——set 的 repr 順序看 hash 隨機種子，
    # 每次啟動 Python 都可能不一樣，用 str 排序等於巧合式通過，不是真的穩定）
    suggested_ids_per_day = [tuple(sorted(s["id"] for s in day["stops"])) for day in body["suggested_days"]]
    expected = [tuple(sorted(NORTH)), tuple(sorted(SOUTH)), tuple(sorted(CENTRAL))]
    assert sorted(suggested_ids_per_day) == sorted(expected)


def test_already_sensible_day_order_gets_no_suggestion():
    # 南 -> 中 -> 北，由近到遠，理論上已經是合理天序
    resp = client.post("/day-plan", json=_base_request([SOUTH, CENTRAL, NORTH]))
    assert resp.status_code == 200
    body = resp.json()
    assert body["suggested_order"] is None
    assert body["suggested_days"] is None
    assert body["minutes_saved"] == 0.0


def test_single_day_never_gets_a_suggestion():
    resp = client.post("/day-plan", json=_base_request([NORTH]))
    assert resp.status_code == 200
    body = resp.json()
    assert body["suggested_order"] is None


def test_more_than_7_days_rejected():
    resp = client.post("/day-plan", json=_base_request([["kouri-tower"]] * 8))
    assert resp.status_code == 422


def test_same_attraction_in_two_days_rejected():
    resp = client.post("/day-plan", json=_base_request([["kouri-tower"], ["kouri-tower"]]))
    assert resp.status_code == 422


def test_unknown_attraction_id_rejected():
    resp = client.post("/day-plan", json=_base_request([["not-a-real-id"]]))
    assert resp.status_code == 422


def test_day_entirely_missing_coords_rejected():
    resp = client.post("/day-plan", json=_base_request([[NO_COORDS]]))
    assert resp.status_code == 422


def test_partial_missing_coords_excluded_with_warning():
    resp = client.post("/day-plan", json=_base_request([[*NORTH, NO_COORDS]]))
    assert resp.status_code == 200
    body = resp.json()
    assert NO_COORDS in body["excluded_attraction_ids"]
    all_ids = {s["id"] for day in body["chosen_days"] for s in day["stops"]}
    assert NO_COORDS not in all_ids
    assert any("缺少座標" in w for w in body["warnings"])


# ============================================================================
# 時間窗（訂位時間）：只有標了 must_arrive_by 的景點才受影響。
# ============================================================================


def test_no_deadline_leaves_eta_and_late_by_minutes_none():
    resp = client.post("/day-plan", json=_base_request([SOUTH]))
    assert resp.status_code == 200
    body = resp.json()
    for stop in body["chosen_days"][0]["stops"]:
        assert stop["eta"] is None
        assert stop["late_by_minutes"] is None
    assert not any("訂位" in w for w in body["warnings"])


def test_generous_deadline_is_satisfied_and_shown_in_eta():
    resp = client.post(
        "/day-plan",
        json=_base_request([SOUTH], deadlines={"kokusai-street": "20:00"}),
    )
    assert resp.status_code == 200
    body = resp.json()
    stops_by_id = {s["id"]: s for s in body["chosen_days"][0]["stops"]}
    assert stops_by_id["kokusai-street"]["eta"] is not None
    assert stops_by_id["kokusai-street"]["late_by_minutes"] is None
    assert not any("訂位" in w for w in body["warnings"])


def test_impossible_deadline_reports_warning_and_late_by_minutes():
    # deadline 設在出發時間本身，兩站都在南部但彼此有實際車程，不可能剛好準時
    resp = client.post(
        "/day-plan",
        json=_base_request([SOUTH], deadlines={"kokusai-street": "09:00"}, start_times=["09:00"]),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert any("訂位" in w for w in body["warnings"])
    stops_by_id = {s["id"]: s for s in body["chosen_days"][0]["stops"]}
    assert stops_by_id["kokusai-street"]["late_by_minutes"] is not None
    assert stops_by_id["kokusai-street"]["late_by_minutes"] > 0


def test_start_time_defaults_when_omitted():
    # 不給 start_time 也該能正常送出（schema 層預設 09:00），不是必填炸掉
    payload = _base_request([SOUTH])
    for day in payload["days"]:
        day.pop("start_time", None)
    resp = client.post("/day-plan", json=payload)
    assert resp.status_code == 200
