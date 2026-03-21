#!/bin/bash
# post-scrape.sh
# 수집 완료 후 실행되는 훅 — 로그 기록

LOG_FILE="memory/scrape.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] 수집 완료" >> "$LOG_FILE"

# pending.json 항목 수 기록
if [ -f "memory/pending.json" ]; then
  COUNT=$(python3 -c "import json; print(len(json.load(open('memory/pending.json'))))" 2>/dev/null || echo "?")
  echo "[$TIMESTAMP] 대기 항목: ${COUNT}개" >> "$LOG_FILE"
fi

echo "[post-scrape] 로그 기록 완료: $LOG_FILE"
exit 0
