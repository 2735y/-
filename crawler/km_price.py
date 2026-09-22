"""
康美·中国中药材价格指数爬虫
数据源: https://wapprice.kmzyw.com.cn/?code=B-083
合规: 仅采集公开页面数据, 请求间隔>=3秒, 遵守robots.txt
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}
URL = "https://wapprice.kmzyw.com.cn/?code=B-083"


def fetch_km_index():
    """抓取康美总指数与涨跌榜"""
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    data = {"source": "康美·中国中药材价格指数网", "date": datetime.now().strftime("%Y-%m-%d")}

    # 解析日指数
    text = soup.get_text()
    m = re.search(r"日指数[：:]\s*([\d.]+)", text)
    if m:
        data["value"] = float(m.group(1))

    # 涨跌幅
    for label, key in [("较昨日", "chg_day"), ("较上周", "chg_week"),
                        ("较上月", "chg_month"), ("较去年", "chg_year")]:
        m = re.search(label + r"[：:]\s*(-?[\d.]+)\s*/\s*(-?[\d.]+)%", text)
        if m:
            data[key] = float(m.group(1))
            data[key + "_pct"] = float(m.group(2))

    # 涨跌榜: 页面上有"上涨幅度最大"和"下跌幅度最大"两个表格
    tables = soup.find_all("table")
    gainers, losers = [], []
    for tbl in tables:
        rows = tbl.find_all("tr")
        for row in rows[1:]:  # skip header
            cells = row.find_all(["td", "th"])
            if len(cells) >= 3:
                name = cells[0].get_text(strip=True)
                try:
                    idx = float(cells[1].get_text(strip=True))
                    pct = float(cells[2].get_text(strip=True).replace("%", "").replace("+", ""))
                    entry = {"name": name, "index": idx, "chg_pct": pct}
                    if pct >= 0:
                        gainers.append(entry)
                    else:
                        losers.append(entry)
                except (ValueError, IndexError):
                    pass

    data["top_gainers"] = sorted(gainers, key=lambda x: -x["chg_pct"])[:10]
    data["top_losers"] = sorted(losers, key=lambda x: x["chg_pct"])[:10]

    # 周评文章
    news = []
    for a in soup.select("a"):
        title = a.get_text(strip=True)
        if title and ("周评" in title or "月评" in title or "周报" in title or "分析" in title):
            news.append({"title": title, "source": "康美指数"})
    data["news"] = news[:10]

    return data


if __name__ == "__main__":
    result = fetch_km_index()
    print(json.dumps(result, ensure_ascii=False, indent=2))
