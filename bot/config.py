import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Config:
    bot_token: str
    openrouter_api_key: str
    model: str
    web_search: bool
    web_max_results: int
    user_daily_limit: int
    global_daily_limit: int
    proxy_url: str | None
    db_path: str


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not token:
        raise SystemExit("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set. Copy .env.example to .env and fill it in.")
    return Config(
        bot_token=token,
        openrouter_api_key=key,
        model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat").strip(),
        web_search=_bool("WEB_SEARCH", True),
        web_max_results=int(os.getenv("WEB_MAX_RESULTS", "3")),
        user_daily_limit=int(os.getenv("USER_DAILY_LIMIT", "30")),
        global_daily_limit=int(os.getenv("GLOBAL_DAILY_LIMIT", "300")),
        proxy_url=os.getenv("PROXY_URL", "").strip() or None,
        db_path=os.getenv("DB_PATH", "data/bot.db"),
    )
