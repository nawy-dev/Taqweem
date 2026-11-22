#!/usr/bin/env python3
"""The 1024x500 feature graphic Google Play asks for (D-172, new icon D-177). Run from the repo root.

Uses the installed web icon (public/icons/icon-512.png), so it always matches the app's icon.
Needs Playwright (Chromium).
"""
import base64
import os
import tempfile

from playwright.sync_api import sync_playwright

TILE = '#111318'
cwd = os.getcwd()
icon = base64.b64encode(open('public/icons/icon-512.png', 'rb').read()).decode()

html = f"""<!doctype html><meta charset=utf-8>
<style>
@font-face {{ font-family: Cairo; src: url('file://{cwd}/public/fonts/cairo-Bold.woff2'); font-weight: 700; }}
body {{ margin:0; width:1024px; height:500px; background:{TILE}; display:flex; align-items:center;
  justify-content:center; gap:64px; direction:rtl; font-family:Cairo, sans-serif; color:#E3E3E3; }}
img {{ width:340px; height:340px; }}
h1 {{ font-size:120px; margin:0; line-height:1.1; font-weight:700; }}
p {{ font-size:36px; margin:8px 0 0; color:#A3A9B5; font-weight:700; }}
</style>
<img alt="" src="data:image/png;base64,{icon}">
<div><h1>تقويم</h1><p>تقويمك الشخصي، على جهازك</p></div>"""

with tempfile.TemporaryDirectory() as tmp:
    page_path = os.path.join(tmp, 'feature.html')
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(html)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1024, 'height': 500})
        pg.goto(f'file://{page_path}')
        pg.wait_for_timeout(800)
        pg.screenshot(path='tools/android/play/feature-graphic-1024x500.png')
        b.close()
