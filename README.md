# Invest Hub · 全球投资信息中心

> 全球市场每日追踪 + 趋势研报 · 自动化采集 · 静态站点

## 简介

Invest Hub 是一个**每日自动化的全球投资信息收集 + 静态站点生成**项目。

每天会做这些事：
1. **收菜** A 股、港股、美股、加密、大宗商品今日热点
2. **整理** 资金流向、机构观点、宏观政策
3. **写** 未来 1-3 个月趋势研报
4. **生成** 可浏览的静态站点（`site/` 目录）

## 项目结构

```
invest-hub/
├── knowledge-base/          # 原始 markdown 知识库
│   ├── A股/                 # A 股日报
│   ├── 港股/                # 港股日报
│   ├── 美股/                # 美股日报
│   ├── 加密货币/            # 加密日报
│   ├── 大宗商品/            # 大宗日报
│   ├── 宏观政策/            # 宏观政策
│   ├── 趋势研报/            # 未来 1-3 个月展望
│   └── YYYY-MM-DD-今日综合分析.md
├── scripts/
│   └── build_site.py        # 把 markdown 转成 html
└── site/                    # 静态站点（可部署到 GitHub Pages）
    ├── index.html           # 入口
    ├── style.css            # 样式
    └── knowledge-base/      # 文档
```

## 重要声明

⚠️ **本项目所有内容均为信息整理，不构成任何投资建议。**
- 投资有风险，决策需谨慎
- 任何因参考本项目内容造成的损失，与项目作者无关

## 数据来源

- 东方财富、新浪财经、腾讯财经
- 券商研报（中信、中金、华泰等）
- 机构观点（摩根士丹利、高盛、瑞银等）
- 公开媒体（财联社、Wind 等）

## 部署

### 本地浏览

```
cd site
python3 -m http.server 8000
# 访问 http://localhost:8000
```

### 部署到 GitHub Pages

1. 推送代码到 GitHub
2. Settings → Pages → Source 选择 `main` 分支 + `/site` 目录
3. 等待几分钟即可访问

### 重新生成站点

```
python3 scripts/build_site.py
```

## 更新方式

- **手动模式**：每天收盘后执行 `python3 scripts/build_site.py`
- **自动模式**：配合 GitHub Actions 每天定时执行

## 贡献

欢迎提交 PR 补充：
- 新的数据源
- 更好的分析维度
- 改进的样式

## License

MIT
