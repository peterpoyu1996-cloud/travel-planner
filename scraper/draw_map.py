"""畫沖繩本島的知識庫地圖：高速公路（粗曲線）＋交流道（開口標記）＋
所有景點/飯店/餐廳/海灘（點）＋比例尺。純視覺化用途，不影響 travel_time.py
的實際計算（那支是算出來的數字，這支只是把資料畫出來方便肉眼檢查）。

經緯度不是等距的（同樣1度，經度在沖繩緯度大約只有緯度的90%長），
畫圖時用 ax.set_aspect() 依緯度修正，不然地圖會被拉扁/拉長。
"""

import json
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_PATH = DATA_DIR.parent / "docs" / "assets" / "okinawa_knowledge_map.png"

REFERENCE_LAT = 26.5  # 沖繩本島大致中間緯度，拿來算經度縮放跟比例尺

CATEGORY_STYLE = {
    "attraction": {"color": "#2563eb", "label": "景點"},
    "hotel": {"color": "#16a34a", "label": "飯店"},
    "restaurant": {"color": "#ea580c", "label": "餐廳"},
}

# 中文字型：Windows 內建的微軟正黑體，找不到就靜靜跳過中文標籤（不讓整支腳本壞掉）
for font_name in ("Microsoft JhengHei", "Microsoft YaHei", "MingLiU"):
    if font_name in {f.name for f in plt.matplotlib.font_manager.fontManager.ttflist}:
        plt.rcParams["font.sans-serif"] = [font_name]
        plt.rcParams["axes.unicode_minus"] = False
        break


def load_pois() -> list[dict]:
    pois = []
    for filename in ("attractions.json", "hotels.json", "restaurants.json"):
        data = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        pois.extend(data)
    return [p for p in pois if p.get("lat") is not None and p.get("lng") is not None]


def load_highway() -> dict:
    return json.loads((DATA_DIR / "highway_network.json").read_text(encoding="utf-8"))


def draw() -> None:
    pois = load_pois()
    highway = load_highway()

    fig, ax = plt.subplots(figsize=(10, 14), dpi=150)

    # 經度方向縮放係數：同樣1度經度在這個緯度實際距離 = cos(緯度) * 1度緯度的距離
    lon_scale = math.cos(math.radians(REFERENCE_LAT))
    ax.set_aspect(1 / lon_scale)

    # 高速公路路段（粗曲線）
    for seg in highway["segments"]:
        lats = [p[0] for p in seg["points"]]
        lons = [p[1] for p in seg["points"]]
        width = 3.2 if seg["highway"] == "motorway" else 1.8
        ax.plot(lons, lats, color="#dc2626", linewidth=width, solid_capstyle="round", zorder=3, alpha=0.85)

    # 交流道（開口標記：白底黑框圓點，疊在紅線上看起來像路上開了個口）
    for ic in highway["interchanges"]:
        ax.scatter(ic["lng"], ic["lat"], s=70, facecolor="white", edgecolor="black", linewidth=1.2, zorder=4)

    # 景點/飯店/餐廳
    for category, style in CATEGORY_STYLE.items():
        xs = [p["lng"] for p in pois if p["category"] == category]
        ys = [p["lat"] for p in pois if p["category"] == category]
        ax.scatter(xs, ys, s=14, color=style["color"], alpha=0.75, zorder=2, label=style["label"])

    # 比例尺（畫在左下角，長度對應10公里）
    km_per_degree_lon = 111.32 * lon_scale
    bar_km = 10
    bar_deg_lon = bar_km / km_per_degree_lon
    x0, y0 = ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.06, ax.get_ylim()[0] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.04
    ax.plot([x0, x0 + bar_deg_lon], [y0, y0], color="black", linewidth=2.5, zorder=5)
    ax.text(x0 + bar_deg_lon / 2, y0 + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.012, f"{bar_km} km",
            ha="center", va="bottom", fontsize=9, zorder=5)

    ax.set_title("沖繩本島知識庫地圖：高速公路＋景點/飯店/餐廳分布", fontsize=13)
    ax.set_xlabel("經度")
    ax.set_ylabel("緯度")

    legend_elements = [
        Line2D([0], [0], color="#dc2626", lw=3, label="高速公路"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white", markeredgecolor="black", markersize=8, label="交流道"),
    ] + [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=s["color"], markersize=7, label=s["label"])
        for s in CATEGORY_STYLE.values()
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=9)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT_PATH)
    print(f"[draw_map] 已存檔：{OUT_PATH}（{len(pois)} 個POI，{len(highway['interchanges'])} 個交流道）")


if __name__ == "__main__":
    draw()
