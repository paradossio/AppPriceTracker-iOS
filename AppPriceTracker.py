#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Store 全球比价工具 — 本地后端
========================================
功能:
  • 应用搜索 (iTunes Search API)
  • 应用本身价格跨地区对比 (iTunes Lookup API, JSONP)
  • 内购订阅价格跨地区对比 (apps.apple.com 内部 API)
  • 实时汇率换算

技术:
  • 仅使用 Python 标准库 (无需 pip install)
  • 本地 HTTP 服务，监听 127.0.0.1:8765
  • 启动后自动打开浏览器
  • 关闭：在终端窗口按 Ctrl+C
"""
import json
import sys
import threading
import time
import webbrowser
import urllib.request
import urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path

PORT = 8765
HOST = "127.0.0.1"
SCRIPT_DIR = Path(__file__).resolve().parent
HTML_FILE = SCRIPT_DIR / "AppPriceTracker.html"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15")

# ---------------------------------------------------------------- #
def http_get_json(url, headers=None, timeout=15):
    """通用 GET → JSON。"""
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        # 可能 gzip
        if resp.headers.get("Content-Encoding") == "gzip":
            import gzip
            raw = gzip.decompress(raw)
        return json.loads(raw.decode("utf-8", errors="replace"))


# ---------------------------------------------------------------- #
class Handler(BaseHTTPRequestHandler):
    """单文件路由处理。"""

    def log_message(self, fmt, *args):  # 静音访问日志
        pass

    # ---------- helpers ----------
    def _send(self, body, status=200, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        # 允许任意页面访问（双击 file:// 也能用）
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_html(self):
        if not HTML_FILE.exists():
            return self._send("<h1>缺少 AppPriceTracker.html</h1>", 500, "text/html")
        with open(HTML_FILE, "rb") as f:
            self._send(f.read(), 200, "text/html; charset=utf-8")

    def _err(self, msg, code=500):
        self._send({"error": str(msg)}, status=code)

    # ---------- routing ----------
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        try:
            url = urllib.parse.urlparse(self.path)
            qs = {k: v[0] for k, v in urllib.parse.parse_qs(url.query).items()}
            path = url.path

            # ---------- HTML 主页 ----------
            if path in ("/", "/index.html"):
                return self._send_html()

            if path == "/health":
                return self._send({"ok": True, "ts": int(time.time())})

            # ---------- 1. 搜索应用 ----------
            if path == "/api/search":
                term = qs.get("q", "").strip()
                cc = qs.get("country", "us").lower()
                if not term:
                    return self._send({"results": [], "resultCount": 0})
                # 如果 term 是数字 ID 或 URL，走 lookup
                import re
                m = re.search(r"id(\d{6,})|^(\d{6,})$", term)
                if m:
                    aid = m.group(1) or m.group(2)
                    u = (f"https://itunes.apple.com/lookup?id={aid}"
                         f"&country={cc}&entity=software")
                else:
                    u = (f"https://itunes.apple.com/search?"
                         f"term={urllib.parse.quote(term)}"
                         f"&country={cc}&entity=software&limit=20")
                return self._send(http_get_json(u))

            # ---------- 2. 应用本身价格 (lookup) ----------
            if path == "/api/lookup":
                aid = qs.get("id")
                cc = qs.get("country", "us").lower()
                if not aid:
                    return self._err("missing id", 400)
                u = (f"https://itunes.apple.com/lookup?id={aid}"
                     f"&country={cc}&entity=software")
                return self._send(http_get_json(u))

            # ---------- 3. 内购订阅价格 (核心新功能) ----------
            if path == "/api/iap":
                aid = qs.get("id")
                cc = qs.get("country", "us").lower()
                if not aid:
                    return self._err("missing id", 400)
                u = (f"https://apps.apple.com/api/apps/v1/catalog/{cc}/apps/{aid}"
                     f"?platform=web&views=top-in-app-purchasables&l=en-us")
                headers = {
                    "Authorization": "Bearer",
                    "Referer": f"https://apps.apple.com/{cc}/app/id{aid}",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "application/json",
                }
                try:
                    raw = http_get_json(u, headers=headers, timeout=15)
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        return self._send({"country": cc, "ok": False,
                                           "reason": "未上架"})
                    return self._err(f"HTTP {e.code} from apps.apple.com", 502)

                # 提炼成精简格式
                try:
                    app_data = raw["data"][0]
                    name = app_data["attributes"].get("name", "")
                    iap_view = app_data.get("views", {}).get(
                        "top-in-app-purchasables", {})
                    iaps_raw = iap_view.get("data", [])
                    iaps = []
                    for x in iaps_raw:
                        a = x.get("attributes", {})
                        for o in (a.get("offers") or []):
                            iaps.append({
                                "iapId": x.get("id"),
                                "name": a.get("name"),
                                "offerName": a.get("offerName"),
                                "isSubscription": a.get("isSubscription", False),
                                "groupId": a.get("subscriptionFamilyId"),
                                "groupName": a.get("subscriptionFamilyName"),
                                "groupRank": a.get("subscriptionFamilyRank"),
                                "currencyCode": o.get("currencyCode"),
                                "price": o.get("price"),
                                "priceFormatted": o.get("priceFormatted"),
                                "period": o.get("recurringSubscriptionPeriod"),
                            })
                    return self._send({
                        "country": cc, "ok": True,
                        "appName": name, "iaps": iaps,
                    })
                except Exception as e:
                    return self._err(f"parse: {e}", 500)

            # ---------- 4. 实时汇率（USD 基准） ----------
            if path == "/api/fx":
                # 优先 jsdelivr CDN, 次选 cloudflare 镜像
                for u in [
                    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest"
                    "/v1/currencies/usd.min.json",
                    "https://latest.currency-api.pages.dev/v1/currencies/usd.json",
                ]:
                    try:
                        d = http_get_json(u, timeout=8)
                        if d.get("usd"):
                            rates = {"USD": 1.0}
                            for k, v in d["usd"].items():
                                rates[k.upper()] = v
                            return self._send({"base": "USD", "rates": rates,
                                               "date": d.get("date")})
                    except Exception:
                        continue
                return self._err("FX unavailable", 502)

            return self._send({"error": "not found"}, 404)

        except urllib.error.HTTPError as e:
            self._err(f"upstream HTTP {e.code}: {e.reason}", code=502)
        except Exception as e:
            self._err(str(e), code=500)


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


# ---------------------------------------------------------------- #
def main():
    if not HTML_FILE.exists():
        print(f"\n❌ 缺少前端文件: {HTML_FILE}")
        print(f"   请确认 AppPriceTracker.html 与本脚本在同一目录\n")
        sys.exit(1)

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"

    print()
    print("┌─────────────────────────────────────────────┐")
    print("│  🌍 App Store 全球比价工具 已启动           │")
    print("├─────────────────────────────────────────────┤")
    print(f"│  访问地址:  {url:<32s}│")
    print("│  关闭服务:  在此窗口按 Ctrl+C               │")
    print("└─────────────────────────────────────────────┘")
    print()

    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 已停止。")
        server.shutdown()


if __name__ == "__main__":
    main()
