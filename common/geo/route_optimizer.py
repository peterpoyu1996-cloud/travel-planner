"""單一景點清單 → 最小車程排序 → 依天數切分。純演算法，不呼叫任何 LLM，
不呼叫任何外部路由 API（沿用 common/geo/travel_time.py 的本地估算），
不依賴 FastAPI/Pydantic（common/ 跟 backend/ 分離原則，見 CLAUDE.md）。

跟 backend/app/itinerary.py 的關係：itinerary.py 是 LLM 決定順序、事後用
estimate_minutes() 補真實車程；這裡反過來，車程本身就是排序演算法的核心輸入，
順序是算出來的，不是 LLM 決定的。兩條路徑刻意不共用邏輯（只共用 common/geo/ 底層）。

演算法：起訖點固定（使用者指定），中間點跑貪婪最近鄰構造 + 開放路徑 2-opt 局部搜尋，
把整趟行程當一條路徑一次排好，再依累計車程+停留時間把這條路徑切成連續的 N 天
（沖繩本島狹長近似一維地理，好的路徑本身就會像「由南到北掃過去」，切段幾乎等於
免費附贈地理分群效果，不需要另外跑 k-means 之類的分群演算法）。

已知限制（刻意不處理，非 bug）：不考慮開店時間、用餐時段、飯店 check-in/out 這類
時間窗限制，也不知道使用者每晚住哪裡——如果起訖點相同（例如同一個機場進出），
最優路徑可能會是「去程繞遠、回程再繞回來」，中間幾天在單一方向停留較久。
"""

import itertools
import re
from dataclasses import dataclass

from .geo_utils import haversine_km
from .highway_routing import load_network
from .travel_time import estimate_minutes

MAX_POINTS = 32  # 30 個景點上限 + 起點 + 可能的獨立終點；真正的硬上限（30筆景點）
                  # 由 backend/app/models.py 的 Pydantic Field(max_length=30) 執行，
                  # 這裡只是防呆（common/ 不該假設呼叫者一定守規矩）

MAX_DAY_PLAN_DAYS = 7  # evaluate_day_plan() 天序建議是窮舉全排列（n!），7天=5040種、
                        # 幾乎瞬間算完；再多天數複雜度會爆炸，所以這個功能天數上限比
                        # split_into_days() 用的那個 14 天上限低——這是刻意的、有理由的
                        # 硬上限，不是漏加，由 backend/app/models.py 的 DayPlanRequest 執行

_HOURS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*小時")
_MINUTES_RE = re.compile(r"(\d+(?:\.\d+)?)\s*分(?:鐘)?")


@dataclass(frozen=True)
class RoutePoint:
    id: str
    lat: float
    lng: float
    suggested_stay_minutes: float | None = None


@dataclass(frozen=True)
class Leg:
    from_id: str
    to_id: str
    minutes: float
    via: str
    detail: str


def parse_stay_minutes(duration_text: str | None) -> float | None:
    """粗略解析 suggested_stay_duration 自由文字（"約1.5小時"/"30分鐘"/"1小時30分"）成分鐘數。
    解析不出來回傳 None（不是 0，不能假裝知道）——只給 split_into_days() 內部平衡用，
    不是要精確到分鐘，是「大概半小時 vs 大概三小時」這種量級的區分，不對外顯示或
    當成事實填回任何欄位。
    """
    if not duration_text:
        return None

    total = 0.0
    matched = False

    hours_match = _HOURS_RE.search(duration_text)
    if hours_match:
        total += float(hours_match.group(1)) * 60
        matched = True

    minutes_match = _MINUTES_RE.search(duration_text)
    if minutes_match:
        total += float(minutes_match.group(1))
        matched = True

    return total if matched else None


def build_distance_matrix(points: list[RoutePoint]) -> tuple[list[list[float]], dict[tuple[int, int], dict]]:
    """回傳 (matrix, details)。matrix 是 N x N 分鐘矩陣，對角線 0。
    只算上三角（假設 A→B 車程約等於 B→A，estimate_minutes() 本身沒有建模單行道），
    鏡射填滿下三角——把 N≤32 情況下最多 ~992 次估算降到 ~496 次。

    details[(i, j)]（i<j）保留 estimate_minutes() 的完整回傳值（含 via/detail 說明文字），
    供 optimize_route() 排好順序後查表組 Leg，不用排序完再重算一次。
    """
    graph, interchanges = load_network()
    n = len(points)
    matrix = [[0.0] * n for _ in range(n)]
    details: dict[tuple[int, int], dict] = {}

    for i in range(n):
        for j in range(i + 1, n):
            result = estimate_minutes(
                points[i].lat, points[i].lng, points[j].lat, points[j].lng,
                interchanges, graph,
            )
            matrix[i][j] = result["minutes"]
            matrix[j][i] = result["minutes"]
            details[(i, j)] = result

    return matrix, details


def nearest_neighbor_path(matrix: list[list[float]], start_index: int, end_index: int | None = None) -> list[int]:
    """從 start_index 出發，每步貪婪選未拜訪中最近的一個，構造初始路徑。
    若指定 end_index，該點從貪婪候選中排除，最後才手動接上去，保證是路徑終點。
    回傳 matrix 索引的排列（長度 = len(matrix)）。
    """
    n = len(matrix)
    unvisited = set(range(n)) - {start_index}
    if end_index is not None:
        unvisited.discard(end_index)

    path = [start_index]
    current = start_index
    while unvisited:
        nxt = min(unvisited, key=lambda j: matrix[current][j])
        path.append(nxt)
        unvisited.remove(nxt)
        current = nxt

    if end_index is not None:
        path.append(end_index)

    return path


def _reversal_delta(path: list[int], matrix: list[list[float]], i: int, k: int, n: int) -> float:
    """反轉 path[i:k+1] 這段區間後，總車程會改變多少（負值代表變短）。"""
    before_old = matrix[path[i - 1]][path[i]]
    before_new = matrix[path[i - 1]][path[k]]

    if k == n - 1:
        # 反轉到路徑最尾端：尾端後面沒有邊要比較，只有「進入這段」的邊改變
        after_old = 0.0
        after_new = 0.0
    else:
        after_old = matrix[path[k]][path[k + 1]]
        after_new = matrix[path[i]][path[k + 1]]

    return (before_new + after_new) - (before_old + after_old)


def two_opt(path: list[int], matrix: list[list[float]], fixed_end: bool, max_passes: int = 200) -> list[int]:
    """開放路徑（非環狀）2-opt 局部搜尋。path[0] 永遠固定（起點，使用者指定，不可移動）；
    fixed_end=True 時 path[-1] 也固定（使用者指定終點），反轉範圍不可觸碰最後一個索引；
    fixed_end=False 時終點自由，反轉可以一路延伸到路徑最尾端。

    每輪掃描所有可行的 (i, k) 反轉組合，套用每個能縮短總長度的反轉（同一輪內找到就套用，
    不中斷重掃——delta 每次都是從目前的 path 現算，不是用快取，順序套用不會算錯），
    直到一整輪掃描都找不到改善或達到 max_passes。N≤32 時每輪 O(N^2)，成本可忽略。
    """
    path = list(path)
    n = len(path)
    if n < 4:
        return path

    max_k = (n - 2) if fixed_end else (n - 1)

    for _ in range(max_passes):
        improved = False
        for i in range(1, max_k):
            for k in range(i + 1, max_k + 1):
                delta = _reversal_delta(path, matrix, i, k, n)
                if delta < -1e-9:
                    path[i:k + 1] = path[i:k + 1][::-1]
                    improved = True
        if not improved:
            break

    return path


def optimize_route(points: list[RoutePoint], start_id: str, end_id: str | None = None) -> dict:
    """高階入口：組矩陣 → 最近鄰構造 → 2-opt 改善。
    回傳 {"order": [RoutePoint,...], "legs": [Leg,...], "total_minutes": float}
    legs 長度 = len(order) - 1，每個 leg 對應相鄰兩站的 estimate_minutes() 完整結果
    （含 via/detail），後續組 ItineraryStop.travel_time_from_prev 直接讀這裡，不重算。
    """
    if len(points) > MAX_POINTS:
        raise ValueError(f"景點數量超過上限（{MAX_POINTS}）")
    if len(points) < 2:
        raise ValueError("至少需要起點跟一個景點")

    id_to_index = {p.id: i for i, p in enumerate(points)}
    if start_id not in id_to_index:
        raise ValueError(f"start_id={start_id!r} 不在傳入的 points 裡")

    start_index = id_to_index[start_id]
    end_index = None
    if end_id is not None:
        if end_id not in id_to_index:
            raise ValueError(f"end_id={end_id!r} 不在傳入的 points 裡")
        end_index = id_to_index[end_id]
        if end_index == start_index:
            raise ValueError("start_id 跟 end_id 不能是同一點")

    matrix, details = build_distance_matrix(points)
    path = nearest_neighbor_path(matrix, start_index, end_index)
    path = two_opt(path, matrix, fixed_end=end_index is not None)

    ordered_points = [points[i] for i in path]
    legs: list[Leg] = []
    for a, b in zip(path, path[1:]):
        key = (a, b) if a < b else (b, a)
        detail = details[key]
        legs.append(Leg(
            from_id=points[a].id, to_id=points[b].id,
            minutes=detail["minutes"], via=detail["via"], detail=detail["detail"],
        ))

    total_minutes = sum(leg.minutes for leg in legs)
    return {"order": ordered_points, "legs": legs, "total_minutes": round(total_minutes, 1)}


def split_into_days(order: list[RoutePoint], legs: list[Leg], trip_days: int) -> list[list[RoutePoint]]:
    """把已排序好的單一路徑切成 trip_days 段連續子序列（不重新排序，只切分點）。

    每個點的平衡權重 = 進入該點的 leg 分鐘數 + 該點的 suggested_stay_minutes（None 視為 0，
    「不知道停多久」跟「這個點本來就不用停留時間」——例如虛擬的起訖錨點——由呼叫端在
    建 RoutePoint 時決定要不要填入預設值，這裡不做任何隱藏假設）。

    貪婪切分：沿路徑累加權重，一旦目前這天的累計權重達到 target = 總權重 / 有效天數，
    且切下去後剩餘的點還夠分給剩餘的天數（每天至少一點），就在此收工、開下一天
    （經典的貪婪換行演算法）。trip_days 超過景點數時，多出來的天數回傳空 list。
    """
    if trip_days <= 0:
        raise ValueError("trip_days 必須大於 0")

    n = len(order)
    if n == 0:
        return [[] for _ in range(trip_days)]

    weights = [0.0] * n
    for idx in range(1, n):
        weights[idx] = legs[idx - 1].minutes + (order[idx].suggested_stay_minutes or 0.0)

    effective_days = min(trip_days, n)
    target = sum(weights) / effective_days

    days: list[list[RoutePoint]] = []
    current_day: list[RoutePoint] = []
    current_weight = 0.0
    remaining_days = effective_days

    for idx in range(n):
        current_day.append(order[idx])
        current_weight += weights[idx]

        remaining_points = n - idx - 1
        remaining_slots = remaining_days - 1

        if (
            remaining_points > 0
            and remaining_slots > 0
            and current_weight >= target
            and remaining_points >= remaining_slots
        ):
            days.append(current_day)
            current_day = []
            current_weight = 0.0
            remaining_days -= 1

    days.append(current_day)

    while len(days) < trip_days:
        days.append([])

    return days


# ============================================================================
# 分天規劃：使用者自己決定每天要去哪些景點（不像上面 optimize_route+split_into_days
# 是丟一包讓演算法全權分天），這裡負責 1) 幫每天內部景點排最佳順序 2) 檢查使用者
# 選的天序（哪天先去）是不是最有效率，不是的話建議更好的天序——但天序建議只調換
# 「哪天先去」，不會把使用者選的景點搬到別天去（那是使用者自己的決定，不該被覆蓋）。
# ============================================================================


def day_centroid(points: list[RoutePoint]) -> tuple[float, float]:
    """一天所選景點的座標平均值（單純算術平均，不是加權），只用來快速比較「天序」
    好不好排，不是最終呈現的真實路線座標。"""
    lat = sum(p.lat for p in points) / len(points)
    lng = sum(p.lng for p in points) / len(points)
    return lat, lng


def best_day_order_by_centroid(
    day_buckets: list[list[RoutePoint]],
    start: RoutePoint,
    end: RoutePoint | None = None,
) -> list[int]:
    """窮舉 day_buckets 所有天序排列，用每天的重心座標算「起點→day1重心→day2重心→
    ...→終點」的總直線距離（haversine，不含高速公路，只是粗估排名用，避免每個排列
    都要跑一次昂貴的 estimate_minutes），回傳總距離最小的排列（day_buckets 的索引順序）。
    天數上限由呼叫端保證（MAX_DAY_PLAN_DAYS），這裡不重複檢查。
    """
    n = len(day_buckets)
    centroids = [day_centroid(bucket) for bucket in day_buckets]

    def total_distance(order: tuple[int, ...]) -> float:
        path = [(start.lat, start.lng)] + [centroids[i] for i in order]
        if end is not None:
            path.append((end.lat, end.lng))
        return sum(
            haversine_km(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1])
            for i in range(len(path) - 1)
        )

    best_order = tuple(range(n))
    best_distance = total_distance(best_order)
    for perm in itertools.permutations(range(n)):
        d = total_distance(perm)
        if d < best_distance:
            best_distance = d
            best_order = perm

    return list(best_order)


def chain_optimize_days(
    day_buckets: list[list[RoutePoint]],
    start: RoutePoint,
    end: RoutePoint | None = None,
) -> dict:
    """依 day_buckets 目前的順序（呼叫端已經決定好天序）逐天往前鏈接最佳化：
    第1天從 start 出發、自由選終點；第2天從第1天實際排出來的最後一站出發、一樣
    自由選終點；以此類推；最後一天如果有 end，終點鎖定在 end。每天內部景點順序
    重用 optimize_route()（NN + 2-opt）。

    是貪婪逐天鏈接、不是跨天聯合最佳化——每天決定「往哪邊收尾」時看不到後面幾天
    的安排，可能不是全域最優解，但比起真正聯合最佳化（NP-hard 的 clustered TSP）
    簡單很多，對 MVP 規模（每天數個景點、總天數 ≤ MAX_DAY_PLAN_DAYS）已經夠用。

    回傳 {"days": [[RoutePoint,...], ...], "legs": [Leg,...], "total_minutes": float}
    legs 是整趟行程攤平的相鄰站車程（含跨天銜接段），第一段從 start 出發算起。
    """
    result_days: list[list[RoutePoint]] = []
    all_legs: list[Leg] = []
    total_minutes = 0.0
    current_anchor = start

    for day_index, bucket in enumerate(day_buckets):
        is_last_day = day_index == len(day_buckets) - 1
        anchor_id = f"__day_anchor_{day_index}__"
        points = [RoutePoint(id=anchor_id, lat=current_anchor.lat, lng=current_anchor.lng, suggested_stay_minutes=0.0)]
        points.extend(bucket)

        end_id = None
        if is_last_day and end is not None:
            points.append(RoutePoint(id="__end__", lat=end.lat, lng=end.lng, suggested_stay_minutes=0.0))
            end_id = "__end__"

        day_result = optimize_route(points, start_id=anchor_id, end_id=end_id)
        day_order = [p for p in day_result["order"] if p.id not in (anchor_id, "__end__")]
        day_legs = list(day_result["legs"])

        # 第一段 leg 是「虛擬錨點 -> 這天第一個真實景點」，錨點只是座標複製品
        # （跟前一天最後一站或 start 座標相同），把 from_id 換成真正的那個點，
        # 顯示上才接得起來（不會出現 __day_anchor_1__ 這種內部 id）
        if day_legs:
            first = day_legs[0]
            day_legs[0] = Leg(from_id=current_anchor.id, to_id=first.to_id,
                               minutes=first.minutes, via=first.via, detail=first.detail)

        result_days.append(day_order)
        all_legs.extend(day_legs)
        total_minutes += sum(leg.minutes for leg in day_legs)

        if day_order:
            current_anchor = day_order[-1]
        # 這天理論上不會沒有真實景點（呼叫端會擋掉空 bucket），萬一發生就沿用
        # 上一個錨點，下一天直接從同一個點接續，不會壞掉

    return {"days": result_days, "legs": all_legs, "total_minutes": round(total_minutes, 1)}


def evaluate_day_plan(
    day_buckets: list[list[RoutePoint]],
    start: RoutePoint,
    end: RoutePoint | None = None,
) -> dict:
    """幫「使用者已經自己分好每天要去的景點」評分：照使用者指定的天序算一次精確結果，
    再用重心距離找一個理論上更好的天序候選、也算一次精確結果，兩個一比——只有當候選
    天序真的比較省（省超過 1 分鐘，避免雜訊等級的差異也拿出來講）才會建議，且建議只
    調整「哪天先去」，每天內部的景點組合完全不變。

    回傳 {
      "chosen": {"days": [...], "legs": [...], "total_minutes": float},
      "suggested_order": list[int] | None,   # None 代表使用者選的天序已經是最好的
      "suggested": {...} | None,
      "minutes_saved": float,
    }
    """
    chosen = chain_optimize_days(day_buckets, start, end)

    if len(day_buckets) < 2:
        return {"chosen": chosen, "suggested_order": None, "suggested": None, "minutes_saved": 0.0}

    candidate_order = best_day_order_by_centroid(day_buckets, start, end)
    if candidate_order == list(range(len(day_buckets))):
        return {"chosen": chosen, "suggested_order": None, "suggested": None, "minutes_saved": 0.0}

    reordered_buckets = [day_buckets[i] for i in candidate_order]
    suggested = chain_optimize_days(reordered_buckets, start, end)
    minutes_saved = round(chosen["total_minutes"] - suggested["total_minutes"], 1)

    if minutes_saved <= 1.0:
        return {"chosen": chosen, "suggested_order": None, "suggested": None, "minutes_saved": 0.0}

    return {
        "chosen": chosen,
        "suggested_order": candidate_order,
        "suggested": suggested,
        "minutes_saved": minutes_saved,
    }
