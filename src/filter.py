from src.db import is_duplicate

MIN_SCORE = 5

AI_KEYWORDS = [
    # 모델 & 프레임워크
    "llm", "large language model", "transformer", "diffusion model",
    "neural network", "deep learning", "machine learning",
    "gpt", "claude", "gemini", "llama", "mistral", "qwen", "deepseek",
    "stable diffusion", "flux", "whisper",
    # 개발 도구 & 기술
    "ai agent", "rag", "retrieval augmented", "fine-tuning", "fine-tune",
    "embedding", "vector database", "inference", "quantization",
    "lora", "qlora", "vllm", "ollama", "langchain", "llamaindex",
    "hugging face", "openai api", "anthropic api", "prompt engineering",
    "context window", "tokenizer", "benchmark",
    # 논문 & 연구
    "arxiv", "paper", "research", "dataset", "training",
    "open source", "open-source", "open weights",
]

AI_SUBREDDITS = {"MachineLearning", "LocalLLaMA"}


def _matches_ai(item: dict) -> bool:
    source = item.get("source", "")
    subreddit = source.split("/")[-1] if "/" in source else ""
    if subreddit in AI_SUBREDDITS:
        return True
    text = (item.get("title", "") + " " + item.get("url", "")).lower()
    return any(kw in text for kw in AI_KEYWORDS)


def filter_items(items: list[dict]) -> list[dict]:
    seen_urls = set()
    results = []

    for item in items:
        url = item.get("url", "")
        if not url:
            continue
        if url in seen_urls:
            continue
        if is_duplicate(url):
            continue
        if item.get("score", 0) < MIN_SCORE:
            continue
        if item.get("source", "").startswith("reddit") and not _matches_ai(item):
            continue
        seen_urls.add(url)
        results.append(item)

    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results
