# 🌍 AppPriceTracker-iOS · App Store Cross-Region Price Comparison

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey.svg)]()

**[中文](README.md) · English**

> A double-click-to-run desktop tool that compares iOS App Store **subscription IAP prices** (and one-time app prices) across 175 countries — works for ChatGPT, Spotify, Notion, Bumble, Tinder, etc.

## 📸 Real-world example

| ChatGPT Plus monthly subscription | Result |
|---|---|
| 🇹🇷 Turkey ₺499 ≈ ¥73 (~$10) | **Cheapest** |
| 🇪🇸 Spain €22.99 ≈ ¥179 (~$25) | Most expensive |
| **Spread** | **144%** |

| ChatGPT Pro 20x monthly subscription | Result |
|---|---|
| 🇹🇷 Turkey ₺7,999 ≈ ¥1,175 | Cheapest |
| 🇪🇸 Spain €229 ≈ ¥1,786 | Most expensive |
| **Spread** | **52%** |

## ✨ Features

- 🔎 Search any iOS app by name, App Store URL, or numeric ID
- 💎 **In-App Purchase / Subscription comparison** across 175 storefronts
- 📱 Application one-time purchase price comparison
- 💱 Real-time FX conversion (CNY/USD/EUR/JPY · ECB rates)
- 📋 Watchlist with localStorage persistence
- 📤 CSV export & clipboard copy
- 🌗 Auto dark mode (follows system theme)
- 🌐 175 countries / regions with flags + Chinese names

## 🚀 Quick Start

### macOS
1. Click green **Code** button above → **Download ZIP** → unzip
2. Open the unzipped `AppPriceTracker-iOS-main/` folder
3. Double-click **`启动 (macOS).command`**
4. Browser auto-opens at `http://localhost:8765`
5. Stop: press **Ctrl+C** in terminal

### Windows
1. Download ZIP and unzip
2. Double-click **`启动 (Windows).bat`**
3. Browser auto-opens
4. Stop: close the cmd window

### Requirements
- **Python 3.7+** (macOS bundles it; Windows: install from [python.org](https://www.python.org/downloads/) and ✅ check "Add Python to PATH")
- Zero `pip install` — uses Python standard library only

## 🎯 Apps to try

| App | App ID | Notes |
|---|---|---|
| ChatGPT | 6448311069 | Plus / Go / Pro multiple tiers |
| Spotify | 324684580 | Global Premium spread |
| Notion | 1232780281 | Personal Pro |
| Bumble | 930441707 | Boost / Premium |
| YouTube | 544007664 | YT Premium |
| Tinder | 547702041 | Plus / Gold / Platinum |
| Disney+ | 1446075923 | Streaming subscription |
| Duolingo | 570060128 | Super Duolingo |

## 🔧 How it works

### Data sources

1. **iTunes Search API** — app discovery + one-time prices (public, free, JSONP-friendly)
2. **`apps.apple.com/api/apps/v1/...`** — App Store SPA's internal API (returns IAP data)
   - Same-origin only, hence the **local Python proxy** is required
   - No token, no IP-based redirect, no cookies needed
   - This is why a pure browser solution cannot fetch IAP data
3. **`@fawazahmed0/currency-api`** — CDN-hosted free FX rates (CORS-enabled, ECB-backed)

### Architecture

```
Browser (UI) ←→ http://localhost:8765 (Python backend) ←→ Apple APIs
   ↑
Browser localStorage stores: watchlist + price history + settings
```

- Backend ≈ 200 lines of Python (`http.server` + `urllib`)
- Frontend ≈ 800 lines vanilla HTML/JS, no external dependencies
- Concurrency: 5 parallel workers, ~10s for 30 countries

## ⚠️ Notes

- One instance at a time (port 8765)
- iTunes API rate limit: ~20 calls/minute
- "Not available" for some regions reflects actual storefront availability
- All prices stored at original currency, conversion uses live FX (refreshed every 6h)

## 🐛 FAQ

**Q: Port 8765 is in use.** Edit `AppPriceTracker.py` line 22 (`PORT = 8765`).

**Q: macOS says the file is from an unidentified developer.** Right-click → Open → "Open" in the dialog. Source code is fully open and runs locally — your data never leaves your machine.

**Q: Why are some queries slow?** First query a country fans out to 30 parallel HTTPS requests. 8–15s is normal.

## 📜 License

[MIT](LICENSE) © 2026 paradossio

## 🙏 Credits

- [Apple iTunes Search API](https://performance-partners.apple.com/search-api) — search & price data
- [@fawazahmed0/currency-api](https://github.com/fawazahmed0/exchange-api) — free FX CDN
- [BestLemoon/ApplePriceTracker](https://github.com/BestLemoon/ApplePriceTracker) — IAP parsing inspiration

## 💡 Contributing

Feature ideas or bug reports — please [open an issue](../../issues) or send a PR.
