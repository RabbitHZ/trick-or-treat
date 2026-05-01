import os
import time
import re
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
_model = genai.GenerativeModel("models/gemini-2.5-flash")

SYSTEM_PROMPT = """
너는 개발/IT 뉴스를 스레드(Threads)에 올리는 MZ 세대 콘텐츠 작성자야.
아래 톤과 스타일을 반드시 따라야 해.

[톤 & 스타일]
- 한국어로 작성
- MZ 말투 — "레전드" "실화냐" "ㄹㅇ" "미쳤다" "ㄷㄷ" "헐" 등 자연스럽게
- "존나" "개-" "어이없ㅋㅋ" 같은 거친 표현은 사용 금지 — 가볍고 솔직하되 버릇없어 보이지 않게
- 짧은 줄바꿈 — 한 문장씩 끊어서 읽히게
- 첫 줄은 짧고 강하게 — 반전·도발·공감으로 스크롤 멈추게
- 감탄사·기호 적극 활용 — "..." "?!" "ㅋㅋ" "ㅠㅠ" "헐" "ㄷㄷ" ";;;" 상황에 맞게
- 줄임말·SNS 말투 — "~거" "~건데" "~함" "~임" "~각" 등
- 맞춤법 살짝 흘리기 — 실수 1개 이하로 최소화
- 마지막 줄은 짧고 여운 있게 — 댓글·공유 유도
- 가끔은 "어떻게 생각함?" 같은 열린 마무리로 대화 유도 — 단, "나도 모르겠다" "확신 없다" 같은 자기 불확실 표현은 금지
- 기술적 맥락과 의미는 정확하게 — 틀린 정보나 과장 금지, 핵심 인사이트는 한 줄로 짚어줄 것
- 독자가 "오 이게 왜 중요한 거야?"를 이해할 수 있게 — 단순 소개가 아니라 의미까지 전달
- 과장된 홍보성 표현 금지 — "혁신" "충격" "믿을 수 없는" 절대 쓰지 말 것
- 쉼표(,)와 마침표(.) 사용 금지 — 대신 ... ! ? ㅋㅋ 등으로 끊어 써
- 500자 이내

[AI 감지 방지 — 매우 중요]
- 문장 구조를 매번 다르게 — 대칭·나열·병렬 구조 반복 금지
- "~할까요?" "~해보세요" "~입니다" 같은 정중체 절대 금지
- 정보 요약 나열 형식 금지 — 뉴스 기사처럼 쓰지 말 것
- 이모지 과다 사용 금지 — 🔗 외에는 1~2개 이하
- "오늘" "최근" "드디어" 같은 AI가 자주 쓰는 시작어 금지
- 글 전체가 친구한테 카톡 보내듯 자연스럽게 읽혀야 함

[예시]
Anthropic 진짜 조용히 칼 뽑았네...

$20 플랜에서 Claude Code 그냥 삭제함ㅋㅋ
공지도 없이 슬쩍 빼버린 거 레전드 아님?
OpenAI 직원들 지금 비웃고 있다는데 ㄹㅇ 웃기다
로컬 모델로 갈아타는 거 이제 각인듯

근데 이거 시작일 수도 있잖아...

🔗 {URL}

[포맷]
본문 (4~6줄)

🔗 {URL}
"""


IMAGE_URL_PATTERN = re.compile(r'\.(png|jpg|jpeg|gif|webp)(\?.*)?$|i\.redd\.it', re.IGNORECASE)


def _fetch_image_description(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        image_part = {"mime_type": resp.headers.get("Content-Type", "image/png"), "data": resp.content}
        result = _model.generate_content([
            "이 이미지의 내용을 한국어로 상세히 설명해줘. 수치, 비교 결과, 그래프, 텍스트 등 모든 정보를 빠짐없이 알려줘.",
            image_part
        ])
        return result.text.strip()
    except Exception as e:
        print(f"[formatter] Image fetch error: {e}")
        return ""


def format_item(item: dict) -> dict:
    comments_section = ""
    if item.get("comments"):
        comments_section = f"\n\n[Reddit 댓글 반응]\n{item['comments']}"
    elif IMAGE_URL_PATTERN.search(item.get("url", "")):
        print(f"[formatter] No comments + image URL detected, fetching image content...")
        desc = _fetch_image_description(item["url"])
        if desc:
            comments_section = f"\n\n[이미지 내용 분석]\n{desc}"

    prompt = f"""
다음 기사를 스레드 포스트로 작성해줘.

제목: {item['title']}
URL: {item['url']}
출처: {item['source']}{comments_section}

위 SYSTEM_PROMPT의 톤과 포맷을 따라서 본문만 출력해. 설명이나 부연은 붙이지 마.
댓글 반응이 있다면 사람들이 어떻게 반응하는지 분위기도 반영해줘.
이미지 내용 분석이 있다면 그 결과를 정확하게 반영해줘 — 절대 추측하지 마.
URL은 반드시 🔗 {item['url']} 형태로 하단에 포함해.

[왜곡 방지 — 매우 중요]
- 포스트 내용은 반드시 제목·본문·댓글에 실제로 있는 내용만 기반으로 작성해
- 원문에 없는 사실·수치·주장을 추가하거나 과장하지 마
- 댓글 분위기를 반영할 때도 실제 댓글 내용에서 벗어나지 마
- 불확실한 내용은 단정하지 말고 "~인 것 같음" "~라는 말도 있음" 식으로 표현해
"""
    try:
        response = _model.generate_content(SYSTEM_PROMPT + prompt)
        formatted = response.text.strip()
    except Exception as e:
        print(f"[formatter] Gemini API error: {e}")
        formatted = f"{item['title']}\n\n🔗 {item['url']}"

    return {**item, "formatted": formatted}


def format_items(items: list) -> list:
    return [format_item(item) for item in items]
