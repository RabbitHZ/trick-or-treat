# Python Style Rules

## Basics

- Python 3.11+
- Type hints required on all function arguments and return values
- Formatter: `black` (line-length=100)
- Linter: `ruff`

## Structure

- Each source scraper must inherit from `BaseScraper`
- Load environment variables via `python-dotenv` from `.env`
- All config values must be managed in a single `config.py`
- Use custom Exception classes for error handling

## Prohibited

- Use `logging` module — never use `print()` for output
- No hardcoded API keys, URLs, or timeout values
- No bare `except:` clauses
