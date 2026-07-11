# 동작 구조

1. `config/sections.yaml`에서 사용자가 정한 섹션을 읽습니다.
2. 섹션 폴더나 `sources.yaml`이 없으면 OpenAI 웹 검색으로 신뢰할 수 있는 출처를 선정합니다.
3. 선정한 출처 도메인만 검색해 최신 기사를 확인합니다.
4. 섹션별 `newsletters/YYYY-MM-DD.md`를 생성합니다.
5. GitHub Actions가 매일 실행 후 변경된 결과를 커밋합니다.

현재 초기 섹션은 경제, 주식, AI트렌드입니다. 섹션 구성의 유일한 원본은 `config/sections.yaml`입니다.

