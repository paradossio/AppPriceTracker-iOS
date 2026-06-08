# 🌍 AppPriceTracker-iOS · App Store 全球比价工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey.svg)]()
[![Version](https://img.shields.io/badge/version-2.1-blue.svg)]()

**中文 · [English](README_EN.md)**

**实测可拿到 ChatGPT Plus / Pro / Spotify / Notion / Bumble 等任意 App 的全球订阅价格。**

> 双击启动器 → 浏览器自动打开 → 搜索 App → 一键看 175 个国家的订阅价格对比

## 🆕 V2.1 新功能 (2026-06)

- 📈 **历史价格折线图**（180 天周期，每次查询自动累积快照，多国多线 + 悬停 tooltip）
- 📊 **家族大表**：一张表横向看 ChatGPT Plus/Pro/Go 在 30 国全部价格 (热力图色)
- ⚖️ **多 App 横向对比**：监控列表多选 → 为每 App 选订阅 → 跨 App 跨国大表 (如 ChatGPT vs YouTube vs Notion)
- 🌐 **中英双语 UI 切换**（保存到 localStorage）
- 🎯 **SKU 名称校准**：跨国对齐主键改用 `iapId`（Apple salableAdamId 全球唯一），显示名优先英文区 canonical
- 🔍 **SKU 模糊搜索**：YouTube 31 个内购也能秒筛（支持中英文、全文匹配，如 "plus" / "月付" / "premium"）

## 📸 效果

| 内购订阅跨国对比 | 关键指标 |
|---|---|
| ChatGPT Plus 月付：🇹🇷 土耳其 ₺499 ≈ ¥73 / 🇪🇸 西班牙 €22.99 ≈ ¥179 | 价差 **144%** |
| ChatGPT Pro 20x 月付：🇹🇷 ₺7999 ≈ ¥1175 / 🇪🇸 €229 ≈ ¥1786 | 价差 **52%** |

## 📦 文件清单

| 文件 | 说明 |
|---|---|
| `AppPriceTracker.py` | 后端（Python 标准库，零依赖）|
| `AppPriceTracker.html` | 前端（中文 UI、175 国、暗色模式自适应）|
| `启动 (macOS).command` | macOS 双击启动 |
| `启动 (Windows).bat` | Windows 双击启动 |

## 🚀 使用方法

### macOS
1. 下载本仓库 ZIP（绿色 `Code` 按钮 → `Download ZIP`），解压
2. 进入 `AppPriceTracker-iOS-main/` 文件夹
3. 双击 **`启动 (macOS).command`**
   - 首次双击如果系统提示"无法打开"，右键 → 打开 → 确认即可
4. 浏览器自动打开 `http://localhost:8765`
5. 关闭：在终端窗口按 **Ctrl+C**

### Windows
1. 下载并解压本仓库 ZIP
2. 进入 `AppPriceTracker-iOS-main\` 文件夹
3. 双击 **`启动 (Windows).bat`**
4. 浏览器自动打开
5. 关闭：直接关掉 cmd 黑窗口

### 系统要求
- **Python 3.7+**
  - macOS：`python3 --version` 检查（系统通常自带）
  - Windows：[python.org](https://www.python.org/downloads/) 下载，安装时务必勾选 ✅ "Add Python to PATH"
- 不需要 `pip install` 任何东西，纯标准库

## ✨ 功能

### 💎 内购 / 订阅模式（核心）
- 自动并发查询 30 国（可改为全部 175 国）的所有 IAP
- 按订阅产品分类：ChatGPT Plus / Pro / Go / Plus 年付 …
- 切换不同订阅看跨国比价
- 每国显示原币价、折算 CNY/USD、与最低价的百分比差
- 实测准确：与 App Store 当前实时价格一致

### 📱 应用本身价格模式
- 一次性买断价格（适合 Minecraft、Procreate 等付费 App）

### 🛠 通用功能
- 监控列表（localStorage 持久化）
- CSV 导出 / 表格复制
- 暗色模式自动跟随系统
- 实时汇率（ECB 数据，每日更新）

## 🎯 推荐试用

| 应用 | App ID | 看点 |
|---|---|---|
| ChatGPT | 6448311069 | Plus / Go / Pro 多档订阅 |
| Spotify | 324684580 | 全球 Premium 价差 |
| Notion | 1232780281 | Personal Pro 订阅 |
| Bumble | 930441707 | Boost / Premium |
| YouTube | 544007664 | YT Premium 订阅 |
| Tinder | 547702041 | Plus / Gold / Platinum |

## 🔧 技术原理

### 数据源
1. **iTunes Search API** — 应用搜索 + 应用本身价格（公开免费）
2. **`apps.apple.com/api/apps/v1/...`** — App Store 网页内部用的 API
   - same-origin 限制，所以**必须有本地后端**做转发
   - 不需要 token、不被 IP 区域重定向、不需要 cookie
   - 这是浏览器纯前端做不到的关键原因
3. **`@fawazahmed0/currency-api`** — 汇率（CDN 缓存、ECB 数据、CORS-enabled）

### 架构
```
浏览器 (UI) ←→ http://localhost:8765 (Python 后端) ←→ Apple APIs
   ↑
浏览器 localStorage 存监控列表 + 历史价格 + 设置
```

后端约 200 行 Python（`http.server` + `urllib`），前端约 800 行 HTML + JS（无外部库依赖）。

## ⚠️ 注意事项

- **同时只能跑一个实例**（端口 8765 占用）
- **iTunes API 限速 ~20 calls/min**：默认并发 5，30 国查询 ~10 秒
- **某些区域显示"未上架"是真实情况**（如 ChatGPT Pro 在中国大陆/香港未上架）
- **数据精确到原币种**，跨国比价用实时汇率换算（汇率每 6 小时刷新一次）

## 🐛 常见问题

**Q: 端口被占用？**
编辑 `AppPriceTracker.py` 第 22 行 `PORT = 8765`，改成其他端口（如 8766）。

**Q: 公司网络拦截了某个 API？**
查看启动窗口的报错。如果是 `apps.apple.com` 被拦截，订阅查询会失败但应用本身价格还能用。

**Q: macOS 提示"未签名"？**
右键文件 → 打开 → 在弹出的安全提示里点"打开"。这个项目本地运行不联网你的数据，可以放心用。

**Q: 换 App 之后查询很慢？**
正常。30 国 × 1 个 API 调用 = 30 次请求，并发 5 路约 8-15 秒。

## 📜 License

[MIT](LICENSE) © 2026 paradossio

## 🙏 致谢

- [Apple iTunes Search API](https://performance-partners.apple.com/search-api) — 应用搜索 + 价格数据源
- [@fawazahmed0/currency-api](https://github.com/fawazahmed0/exchange-api) — 免费汇率 CDN
- [BestLemoon/ApplePriceTracker](https://github.com/BestLemoon/ApplePriceTracker) — App Store IAP 解析思路启发

## 💡 反馈与贡献

发现 bug 或想加新功能？欢迎 [开 issue](../../issues) 或 PR。

