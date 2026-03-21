#!/bin/bash
# pre-post.sh
# 포스팅 전 실행되는 검증 훅

set -e

APPROVED_FILE="memory/approved.json"
POSTED_FILE="memory/posted.json"
MAX_DAILY=10

echo "[pre-post] 포스팅 전 검증 시작..."

# 1. 승인 파일 존재 확인
if [ ! -f "$APPROVED_FILE" ]; then
  echo "[pre-post] ERROR: 승인된 항목 없음 (approved.json 없음). 포스팅 중단."
  exit 1
fi

# 2. 승인 파일이 비어있지 않은지 확인
APPROVED_COUNT=$(python3 -c "import json; data=json.load(open('$APPROVED_FILE')); print(len(data))" 2>/dev/null || echo "0")
if [ "$APPROVED_COUNT" -eq 0 ]; then
  echo "[pre-post] ERROR: 승인된 항목이 없습니다. 포스팅 중단."
  exit 1
fi

# 3. API 키 존재 확인
if [ -z "$THREADS_API_KEY" ]; then
  echo "[pre-post] ERROR: THREADS_API_KEY 환경변수가 없습니다."
  exit 1
fi

# 4. 오늘 포스팅 수 확인
TODAY=$(date +%Y-%m-%d)
if [ -f "$POSTED_FILE" ]; then
  TODAY_COUNT=$(python3 -c "
import json
from datetime import date
data = json.load(open('$POSTED_FILE'))
today = '$TODAY'
count = sum(1 for item in data if item.get('posted_at', '').startswith(today))
print(count)
" 2>/dev/null || echo "0")

  if [ "$TODAY_COUNT" -ge "$MAX_DAILY" ]; then
    echo "[pre-post] ERROR: 오늘 포스팅 한도($MAX_DAILY)에 도달했습니다. 내일 다시 시도하세요."
    exit 1
  fi
  echo "[pre-post] 오늘 포스팅: ${TODAY_COUNT}/${MAX_DAILY}"
fi

echo "[pre-post] 검증 통과. 포스팅 진행합니다."
exit 0
