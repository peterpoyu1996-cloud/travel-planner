"""B 級來源：官方觀光局/景點官網。範例骨架，尚未指定實際目標網址。

使用方式：
1. 先確認目標網站屬於 B 級（ToS 未明文禁止爬蟲），不可用於 C 級網站
   （Google Maps / Tripadvisor / 食べログ / Booking.com / Agoda 等，見 docs/ARCHITECTURE.md 第4節）
2. 每個網域呼叫前先 can_fetch() 檢查 robots.txt
3. 每個請求前呼叫 throttle() 控制頻率

TODO: 確定要爬的官網清單（例：沖繩觀光會議局 OCVB 官網）後，
      在 fetch_page() 針對該網站的 HTML 結構寫解析邏輯。
"""

import requests
from bs4 import BeautifulSoup

from robots_check import USER_AGENT, can_fetch, throttle


def fetch_page(url: str) -> BeautifulSoup | None:
    domain = url.split("/")[2]

    if not can_fetch(url):
        print(f"[official_sites] robots.txt 不允許擷取: {url}，略過")
        return None

    throttle(domain)
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


if __name__ == "__main__":
    # 範例：確認 robots.txt 檢查機制可用（尚未接上實際解析邏輯）
    test_url = "https://www.okinawastory.jp/"
    soup = fetch_page(test_url)
    if soup:
        print(f"[official_sites] 成功讀取 {test_url}，title: {soup.title.string if soup.title else 'N/A'}")
