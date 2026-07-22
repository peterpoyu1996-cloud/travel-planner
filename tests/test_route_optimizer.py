"""common/geo/route_optimizer.py 的純函式測試。全專案第一個測試模組，範圍刻意只涵蓋
這個新模組——其他既有程式碼（尤其 itinerary.py）核心行為是「LLM 說了算」，本來就難單元測試，
不在這次範圍內回頭補。
"""

import math

import pytest

from common.geo.route_optimizer import (
    Leg,
    RoutePoint,
    best_day_order_by_centroid,
    build_distance_matrix,
    chain_optimize_days,
    day_centroid,
    evaluate_day_plan,
    nearest_neighbor_path,
    optimize_route,
    parse_stay_minutes,
    split_into_days,
    two_opt,
)

# 沖繩本島南部隨便一個角落附近，邊長約 0.01 度（約 1.1km）的正方形四個角，
# 座標夠近，estimate_minutes() 一定會選 surface（平面道路）路徑，不會被高速公路的
# 交流道繞路邏輯干擾，讓「總車程」跟「總 haversine 距離」維持單調對應關係，
# 方便用解析幾何驗證演算法有沒有找到真正的最佳解。
SQUARE = {
    "A": (26.30, 127.80),
    "B": (26.30, 127.81),
    "C": (26.31, 127.81),
    "D": (26.31, 127.80),
}


def _square_points(order: str = "ABCD") -> list[RoutePoint]:
    return [RoutePoint(id=name, lat=SQUARE[name][0], lng=SQUARE[name][1]) for name in order]


class TestParseStayMinutes:
    def test_none_input(self):
        assert parse_stay_minutes(None) is None

    def test_no_number_found(self):
        assert parse_stay_minutes("開放中") is None

    def test_hours_only(self):
        assert parse_stay_minutes("約1.5小時") == pytest.approx(90.0)

    def test_minutes_only(self):
        assert parse_stay_minutes("30分鐘") == pytest.approx(30.0)

    def test_hours_and_minutes_combined(self):
        assert parse_stay_minutes("1小時30分") == pytest.approx(90.0)

    def test_ignores_clock_times_without_unit(self):
        # "14:30進場，16:00離開（約1.5小時）"：14:30/16:00 不該被誤認成分鐘數，
        # 只有帶「小時」/「分」單位的數字才算數
        assert parse_stay_minutes("14:30進場，16:00離開（約1.5小時）") == pytest.approx(90.0)


class TestBuildDistanceMatrix:
    def test_diagonal_is_zero(self):
        points = _square_points()
        matrix, _ = build_distance_matrix(points)
        for i in range(len(points)):
            assert matrix[i][i] == 0.0

    def test_matrix_is_symmetric(self):
        points = _square_points()
        matrix, _ = build_distance_matrix(points)
        n = len(points)
        for i in range(n):
            for j in range(n):
                assert matrix[i][j] == matrix[j][i]

    def test_details_cover_every_unordered_pair(self):
        points = _square_points()
        _, details = build_distance_matrix(points)
        n = len(points)
        expected_pairs = {(i, j) for i in range(n) for j in range(i + 1, n)}
        assert set(details.keys()) == expected_pairs


class TestNearestNeighborAndTwoOpt:
    def test_square_open_path_finds_brute_force_optimum(self):
        # 注意：緯度/經度的「一度」實際公里數不同（經度隨緯度升高而壓縮），
        # 這四個角在度數上是正方形，實際車程距離其實是長方形，兩組對邊不完全等長。
        # 不用解析假設，直接窮舉剩餘 3 點的全部排列找出真正最小值來比對，才不會
        # 因為錯誤的幾何假設誤判演算法對不對。
        import itertools

        points = _square_points("ABCD")
        matrix, _ = build_distance_matrix(points)

        def total(path):
            return sum(matrix[path[i]][path[i + 1]] for i in range(len(path) - 1))

        brute_force_best = min(
            total([0, *perm]) for perm in itertools.permutations([1, 2, 3])
        )

        nn_path = nearest_neighbor_path(matrix, start_index=0)
        optimized = two_opt(nn_path, matrix, fixed_end=False)

        assert total(optimized) == pytest.approx(brute_force_best, rel=1e-9)
        assert optimized[0] == 0  # 起點必須固定在最前面

    def test_two_opt_never_worse_than_nearest_neighbor(self):
        # 隨機幾組點，2-opt 改善後的總車程不能比純最近鄰構造差
        import random

        rng = random.Random(42)
        for _ in range(5):
            points = [
                RoutePoint(id=f"p{i}", lat=26.1 + rng.random() * 0.5, lng=127.6 + rng.random() * 0.8)
                for i in range(8)
            ]
            matrix, _ = build_distance_matrix(points)
            nn_path = nearest_neighbor_path(matrix, start_index=0)
            improved = two_opt(nn_path, matrix, fixed_end=False)

            def total(path):
                return sum(matrix[path[i]][path[i + 1]] for i in range(len(path) - 1))

            assert total(improved) <= total(nn_path) + 1e-6

    def test_fixed_start_and_end_preserved(self):
        points = _square_points("ABCD")
        matrix, _ = build_distance_matrix(points)

        nn_path = nearest_neighbor_path(matrix, start_index=0, end_index=2)
        assert nn_path[0] == 0
        assert nn_path[-1] == 2

        optimized = two_opt(nn_path, matrix, fixed_end=True)
        assert optimized[0] == 0
        assert optimized[-1] == 2


class TestOptimizeRoute:
    def test_rejects_too_many_points(self):
        points = [RoutePoint(id=f"p{i}", lat=26.1, lng=127.7) for i in range(33)]
        with pytest.raises(ValueError):
            optimize_route(points, start_id="p0")

    def test_rejects_unknown_start_id(self):
        points = _square_points()
        with pytest.raises(ValueError):
            optimize_route(points, start_id="not-a-real-id")

    def test_rejects_same_start_and_end(self):
        points = _square_points()
        with pytest.raises(ValueError):
            optimize_route(points, start_id="A", end_id="A")

    def test_returns_legs_matching_order_length(self):
        points = _square_points()
        result = optimize_route(points, start_id="A")
        assert len(result["legs"]) == len(result["order"]) - 1
        assert result["order"][0].id == "A"
        assert result["total_minutes"] == pytest.approx(
            sum(leg.minutes for leg in result["legs"])
        )


class TestSplitIntoDays:
    def _synthetic(self, n: int, leg_minutes: float = 30.0):
        order = [RoutePoint(id=f"p{i}", lat=26.1, lng=127.7, suggested_stay_minutes=60.0) for i in range(n)]
        legs = [Leg(from_id=f"p{i}", to_id=f"p{i+1}", minutes=leg_minutes, via="surface", detail="")
                for i in range(n - 1)]
        return order, legs

    def test_rejects_non_positive_trip_days(self):
        order, legs = self._synthetic(3)
        with pytest.raises(ValueError):
            split_into_days(order, legs, trip_days=0)

    def test_result_length_always_equals_trip_days(self):
        order, legs = self._synthetic(5)
        result = split_into_days(order, legs, trip_days=8)
        assert len(result) == 8

    def test_no_points_dropped_or_duplicated_and_order_preserved(self):
        order, legs = self._synthetic(10)
        result = split_into_days(order, legs, trip_days=3)
        flattened = [p for day in result for p in day]
        assert flattened == order

    def test_trailing_days_empty_when_more_days_than_points(self):
        order, legs = self._synthetic(2)
        result = split_into_days(order, legs, trip_days=5)
        assert len(result) == 5
        non_empty = [day for day in result if day]
        assert len(non_empty) <= 2
        # 沒有點被留在空 list 裡搞丟
        assert sum(len(day) for day in result) == 2

    def test_days_are_roughly_balanced_by_weight(self):
        # 切分是依「權重」（車程+停留時間）平衡，不是依點數平衡——起點本身權重是 0
        # （沒有「進入它」的 leg），所以點數兩天不見得會一樣多，但每天的權重總和
        # 應該落在 target 正負一個「單位權重」以內（貪婪換行演算法的標準誤差界線）。
        order, legs = self._synthetic(10, leg_minutes=20.0)
        result = split_into_days(order, legs, trip_days=2)
        assert len(result) == 2

        unit_weight = 20.0 + 60.0  # leg_minutes + suggested_stay_minutes，這組合成資料裡均一
        target = (len(order) - 1) * unit_weight / 2

        for day in result:
            day_weight = sum(unit_weight for p in day if order.index(p) != 0)
            assert abs(day_weight - target) <= unit_weight


# ============================================================================
# 分天規劃測試：模擬「使用者自己選好每天要去哪些景點，程式檢查天序順不順」這個情境。
# 座標佈局：起點在南部（靠近那霸機場），三個 bucket 分別是北部/南部/中部的景點群，
# 刻意設計成「南部 bucket 離起點最近、中部居中、北部最遠」，如果照 [北,南,中] 這種
# 天序走（模擬使用者選的「第一天北部、第二天南部、第三天中部」），會來回跑；
# 真正合理的天序應該是由近到遠沿路收，也就是 [南,中,北]。
# ============================================================================

START_POINT = RoutePoint(id="start", lat=26.20, lng=127.65)  # 靠近那霸機場

NORTH_BUCKET = [
    RoutePoint(id="north-1", lat=26.70, lng=128.00),
    RoutePoint(id="north-2", lat=26.72, lng=128.02),
]
SOUTH_BUCKET = [
    RoutePoint(id="south-1", lat=26.15, lng=127.68),
    RoutePoint(id="south-2", lat=26.17, lng=127.70),
]
CENTRAL_BUCKET = [
    RoutePoint(id="central-1", lat=26.35, lng=127.80),
    RoutePoint(id="central-2", lat=26.37, lng=127.82),
]

ZIGZAG_ORDER = [NORTH_BUCKET, SOUTH_BUCKET, CENTRAL_BUCKET]  # 使用者選的「壞」天序
GOOD_ORDER = [SOUTH_BUCKET, CENTRAL_BUCKET, NORTH_BUCKET]    # 由近到遠，理論上的「好」天序


class TestDayCentroid:
    def test_averages_coordinates(self):
        points = [RoutePoint(id="a", lat=26.0, lng=127.0), RoutePoint(id="b", lat=26.2, lng=127.4)]
        lat, lng = day_centroid(points)
        assert lat == pytest.approx(26.1)
        assert lng == pytest.approx(127.2)


class TestBestDayOrderByCentroid:
    def test_reorders_away_from_zigzag(self):
        best_order = best_day_order_by_centroid(ZIGZAG_ORDER, START_POINT)
        assert best_order != [0, 1, 2]

        # 用窮舉獨立驗證，不是單純相信函式自己算的結果
        import itertools

        from common.geo.geo_utils import haversine_km

        centroids = [day_centroid(b) for b in ZIGZAG_ORDER]

        def total(order):
            path = [(START_POINT.lat, START_POINT.lng)] + [centroids[i] for i in order]
            return sum(haversine_km(*path[i], *path[i + 1]) for i in range(len(path) - 1))

        brute_force_best = min(itertools.permutations(range(3)), key=total)
        assert best_order == list(brute_force_best)
        assert best_order == [1, 2, 0]  # 對應 [南,中,北]，符合地理直覺

    def test_already_good_order_returns_identity(self):
        best_order = best_day_order_by_centroid(GOOD_ORDER, START_POINT)
        assert best_order == [0, 1, 2]


class TestChainOptimizeDays:
    def test_all_points_preserved_across_days(self):
        result = chain_optimize_days(ZIGZAG_ORDER, START_POINT)
        assert len(result["days"]) == 3

        all_ids = {p.id for day in result["days"] for p in day}
        expected_ids = {p.id for bucket in ZIGZAG_ORDER for p in bucket}
        assert all_ids == expected_ids

    def test_legs_count_matches_total_real_points(self):
        result = chain_optimize_days(ZIGZAG_ORDER, START_POINT)
        total_points = sum(len(bucket) for bucket in ZIGZAG_ORDER)
        assert len(result["legs"]) == total_points  # 每個真實點都有一段「進入它」的 leg

    def test_no_internal_anchor_ids_leak_into_legs(self):
        result = chain_optimize_days(ZIGZAG_ORDER, START_POINT, end=RoutePoint(id="end", lat=26.20, lng=127.65))
        for leg in result["legs"]:
            assert "__day_anchor_" not in leg.from_id
            assert "__day_anchor_" not in leg.to_id
        # 第一段 leg 要從真正的 start id 開始，不是內部錨點 id
        assert result["legs"][0].from_id == START_POINT.id

    def test_end_anchor_fixes_last_stop_of_last_day(self):
        end = RoutePoint(id="end", lat=26.20, lng=127.65)
        result = chain_optimize_days(ZIGZAG_ORDER, START_POINT, end=end)
        # end 本身不該出現在任何一天的真實景點清單裡（它是虛擬終點，不是使用者選的景點）
        all_ids = {p.id for day in result["days"] for p in day}
        assert "end" not in all_ids


class TestEvaluateDayPlan:
    def test_zigzag_triggers_suggestion(self):
        result = evaluate_day_plan(ZIGZAG_ORDER, START_POINT)
        assert result["suggested_order"] is not None
        assert result["suggested_order"] == [1, 2, 0]
        assert result["minutes_saved"] > 1.0
        assert result["suggested"]["total_minutes"] < result["chosen"]["total_minutes"]

    def test_already_good_order_returns_no_suggestion(self):
        result = evaluate_day_plan(GOOD_ORDER, START_POINT)
        assert result["suggested_order"] is None
        assert result["suggested"] is None
        assert result["minutes_saved"] == 0.0

    def test_single_day_never_suggests(self):
        result = evaluate_day_plan([NORTH_BUCKET], START_POINT)
        assert result["suggested_order"] is None

    def test_chosen_days_match_input_bucket_order(self):
        # chosen（使用者選的天序）不該被重排，只有 suggested 才是候選的新順序
        result = evaluate_day_plan(ZIGZAG_ORDER, START_POINT)
        chosen_day1_ids = {p.id for p in result["chosen"]["days"][0]}
        assert chosen_day1_ids == {p.id for p in NORTH_BUCKET}

    def test_empty_order_returns_all_empty_days(self):
        result = split_into_days([], [], trip_days=4)
        assert result == [[], [], [], []]
