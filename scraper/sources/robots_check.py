"""B 級來源爬蟲共用工具：抓官網前先檢查 robots.txt、控制請求間隔。
任何 official_sites.py 內的爬蟲都應該先呼叫 can_fetch() 確認允許再發送請求。
"""

import time
import urllib.robotparser as robotparser
from urllib.parse import urlparse

USER_AGENT = "travel-planner-okinawa-mvp/0.1 (+personal portfolio project, low volume)"
MIN_INTERVAL_SECONDS = 2.0

_last_request_time: dict[str, float] = {}


def can_fetch(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        # 讀不到 robots.txt 時保守處理：視為不允許，改人工檢查
        return False

    return rp.can_fetch(USER_AGENT, url)


def throttle(domain: str) -> None:
    """確保對同一網域的請求間隔至少 MIN_INTERVAL_SECONDS。"""
    now = time.monotonic()
    last = _last_request_time.get(domain, 0.0)
    wait = MIN_INTERVAL_SECONDS - (now - last)
    if wait > 0:
        time.sleep(wait)
    _last_request_time[domain] = time.monotonic()
