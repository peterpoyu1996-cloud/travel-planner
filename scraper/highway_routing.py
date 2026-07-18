"""高速公路網路的圖論最短路徑，算「交流道到交流道實際沿路開多遠」。

為什麼不能只用交流道座標直接算 haversine：沖繩自動車道不是直線，交流道到交流道
中間會繞路，而且交流道有分支（那覇空港自動車道、沖縄西海岸道路），直接用緯度排序
逼近會在分支路段算錯。用路段幾何建圖、跑最短路徑，才能正確處理分支。

做法：把 data/highway_network.json 的每段路 segments 拆成一串節點，相鄰節點連邊
（邊權重 = haversine 距離），節點座標四捨五入到小數點後5位（約1公尺誤差）當作
合併同一個實體交叉點的 key——OSM 的路段在交流道等交叉點本來就會共用同一個節點
座標，用四捨五入後的座標當 key 剛好可以把不同路段在同一個交叉點自然接起來。
"""

import heapq
import json
from pathlib import Path

from geo_utils import haversine_km

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

NodeKey = tuple[float, float]


def _key(lat: float, lon: float) -> NodeKey:
    return (round(lat, 5), round(lon, 5))


def load_network() -> tuple[dict[NodeKey, list[tuple[NodeKey, float]]], list[dict]]:
    """回傳 (graph, interchanges)。graph 是 node_key -> [(neighbor_key, distance_km), ...]。"""
    data = json.loads((DATA_DIR / "highway_network.json").read_text(encoding="utf-8"))

    graph: dict[NodeKey, list[tuple[NodeKey, float]]] = {}
    for segment in data["segments"]:
        points = segment["points"]
        for i in range(len(points) - 1):
            a = _key(*points[i])
            b = _key(*points[i + 1])
            if a == b:
                continue
            dist = haversine_km(a[0], a[1], b[0], b[1])
            graph.setdefault(a, []).append((b, dist))
            graph.setdefault(b, []).append((a, dist))

    return graph, data["interchanges"]


def nearest_node_key(lat: float, lon: float, graph: dict[NodeKey, list]) -> NodeKey | None:
    """找離 (lat, lon) 最近的圖節點。交流道座標通常就是路段節點本身，
    但取平均座標合併同名交流道後可能有微小誤差，所以還是要找最近的，不能直接四捨五入配對。
    """
    best_key, best_dist = None, float("inf")
    for key in graph:
        dist = haversine_km(lat, lon, key[0], key[1])
        if dist < best_dist:
            best_key, best_dist = key, dist
    return best_key


def dijkstra(graph: dict[NodeKey, list[tuple[NodeKey, float]]], start: NodeKey) -> dict[NodeKey, float]:
    dist = {start: 0.0}
    visited = set()
    heap = [(0.0, start)]

    while heap:
        d, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)

        for neighbor, weight in graph.get(node, []):
            nd = d + weight
            if nd < dist.get(neighbor, float("inf")):
                dist[neighbor] = nd
                heapq.heappush(heap, (nd, neighbor))

    return dist


def highway_distance_km(
    ic_a: dict, ic_b: dict, graph: dict[NodeKey, list[tuple[NodeKey, float]]]
) -> float | None:
    """算兩個交流道之間沿著高速公路網路走的實際距離。找不到路徑（理論上不會，
    因為都在同一個連通的路網上）回傳 None。"""
    key_a = nearest_node_key(ic_a["lat"], ic_a["lng"], graph)
    key_b = nearest_node_key(ic_b["lat"], ic_b["lng"], graph)
    if key_a is None or key_b is None:
        return None

    distances = dijkstra(graph, key_a)
    return distances.get(key_b)
