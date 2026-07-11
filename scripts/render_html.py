#!/usr/bin/env python3
"""같은 날짜의 섹션별 Markdown 뉴스레터를 단일 HTML로 합친다."""

from __future__ import annotations

import argparse
import html
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

import yaml
from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
SECTIONS_FILE = ROOT / "config" / "sections.yaml"
OUTPUT_DIR = ROOT / "public"


def load_sections() -> List[Dict[str, Any]]:
    with SECTIONS_FILE.open(encoding="utf-8") as handle:
        return (yaml.safe_load(handle) or {}).get("sections", [])


def strip_document_title(markdown: str) -> str:
    return re.sub(r"^# .+?\n+", "", markdown, count=1)


def render_date(target_date: date) -> Path:
    renderer = MarkdownIt("commonmark", {"html": False, "typographer": True})
    sections = []
    for section in load_sections():
        path = ROOT / "sections" / section["id"] / "newsletters" / f"{target_date.isoformat()}.md"
        if not path.exists():
            continue
        body = renderer.render(strip_document_title(path.read_text(encoding="utf-8")))
        sections.append({**section, "body": body})

    if not sections:
        raise FileNotFoundError(f"{target_date.isoformat()} 뉴스레터가 없습니다.")

    nav = "".join(
        f'<a href="#{html.escape(s["id"])}">{html.escape(s["name"])}</a>' for s in sections
    )
    cards = "".join(
        f'''<section class="newsletter" id="{html.escape(s['id'])}">
          <div class="section-label">SECTION</div>
          <h2 class="section-title">{html.escape(s['name'])}</h2>
          <div class="section-body">{s['body']}</div>
        </section>'''
        for s in sections
    )
    document = f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>mnews — {target_date.isoformat()}</title>
  <style>
    :root {{ --ink:#14213d; --muted:#667085; --paper:#fffdf8; --line:#ded8cb; --accent:#e4572e; --soft:#f3efe5; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; color:var(--ink); background:#e9e4d9; font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR",sans-serif; line-height:1.75; }}
    a {{ color:#0b5cab; text-decoration-thickness:1px; text-underline-offset:3px; }}
    .page {{ width:min(1120px, calc(100% - 32px)); margin:28px auto 64px; background:var(--paper); box-shadow:0 18px 60px rgba(20,33,61,.13); }}
    header {{ padding:68px clamp(24px,7vw,88px) 50px; border-bottom:1px solid var(--line); }}
    .masthead {{ display:flex; align-items:end; justify-content:space-between; gap:20px; border-top:5px solid var(--ink); padding-top:18px; }}
    .brand {{ margin:0; font:900 clamp(44px,9vw,92px)/.9 Georgia,serif; letter-spacing:-.06em; }}
    .date {{ color:var(--muted); font-weight:700; letter-spacing:.08em; white-space:nowrap; }}
    .deck {{ max-width:720px; margin:30px 0 0; color:#344054; font:400 clamp(19px,2.2vw,25px)/1.55 Georgia,"Noto Serif KR",serif; }}
    nav {{ position:sticky; top:0; z-index:5; display:flex; gap:10px; padding:13px clamp(24px,7vw,88px); overflow:auto; background:rgba(255,253,248,.94); backdrop-filter:blur(12px); border-bottom:1px solid var(--line); }}
    nav a {{ padding:6px 14px; color:var(--ink); background:var(--soft); border-radius:999px; font-size:14px; font-weight:750; text-decoration:none; white-space:nowrap; }}
    main {{ padding:0 clamp(24px,7vw,88px) 72px; }}
    .newsletter {{ padding:64px 0 54px; border-bottom:2px solid var(--ink); scroll-margin-top:70px; }}
    .newsletter:last-child {{ border-bottom:0; }}
    .section-label {{ color:var(--accent); font-size:12px; font-weight:900; letter-spacing:.18em; }}
    .section-title {{ margin:6px 0 28px; font:850 clamp(35px,6vw,58px)/1.08 Georgia,"Noto Serif KR",serif; letter-spacing:-.035em; }}
    .section-body > p:first-child {{ padding:22px 24px; background:var(--soft); border-left:4px solid var(--accent); font-size:18px; }}
    .section-body h2 {{ margin:48px 0 18px; padding-bottom:9px; border-bottom:1px solid var(--line); font-size:14px; letter-spacing:.12em; text-transform:uppercase; }}
    .section-body h3 {{ margin:34px 0 10px; font:750 25px/1.4 Georgia,"Noto Serif KR",serif; letter-spacing:-.02em; }}
    .section-body h4 {{ margin:28px 0 8px; color:#263b63; font-size:20px; line-height:1.45; letter-spacing:-.015em; }}
    .section-body ul, .section-body ol {{ padding-left:24px; }}
    .section-body li {{ margin:8px 0; }}
    footer {{ padding:24px clamp(24px,7vw,88px); color:var(--muted); background:var(--soft); font-size:13px; }}
    @media (max-width:640px) {{ .page {{ width:100%; margin:0; }} header {{ padding-top:38px; }} .masthead {{ align-items:start; flex-direction:column; }} .date {{ white-space:normal; }} }}
    @media print {{ body {{ background:white; }} .page {{ width:100%; margin:0; box-shadow:none; }} nav {{ display:none; }} .newsletter {{ break-before:page; }} .newsletter:first-child {{ break-before:auto; }} }}
  </style>
</head>
<body>
  <div class="page">
    <header>
      <div class="masthead"><h1 class="brand">mnews</h1><div class="date">{target_date.isoformat()} · DAILY BRIEF</div></div>
      <p class="deck">경제, 주식, AI 트렌드의 중요한 흐름을 한 페이지에서 읽는 오늘의 뉴스 브리핑.</p>
    </header>
    <nav aria-label="섹션 바로가기">{nav}</nav>
    <main>{cards}</main>
    <footer>AI가 선정·요약한 뉴스입니다. 중요한 판단 전에는 연결된 원문을 확인하세요.</footer>
  </div>
</body>
</html>
'''
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{target_date.isoformat()}.html"
    output.write_text(document, encoding="utf-8")
    (OUTPUT_DIR / "index.html").write_text(document, encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="뉴스레터 날짜(YYYY-MM-DD)")
    args = parser.parse_args()
    output = render_date(date.fromisoformat(args.date))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
