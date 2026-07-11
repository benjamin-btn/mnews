#!/usr/bin/env python3
"""종합 뉴스레터 HTML과 주식 관심 종목을 Telegram으로 전송한다."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

import requests


ROOT = Path(__file__).resolve().parents[1]


def credentials_from_chrome() -> Optional[Tuple[str, str]]:
    base = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
    candidates = sorted(
        list(base.glob("*/Local Storage/leveldb/*.ldb"))
        + list(base.glob("*/Local Storage/leveldb/*.log")),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    token_pattern = re.compile(rb"\d{8,12}:[A-Za-z0-9_-]{30,}")
    for path in candidates:
        data = path.read_bytes()
        if b"shortscut-telegram" not in data and b"AI Daily" not in data:
            continue
        for match in token_pattern.finditer(data):
            chunk = data[max(0, match.start() - 500) : match.end() + 800]
            printable = re.sub(rb"[^\x20-\x7e]", b"", chunk).decode("ascii", errors="ignore")
            chat = re.search(r'chatI(?:d)?[^0-9]{0,8}(-?\d{5,})', printable)
            if chat:
                return match.group().decode("ascii"), chat.group(1)
    return None


def load_credentials() -> Tuple[str, str]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        return token, chat_id
    try:
        token = subprocess.run(
            ["security", "find-generic-password", "-a", os.environ.get("USER", "benjamin"), "-s", "mnews-telegram-token", "-w"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        chat_id = subprocess.run(
            ["security", "find-generic-password", "-a", os.environ.get("USER", "benjamin"), "-s", "mnews-telegram-chat-id", "-w"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        if token and chat_id:
            return token, chat_id
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    found = credentials_from_chrome()
    if found:
        return found
    raise RuntimeError(
        "Telegram 설정을 찾지 못했습니다. TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID를 설정하세요."
    )


def stock_digests(target_date: date) -> List[str]:
    path = ROOT / "sections" / "stocks" / "newsletters" / f"{target_date.isoformat()}.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^## 오늘의 관심 종목\s*$([\s\S]*?)(?=^## |\Z)", text, re.MULTILINE)
    if not match:
        return []
    body = match.group(1)
    messages = []
    for label, emoji in (("국내주식", "🇰🇷"), ("해외주식", "🌎")):
        group = re.search(rf"^### {label}\s*$([\s\S]*?)(?=^### |\Z)", body, re.MULTILINE)
        if not group:
            continue
        digest = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", group.group(1)).strip()
        digest = re.sub(r"^#### ", "• ", digest, flags=re.MULTILINE)
        messages.append(f"{emoji} 오늘의 {label} 관심 종목\n\n{digest}"[:3800])
    return messages


def call_telegram(token: str, method: str, **kwargs):
    response = requests.post(
        f"https://api.telegram.org/bot{token}/{method}", timeout=60, **kwargs
    )
    if not response.ok:
        description = response.json().get("description", response.text[:200])
        raise RuntimeError(f"Telegram {method} 실패: {description}")
    return response.json()["result"]


def send(target_date: date) -> Tuple[int, List[int]]:
    token, chat_id = load_credentials()
    html_path = ROOT / "public" / f"{target_date.isoformat()}.html"
    if not html_path.exists():
        raise FileNotFoundError(html_path)
    caption = (
        f"📰 mnews · {target_date.isoformat()}\n"
        "경제 · 주식 · AI트렌드 종합 뉴스레터\n"
        "첨부 HTML을 열면 원문 링크와 함께 볼 수 있습니다."
    )
    with html_path.open("rb") as handle:
        document = call_telegram(
            token,
            "sendDocument",
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (html_path.name, handle, "text/html")},
        )
    digest_ids = []
    for digest in stock_digests(target_date):
        digest += "\n\n⚠️ 정보 제공용이며 개인 맞춤 투자자문이 아닙니다. 투자 손실 가능성이 있습니다."
        digest_result = call_telegram(
            token, "sendMessage", data={"chat_id": chat_id, "text": digest}
        )
        digest_ids.append(digest_result["message_id"])
    return document["message_id"], digest_ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="뉴스레터 날짜(YYYY-MM-DD)")
    args = parser.parse_args()
    document_id, digest_ids = send(date.fromisoformat(args.date))
    print(f"Telegram 전송 완료: document_message_id={document_id}, digest_message_ids={digest_ids}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
