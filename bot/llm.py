import html
import logging
import re
from collections import defaultdict, deque
from datetime import date

import aiohttp

from .config import Config
from .net import make_session

log = logging.getLogger(__name__)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
HISTORY_MESSAGES = 6  # last 3 questions and answers per user

SYSTEM_PROMPT = """You are "Help in Moscow", a friendly Telegram assistant for foreigners \
(students, tourists, interns, new residents) who live in or visit Moscow, Russia. Today is {today}.

Rules:
- Reply in {language}. Only if the user clearly writes in a different language, reply in that language.
- Always give a concrete, practical answer: where to go, what to bring, prices, steps, official \
websites and apps. Never tell the user to figure it out on their own.
{sources_rule}- If something changes often (prices, rules), give the current best answer and say briefly what to double-check.
- In emergencies always put the single emergency number 112 first.
- If the user asks for the nearest place (pharmacy, metro, shop, hospital), answer briefly and \
suggest pressing the "📍" button to send their location.
- Keep it short and easy to read: up to about 200 words, short bullet lists, a few emoji are fine.
- Format with simple Markdown only: **bold**, lists with "-", links as [text](url). No tables, no headings.
"""
WEB_RULE = "- Use the web search results for up-to-date facts and add 1-3 links to the most useful sources.\n"
NO_WEB_RULE = (
    "- Answer from your own knowledge. Where useful, add 1-2 links to official sites "
    "(mos.ru, gosuslugi.ru, mosmetro.ru) that you are sure exist.\n"
)


class LLMError(Exception):
    pass


class LLM:
    def __init__(self, config: Config):
        self.config = config
        self.history: dict[int, deque] = defaultdict(lambda: deque(maxlen=HISTORY_MESSAGES))
        self.session: aiohttp.ClientSession | None = None

    async def _session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = make_session(self.config.proxy_url, timeout=aiohttp.ClientTimeout(total=120))
        return self.session

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def ask(self, user_id: int, language: str, question: str, remember: bool = True) -> str:
        system = SYSTEM_PROMPT.format(
            today=date.today().isoformat(),
            language=language,
            sources_rule=WEB_RULE if self.config.web_search else NO_WEB_RULE,
        )
        messages = [{"role": "system", "content": system}]
        if remember:
            messages += list(self.history[user_id])
        messages.append({"role": "user", "content": question})

        payload = {"model": self.config.model, "messages": messages, "max_tokens": 900}
        if self.config.web_search:
            payload["plugins"] = [{"id": "web", "max_results": self.config.web_max_results}]

        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "HTTP-Referer": "https://t.me/",
            "X-Title": "Help in Moscow",
        }
        session = await self._session()
        async with session.post(API_URL, json=payload, headers=headers) as resp:
            data = await resp.json(content_type=None)
            if resp.status != 200 or "choices" not in data:
                log.error("OpenRouter error %s: %s", resp.status, data)
                raise LLMError(str(data.get("error", data)))

        answer = (data["choices"][0]["message"].get("content") or "").strip()
        if not answer:
            raise LLMError("empty answer")
        if remember:
            self.history[user_id].append({"role": "user", "content": question})
            self.history[user_id].append({"role": "assistant", "content": answer})
        return answer


_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_HEADING = re.compile(r"^#{1,6}\s*(.+)$", re.MULTILINE)
_BULLET = re.compile(r"^(\s*)[-*]\s+", re.MULTILINE)


def markdown_to_telegram_html(text: str) -> str:
    """Turn the simple Markdown the model writes into safe Telegram HTML."""
    links: list[str] = []

    def keep_link(m: re.Match) -> str:
        links.append(f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>')
        return f"\x00{len(links) - 1}\x00"

    text = _LINK.sub(keep_link, text)
    text = html.escape(text, quote=False)
    text = _HEADING.sub(r"**\1**", text)
    text = _BOLD.sub(r"<b>\1</b>", text)
    text = _BULLET.sub(r"\1• ", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: links[int(m.group(1))], text)
