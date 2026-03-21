#!/bin/bash
# on-approval.sh
# 사용자 승인 완료 후 실행되는 훅

LOG_FILE="memory/approval.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] 승인 완료" >> "$LOG_FILE"

if [ -f "memory/approved.json" ]; then
  COUNT=$(python3 -c "import json; print(len(json.load(open('memory/approved.json'))))" 2>/dev/null || echo "?")
  echo "[$TIMESTAMP] 승인된 항목: ${COUNT}개" >> "$LOG_FILE"
  echo "[on-approval] ${COUNT}개 항목 승인됨. '/post'로 포스팅하세요."
fi

exit 0
