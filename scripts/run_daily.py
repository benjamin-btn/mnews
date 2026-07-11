#!/usr/bin/env python3
"""뉴스레터 생성, HTML 통합, Telegram 전송을 순서대로 실행한다."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / "bin" / "python"
KST = timezone(timedelta(hours=9))


def main() -> int:
    load_dotenv(Path.home() / "ai" / "shorts-youtuber" / ".env", override=False)
    target_date = datetime.now(KST).date().isoformat()
    subprocess.run([str(PYTHON), str(ROOT / "scripts" / "generate.py"), "--date", target_date], check=True)
    subprocess.run([str(PYTHON), str(ROOT / "scripts" / "send_telegram.py"), "--date", target_date], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

