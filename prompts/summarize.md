# News Summarization Prompt

## Purpose

Convert a collected news article into a short, Threads-ready summary in Korean.

## Prompt Template

```
Summarize the following dev/IT news concisely in Korean.

Title  : {title}
Content: {content}
Source : {source}

Requirements:
- 2~3 sentences maximum
- Focus on the key point (why it matters, what changes)
- Highlight what developers will find most interesting
- No clickbait language
- Write in Korean
```

## Example Output

```
구글이 Python 3.13에서 GIL(Global Interpreter Lock)을 선택적으로 비활성화하는 기능을 공식 지원한다.
멀티스레드 성능이 크게 향상되며, 기존 라이브러리 호환성은 그대로 유지된다.
```
