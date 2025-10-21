#!/usr/bin/env python3
"""
Selenium + selenium-wire site crawler & API mapper.

- Crawls same-origin links from a base URL (BFS)
- Saves HTML, screenshots, metadata, visible text
- Captures network requests/responses (XHR/fetch)
- Optional: click elements to surface more APIs

Usage:
  python crawl_site.py --url https://www.habitsofmindinstitute.org/habits-of-mind-blog/ --out ./dump --click
"""

import argparse
import json
import time
import re
import hashlib
import contextlib
from pathlib import Path
from urllib.parse import urlparse, urljoin, urldefrag
from collections import deque

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# ---------- utils ----------

def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def same_origin(a: str, b: str) -> bool:
    pa, pb = urlparse(a), urlparse(b)
    return (pa.scheme, pa.netloc) == (pb.scheme, pb.netloc)

def is_probably_asset(url: str) -> bool:
    url = url.split("?", 1)[0].lower()
    return url.endswith((
        ".png",".jpg",".jpeg",".gif",".svg",".webp",".ico",
        ".css",".js",".map",".woff",".woff2",".ttf",".otf",".eot",
        ".mp4",".webm",".mp3",".m4a",".pdf"
    ))

def slugify_url(url: str) -> str:
    u = urlparse(url)
    path = u.path or "/"
    q = f"?{u.query}" if u.query else ""
    base = f"{u.scheme}__{u.netloc}{path}{q}"
    s = re.sub(r"[^a-zA-Z0-9_\-./?=]", "_", base).strip("/")
    s = s.replace("/", "__").replace("?", "__q__").replace("=", "__eq__")
    if len(s) > 180:
        h = hashlib.sha1(base.encode()).hexdigest()[:10]
        s = s[:160] + "__" + h
    return s or "root"

def short(s: bytes | str | None, n: int = 8000):
    if s is None:
        return None
    if isinstance(s, bytes):
        try:
            s = s.decode("utf-8", "replace")
        except Exception:
            s = "<binary>"
    return s if len(s) <= n else s[:n] + f"... [truncated {len(s)-n} bytes]"


# ---------- API store ----------

class ApiStore:
    def __init__(self):
        self._by_key = {}

    def _key(self, method, url):
        return f"{method.upper()} {urldefrag(url)[0]}"

    def add(self, entry):
        k = self._key(entry["method"], entry["url"])
        if k not in self._by_key:
            self._by_key[k] = entry
        else:
            e = self._by_key[k]
            e["count"] += 1
            e["last_seen"] = now_iso()
            if e.get("status") is None and entry.get("status") is not None:
                e["status"] = entry["status"]
            for fld in ("request_body", "response_body"):
                if not e.get(fld) and entry.get(fld):
                    e[fld] = entry[fld]

    def to_list(self):
        return sorted(self._by_key.values(), key=lambda x: (x["method"], x["url"]))


# ---------- crawler ----------

class Crawler:
    def __init__(self, base_url, out_dir, max_pages, click, nav_timeout):
        self.base_url = base_url.rstrip("/")
        self.parsed_base = urlparse(self.base_url)
        self.out = Path(out_dir)
        self.max_pages = max_pages
        self.click = click
        self.nav_timeout = nav_timeout

        ensure_dir(self.out / "pages")
        self.site_map = set()
        self.visited = set()
        self.api_store = ApiStore()

        self.sw_opts = {
            'request_storage': 'memory',
            'max_request_body_size': 2 * 1024 * 1024,
            'max_response_body_size': 2 * 1024 * 1024,
            'verify_ssl': True,
        }
        self.driver = None

    def _init_driver(self):
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1400,1000")

        from selenium.webdriver.chrome.service import Service
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        self.driver = webdriver.Chrome(
            service=service,
            options=opts,
            seleniumwire_options=self.sw_opts
        )
        self.driver.set_page_load_timeout(self.nav_timeout)

    def _quit_driver(self):
        with contextlib.suppress(Exception):
            if self.driver:
                self.driver.quit()

    def crawl(self):
        self._init_driver()
        try:
            q = deque([self.base_url])
            while q and len(self.visited) < self.max_pages:
                url = q.popleft()
                if url in self.visited:
                    continue
                self.visited.add(url)
                self._visit_page(url)

                links = self._extract_links()
                for u in links:
                    if u not in self.visited and len(self.visited) + len(q) < self.max_pages:
                        q.append(u)
                        self.site_map.add(u)
        finally:
            self._quit_driver()
            self._write_outputs()

    def _visit_page(self, url):
        with contextlib.suppress(Exception):
            del self.driver.requests
        try:
            self.driver.get(url)
        except Exception as e:
            print(f"[load-error] {url}: {e}")
        if self.click:
            self._light_clicks()
        self._save_page(url)
        self._save_requests()

    def _extract_links(self):
        links = set()
        with contextlib.suppress(Exception):
            for a in self.driver.find_elements(By.CSS_SELECTOR, "a[href]"):
                href = a.get_attribute("href")
                if not href or href.startswith("javascript:") or href.startswith("#"):
                    continue
                absu = urljoin(self.base_url, href)
                absu, _ = urldefrag(absu)
                if same_origin(self.base_url, absu) and not is_probably_asset(absu):
                    links.add(absu)
        return links

    def _light_clicks(self):
        selectors = [
            "button:not([disabled])",
            "[role=button]:not([aria-disabled=true])",
            "a[href^='/']:not([download])",
            "input[type=submit], input[type=button]"
        ]
        for sel in selectors:
            with contextlib.suppress(Exception):
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for el in els[:5]:
                    with contextlib.suppress(Exception):
                        el.click()
                        time.sleep(0.3)

    def _save_page(self, url):
        slug = slugify_url(url)
        pdir = self.out / "pages" / slug
        ensure_dir(pdir)

        with contextlib.suppress(Exception):
            html = self.driver.page_source
            (pdir / "page.html").write_text(html, encoding="utf-8")

        with contextlib.suppress(Exception):
            self.driver.save_screenshot(str(pdir / "screenshot.png"))

        meta = {"url": url, "captured_at": now_iso()}
        meta["title"] = self.driver.title
        (pdir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        with contextlib.suppress(Exception):
            blocks = []
            for e in self.driver.find_elements(By.CSS_SELECTOR, "p, li, div"):
                t = (e.text or "").strip()
                if t and len(t.split()) >= 3:
                    blocks.append(t)
            (pdir / "text.txt").write_text("\n\n".join(blocks[:200]), encoding="utf-8")

    def _save_requests(self):
        for req in getattr(self.driver, "requests", []):
            if not req.url.startswith(("http://", "https://")):
                continue
            if is_probably_asset(req.url):
                continue
            method = (req.method or "GET").upper()
            status = None
            headers = {}
            body = None
            with contextlib.suppress(Exception):
                if req.response:
                    status = req.response.status_code
                    headers = dict(req.response.headers)
                    ct = headers.get("Content-Type", "")
                    if any(t in (ct or "").lower() for t in ("json","text","xml","html")):
                        body = short(req.response.body)
            entry = {
                "detected_at": now_iso(),
                "method": method,
                "url": urldefrag(req.url)[0],
                "status": status,
                "response_headers": headers,
                "response_body": body,
                "request_body": short(getattr(req, "body", None), 2000),
                "count": 1,
                "last_seen": now_iso(),
            }
            self.api_store.add(entry)

    def _write_outputs(self):
        (self.out / "site_map.json").write_text(json.dumps(sorted(self.site_map), indent=2), encoding="utf-8")
        (self.out / "apis.json").write_text(json.dumps(self.api_store.to_list(), indent=2), encoding="utf-8")
        summary = {
            "base_url": self.base_url,
            "captured_at": now_iso(),
            "pages_crawled": len(self.visited),
            "routes_found": len(self.site_map),
            "apis_detected": len(self.api_store.to_list()),
        }
        (self.out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


# ---------- CLI ----------

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", default="./out")
    ap.add_argument("--max-pages", type=int, default=100)
    ap.add_argument("--click", action="store_true")
    ap.add_argument("--timeout", type=int, default=25)
    return ap.parse_args()

def main():
    args = parse_args()
    c = Crawler(args.url, args.out, args.max_pages, args.click, args.timeout)
    c.crawl()

if __name__ == "__main__":
    main()
