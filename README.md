# mnews

`config/sections.yaml`에 원하는 뉴스레터 섹션만 적으면 AI가 섹션별 출처를 찾고 일자별 뉴스레터를 생성합니다.

## 사용법

```bash
cd ~/ai/mnews
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="..."
python scripts/generate.py --refresh-sources
```

이후 매일 실행할 때는 저장된 출처를 재사용합니다.

```bash
python scripts/generate.py
```

실행이 끝나면 섹션별 Markdown과 함께 `public/YYYY-MM-DD.html`, 최신 종합본인 `public/index.html`이 생성됩니다.

특정 섹션만 실행할 수도 있습니다.

```bash
python scripts/generate.py --section economy
```

## 편집할 파일

섹션 추가·삭제·수정은 `config/sections.yaml`에서만 합니다.

```yaml
sections:
  - id: economy
    name: 경제
    description: 한국과 세계의 주요 경제 뉴스
    source_count: 6
```

`id`는 영문 소문자, 숫자, 하이픈만 사용할 수 있으며 폴더명이 됩니다.

## 자동 생성 결과

```text
sections/
└── economy/
    ├── sources.yaml
    └── newsletters/
        └── YYYY-MM-DD.md
```

출처 목록은 기본 30일마다 자동 갱신됩니다. 즉시 다시 찾으려면 `--refresh-sources`를 사용합니다.

## GitHub Actions

`.github/workflows/daily-newsletter.yml`은 매일 오전 8시 5분(한국 시간)에 실행됩니다. GitHub 저장소 Settings의 Actions secrets에 `OPENAI_API_KEY`를 등록해야 합니다.

API 키는 로컬 파일이나 Git 저장소에 저장하지 않습니다.

## Telegram 자동 전송

로컬 Mac에서는 `shorts-youtuber`에 등록했던 `AI Daily` 봇 정보를 macOS 키체인에서 읽습니다. `com.mnews.daily` LaunchAgent가 매일 오전 8시 10분에 다음 작업을 실행합니다.

1. 섹션별 뉴스레터 생성
2. 단일 HTML 종합본 생성
3. 종합 HTML 파일 전송
4. 주식 관심 종목 3~5개와 선정 이유·촉매·위험 요인 전송

수동 전송:

```bash
source .venv/bin/activate
python scripts/send_telegram.py --date YYYY-MM-DD
```

GitHub Actions에서도 전송하려면 저장소 Secret에 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`를 추가합니다.
# mnews
# mnews
# mnews
# mnews
# mnews
# mnews
# mnews
# mnews
# mnews
# mnews
# mnews
# mnews
