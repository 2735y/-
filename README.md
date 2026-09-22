# 中药材行情看板

零成本自动采集的中药材数据看板。每日18:00自动采集公开行情数据，静态页面展示。

## 项目结构

```
├── index.html              # 看板前端 (自包含, ECharts CDN)
├── data/
│   ├── latest.json         # 最新数据 (爬虫生成)
│   └── history/            # 每日快照
├── crawler/
│   ├── km_price.py         # 康美指数爬虫
│   ├── zyctd_price.py      # 天地网爬虫
│   └── run_all.py          # 主入口
├── .github/workflows/
│   └── daily-crawl.yml     # GitHub Actions 定时任务
└── requirements.txt
```

## 本地运行

```bash
pip install -r requirements.txt
python crawler/run_all.py
```

直接用浏览器打开 `index.html` 即可预览（内置示例数据）。

## 部署到GitHub Pages

1. 创建GitHub仓库并push代码
2. Settings → Pages → 选择 `main` 分支根目录
3. Actions → 启用 workflow（每日18:00自动采集并push新数据）
4. 访问 `https://用户名.github.io/仓库名/`

## 合规说明

- 仅采集公开页面数据，不触碰登录墙与付费会员内容
- 遵守robots协议，请求间隔≥3秒
- 数据来源标注于页面底部
- 仅供参考，不构成投资建议
