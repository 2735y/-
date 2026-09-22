"""
主采集入口: 每日18:00由GitHub Actions触发
合并各数据源 → 生成 data/latest.json → 追加到 data/history/
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def safe_fetch(module_name, fetch_func):
    """单个采集器失败不影响其他"""
    try:
        print(f"[采集] {module_name} ...")
        result = fetch_func()
        print(f"[成功] {module_name}, 字段数: {len(result)}")
        return result
    except Exception as e:
        print(f"[失败] {module_name}: {e}")
        return None


def main():
    # 1. 采集康美指数
    from km_price import fetch_km_index
    km = safe_fetch("康美指数", fetch_km_index)

    # 2. 采集天地网
    from zyctd_price import fetch_zyctd
    zyctd = safe_fetch("天地网", fetch_zyctd)

    # 3. 合并数据
    merged = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "crawled_at": datetime.now().isoformat(),
        "index": km or {},
        "top_gainers": (km or {}).get("top_gainers", []),
        "top_losers": (km or {}).get("top_losers", []),
        "market_prices": (zyctd or {}).get("market_prices", []),
        "origin_prices": (zyctd or {}).get("origin_prices", []),
        "news": [],
    }
    if km and km.get("news"):
        merged["news"].extend(km["news"])
    if zyctd and zyctd.get("news"):
        merged["news"].extend(zyctd["news"])

    # 4. 读取历史索引并追加
    history_path = os.path.join(DATA_DIR, "latest.json")
    prev = {}
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            prev = json.load(f)

    # 合并历史指数序列
    hist = prev.get("history_index", [])
    if merged["index"].get("value"):
        today_val = merged["index"]["value"]
        today_str = merged["date"]
        # 去重: 同一天覆盖
        hist = [h for h in hist if h["date"] != today_str]
        hist.append({"date": today_str, "value": today_val})
        hist.sort(key=lambda x: x["date"])
        # 只保留最近90天
        merged["history_index"] = hist[-90:]

    # 5. 写入 latest.json
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"[输出] {history_path}")

    # 6. 保存当日快照到 history/
    history_dir = os.path.join(DATA_DIR, "history")
    os.makedirs(history_dir, exist_ok=True)
    snapshot_path = os.path.join(history_dir, f"{merged['date']}.json")
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"[快照] {snapshot_path}")

    # 7. 数据质量检查
    issues = []
    if not merged["index"].get("value"):
        issues.append("总指数未获取")
    if not merged["top_gainers"]:
        issues.append("涨幅榜为空")
    if issues:
        print(f"[警告] 数据质量: {issues}")
    else:
        print("[完成] 数据质量检查通过")


if __name__ == "__main__":
    main()
