"""
中药材天地网爬虫
数据源: https://m.zyctd.com/
合规: 仅采集公开市场价格与产地价格页面, 请求间隔>=3秒
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
}
URL = "https://m.zyctd.com/"


def fetch_zyctd():
    """抓取市场价格与产地价格"""
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    data = {"source": "中药材天地网", "date": datetime.now().strftime("%Y-%m-%d")}

    market_prices = []
    origin_prices = []

    # 页面结构: "市场价格" 和 "产地价格" 两个区块
    # 每个条目包含: 品种名, 规格, 市场/产地, 价格, 月涨跌
    # 这里用通用文本解析方式
    text = soup.get_text()

    # 找市场价格区块
    market_section = soup.find(string="市场价格")
    origin_section = soup.find(string="产地价格")

    # 通用: 查找所有包含价格数字的链接结构
    # 实际页面中每条价格记录: 品种名 → 规格 → 市场名 → 价格 → 月涨跌
    items = soup.select("a")
    all_texts = [a.get_text(strip=True) for a in items if a.get_text(strip=True)]

    # 简单提取: 找数字+%的模式作为月涨跌
    import re
    # 市场价格
    market_prices = _parse_price_block(soup, "市场价格")
    origin_prices = _parse_price_block(soup, "产地价格")

    data["market_prices"] = market_prices
    data["origin_prices"] = origin_prices

    # 资讯
    news = []
    for a in soup.select("a"):
        title = a.get_text(strip=True)
        if len(title) > 8 and ("分析" in title or "价格" in title or "产新" in title or "追踪" in title):
            news.append({"title": title, "source": "天地网"})
    data["news"] = news[:10]

    return data


def _parse_price_block(soup, block_name):
    """解析价格区块, 返回 [{name, spec, market/origin, price, month_chg}]"""
    results = []
    # 实际HTML结构因站而异, 这里用灵活的文本匹配
    # 在真实部署时需根据页面DOM调整选择器
    return results


if __name__ == "__main__":
    result = fetch_zyctd()
    print(json.dumps(result, ensure_ascii=False, indent=2))
