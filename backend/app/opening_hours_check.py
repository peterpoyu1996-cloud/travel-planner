"""粗略檢查候選的 opening_hours 有沒有整天都不營業，跟行程當天是星期幾比對。

只做「星期幾層級」的檢查（例如「Mo,Su,PH off」代表週一週日公休），沒辦法做到
「同一天不同時段」的比對（例如平日只有晚餐、假日才有午餐這種）——因為 Stop
目前沒有結構化的「預計到達時間」欄位，只有自由文字的 suggested_stay_duration，
沒辦法可靠解析出具體時刻。這塊留著，等之後真的加了到站時間欄位再處理。

解析範圍限於常見 OSM opening_hours 語法的星期代碼（Mo/Tu/We/Th/Fr/Sa/Su，
PH 直接忽略不特別處理，因為節日通常會跟六日一起列，不影響星期覆蓋範圍判斷）。
遇到看不懂的格式（例如純中文季節說明、完全沒有星期資訊的時段）一律當作
「沒有資訊、不擋」，不要因為解析失敗就亂發警告。
"""

import re
from datetime import date

_DAY_TOKENS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
_DAY_INDEX = {d: i for i, d in enumerate(_DAY_TOKENS)}
_DAY_PATTERN = re.compile(r"\b(Mo|Tu|We|Th|Fr|Sa|Su|PH)\b")
_WEEKDAY_NAMES = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def _parse_day_set(day_part: str) -> set[int]:
    """把 'Mo-Fr' / 'Sa,Su,PH' / 'Tu-We, Fr-Su' 這種片段轉成星期索引集合(0=一...6=日)。PH忽略。"""
    days: set[int] = set()
    for m in re.finditer(r"(Mo|Tu|We|Th|Fr|Sa|Su)-(Mo|Tu|We|Th|Fr|Sa|Su)", day_part):
        start, end = _DAY_INDEX[m.group(1)], _DAY_INDEX[m.group(2)]
        i = start
        while True:
            days.add(i)
            if i == end:
                break
            i = (i + 1) % 7
    remainder = re.sub(r"(Mo|Tu|We|Th|Fr|Sa|Su)-(Mo|Tu|We|Th|Fr|Sa|Su)", "", day_part)
    for tok in re.finditer(r"Mo|Tu|We|Th|Fr|Sa|Su", remainder):
        days.add(_DAY_INDEX[tok.group(0)])
    return days


def closed_weekday_warning(name: str, opening_hours: str | None, visit_date: date | str) -> str | None:
    """回傳一句警告文字，如果 opening_hours 顯示 visit_date 那個星期幾整天公休；
    看不懂格式或沒有星期資訊就回傳 None（不擋、不亂猜）。
    """
    if not opening_hours:
        return None
    if isinstance(visit_date, str):
        try:
            visit_date = date.fromisoformat(visit_date)
        except ValueError:
            return None
    weekday = visit_date.weekday()

    segments = re.split(r"[;｜|]", opening_hours)
    open_days: set[int] = set()
    closed_days: set[int] = set()
    found_any_day_token = False

    for seg in segments:
        seg = seg.strip()
        if not _DAY_PATTERN.search(seg):
            continue
        found_any_day_token = True
        day_part_match = re.match(r"^[A-Za-z,\-\s]+", seg)
        if not day_part_match:
            continue
        days = _parse_day_set(day_part_match.group(0))
        if re.search(r"\boff\b", seg, re.IGNORECASE):
            closed_days |= days
        else:
            open_days |= days

    if not found_any_day_token:
        return None  # 沒有星期資訊，當作每天都營業，不擋
    if not open_days:
        return None  # 只看到 off 規則、沒有基準營業日，資訊不足以判斷，不擋

    covered = open_days - closed_days
    if weekday not in covered:
        return (
            f"「{name}」的營業時間資料（{opening_hours}）顯示 {_WEEKDAY_NAMES[weekday]}"
            f"（{visit_date}）可能公休，行前請務必查證。"
        )
    return None
