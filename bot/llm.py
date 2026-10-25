import html
import logging
import re
from collections import defaultdict, deque
from datetime import date

import aiohttp

from . import search
from .config import Config
from .net import make_session

log = logging.getLogger(__name__)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
HISTORY_MESSAGES = 6  # last 3 questions and answers per user

SYSTEM_PROMPT = """You are "Help in Moscow", a friendly Telegram assistant for foreigners \
(students, tourists, interns, new residents) who live in or visit Moscow, Russia. Today is {today}.

Content rules:
{language_rule}- Always give a concrete, practical answer: where to go, what to bring, prices, steps, official \
websites and apps. Never tell the user to figure it out on their own.
{sources_rule}- If something changes often (prices, rules), give the current best answer and say briefly what to double-check.
- In emergencies always put the single emergency number 112 first.
- Key Moscow facts, checked in October 2026. Use them unless an official site in the search results shows \
a newer number: metro, MCC, MCD (Central zone) and buses with a Troika card ("Koshelek" fare) 75 RUB per ride; \
"90 minutes" fare (one metro ride plus unlimited buses) 112 RUB; contactless bank card 83 RUB; Face Pay \
biometric 71 RUB; Troika card deposit 150 RUB; emergency number 112.
- If the user asks for the nearest place (pharmacy, metro, shop, hospital), answer briefly and \
suggest pressing the "📍" button to send their location.
- If the question is not about life in Moscow or Russia, answer in one or two friendly sentences \
and offer help with life in Moscow.

Format every answer like this example (translated to the reply language):

📱 You can get a SIM card at:

• Mobile operator stores (**MTS**, **Beeline**, **MegaFon**, **Tele2**)
• Electronics stores
• Post offices

To register a SIM card, you will need a passport or another identity document.

🔗 [mts.ru](https://mts.ru)

Format rules:
- First line: one fitting emoji and a short heading that ends with a colon.
- Then 3-5 short bullets, each starting with "• ", at most about 12 words each. Use **bold** only for key names.
- Then 1-2 short sentences with the most important tip or warning.
- Optionally a last line starting with "🔗 " with 1-2 links as [text](url).
- At most about 100 words. No tables, no headings with #, no JSON, no code.
"""


WEB_RULE = "- Use the web search results for up-to-date facts and add 1-3 links to the most useful sources.\n"
NO_WEB_RULE = (
    "- Answer from your own knowledge. Do not invent names, prices or rules you are not sure about.\n"
    "- Links: only main pages of well-known sites (https://www.mos.ru, https://www.gosuslugi.ru, "
    "https://mosmetro.ru, operator or shop main pages), never deep links.\n"
)


FREE_WEB_RULE = (
    "- Below are fresh web search results. Prefer them over your memory for prices, fares, rules "
    "and names, because your memory may be outdated. Copy numbers exactly from the results; if they "
    "disagree, trust official sites (mos.ru, mosmetro.ru, gosuslugi.ru). Do not add numbers that are not in "
    "the results or the key facts.Add 1-2 links copied exactly from these results.\n"
)
LANGUAGE_RULE = "- Reply in {language}. Only if the user clearly writes in a different language, reply in that language.\n"
STRICT_LANGUAGE_RULE = "- Always reply in {language}, even though the question below is written in English.\n"


class LLMError(Exception):
    pass


class LLMBusy(LLMError):
    """Rate limit: the free tier allows about 20 requests a minute and 50 a day."""


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

    async def ask(
        self,
        user_id: int,
        language: str,
        question: str,
        remember: bool = True,
        strict_language: bool = False,
        search_query: str | None = None,
    ) -> str:
        """Answer a question. Topic buttons pass strict_language, because their question is in English."""
        context = ""
        if not self.config.web_search and self.config.free_search:
            context = await search.web_context(search_query or f"{question} Москва", self.config.proxy_url)
        # Paid OpenRouter search: always, or only when the free search found nothing.
        use_web = self.config.web_search or (self.config.free_search and not context and self.config.web_fallback)

        if use_web:
            sources_rule = WEB_RULE
        elif context:
            sources_rule = FREE_WEB_RULE
        else:
            sources_rule = NO_WEB_RULE
        language_rule = (STRICT_LANGUAGE_RULE if strict_language else LANGUAGE_RULE).format(language=language)
        system = SYSTEM_PROMPT.format(
            today=date.today().isoformat(),
            language_rule=language_rule,
            sources_rule=sources_rule,
        )
        messages = [{"role": "system", "content": system}]
        if context:
            messages.append({"role": "system", "content": f"Web search results ({date.today().isoformat()}):\n\n{context}"})
        if remember:
            messages += list(self.history[user_id])
        # Free models follow the language of the last message, so the reminder goes right after the question.
        reminder = f"Answer only in {language}. Keep the format: emoji heading, 3-5 bullets, at most 100 words."
        messages.append({"role": "user", "content": f"{question}\n\n({reminder})"})

        models = [self.config.model] + ([self.config.fallback_model] if self.config.fallback_model else [])
        answer = ""
        for i, model in enumerate(models):
            try:
                answer = await self._complete(model, messages, use_web)
                break
            except LLMError:
                if i == len(models) - 1:
                    raise
                log.warning("Model %s failed, trying %s", model, models[i + 1], exc_info=True)

        if remember:
            self.history[user_id].append({"role": "user", "content": question})
            self.history[user_id].append({"role": "assistant", "content": answer})
        return answer

    async def _complete(self, model: str, messages: list[dict], use_web: bool) -> str:
        payload = {"model": model, "messages": messages, "max_tokens": 1000}
        if not self.config.reasoning:
            # Hidden reasoning eats the token limit and gives empty or cut-off answers.
            payload["reasoning"] = {"enabled": False}
        if use_web:
            payload["plugins"] = [{"id": "web", "max_results": self.config.web_max_results}]

        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "HTTP-Referer": "https://t.me/",
            "X-Title": "Help in Moscow",
        }
        session = await self._session()
        try:
            async with session.post(API_URL, json=payload, headers=headers) as resp:
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as e:
            raise LLMError(f"request to {model} failed: {e!r}") from e
        if resp.status == 429:
            raise LLMBusy(str(data.get("error", data)))
        if resp.status != 200 or "choices" not in data:
            log.error("OpenRouter error %s from %s: %s", resp.status, model, data)
            raise LLMError(str(data.get("error", data)))

        choice = data["choices"][0]
        answer = clean_answer(choice["message"].get("content") or "")
        if choice.get("finish_reason") == "length" and "\n" in answer:
            # Cut off by the token limit: drop the unfinished last line.
            answer = answer.rsplit("\n", 1)[0].rstrip()
        if not answer:
            raise LLMError("empty answer")
        return answer


_THINK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def clean_answer(text: str) -> str:
    """Drop reasoning blocks and answers that are JSON instead of text."""
    text = _THINK.sub("", text).strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
    if text.startswith("{") and text.endswith("}"):
        return ""
    return text


_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<![*\w])\*(?!\s)([^*\n]+?)\*(?![*\w])")
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
    text = _ITALIC.sub(r"<i>\1</i>", text)
    text = _BULLET.sub(r"\1• ", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: links[int(m.group(1))], text)
