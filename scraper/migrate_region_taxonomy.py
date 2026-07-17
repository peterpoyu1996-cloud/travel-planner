"""一次性遷移腳本：把舊的 region_group（那霸市區/中部（美國村）等自由文字）
改成標準沖繩本島三分法（北部/中部/南部），細節搬到新的 sub_area 欄位。
邊界定義見 data/schema.md「region_group 分界」。

這是遷移用的一次性腳本，跑過一次、資料改完就不需要再跑，之後新資料
（scraper/ingest_osm.py）直接用正確的三分法寫入，不會再需要這支腳本。
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

OLD_TO_NEW = {
    "北部": ("北部", None),
    "中部": ("中部", None),
    "中部（美國村）": ("中部", "美國村"),
    "那霸市區": ("南部", None),
    "那霸市區（瀨長島）": ("南部", "瀨長島"),
}


def migrate_file(filename: str) -> None:
    path = DATA_DIR / filename
    entries = json.loads(path.read_text(encoding="utf-8"))

    for entry in entries:
        old = entry.get("region_group")
        if old not in OLD_TO_NEW:
            print(f"[migrate] 警告：{entry.get('id')} 的 region_group='{old}' 不在對照表中，跳過")
            continue
        new_region, sub_area = OLD_TO_NEW[old]
        entry["region_group"] = new_region
        if "sub_area" not in entry:
            entry["sub_area"] = sub_area
        print(f"[migrate] {entry['id']}: {old} -> region_group={new_region}, sub_area={sub_area}")

    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[migrate] 寫回 {path}")


def main() -> None:
    for filename in ("attractions.json", "hotels.json", "restaurants.json"):
        migrate_file(filename)


if __name__ == "__main__":
    main()
