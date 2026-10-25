"""Free web search: DuckDuckGo results plus the text of the top pages.

Used when the paid OpenRouter web plugin is off, so that the model answers
from fresh pages instead of its outdated memory.
"""

import asyncio
import logging
import re
from html import unescape

import aiohttp

from .net import make_session

log = logging.getLogger(__name__)

MAX_RESULTS = 5
PAGES_TO_READ = 2
PAGE_CHARS = 2500
SNIPPET_CHARS = 300
TIMEOUT_S = 12
PAGE_TIMEOUT_S = 6

_DROP = re.compile(r"<(script|style|noscript|svg|header|footer|nav|form)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


def _ddg(query: str) -> list[dict]:
    from ddgs import DDGS

    return list(DDGS().text(query, region="ru-ru", max_results=MAX_RESULTS))


def html_to_text(html: str) -> str:
    text = _DROP.sub(" ", html)
    text = _TAG.sub(" ", text)
    return _SPACE.sub(" ", unescape(text)).strip()


async def _read_page(session: aiohttp.ClientSession, url: str) -> str:
    try:
        async with session.get(url) as resp:
            if resp.status != 200 or "html" not in resp.headers.get("Content-Type", ""):
                return ""
            return html_to_text(await resp.text(errors="ignore"))[:PAGE_CHARS]
    except Exception as e:  # a slow or broken page must not break the answer
        log.info("Could not read %s: %s", url, e)
        return ""


async def web_context(query: str, proxy: str | None = None) -> str:
    """Return search results as text for the prompt, or "" if search failed."""
    try:
        results = await asyncio.wait_for(asyncio.to_thread(_ddg, query), TIMEOUT_S)
    except Exception as e:
        log.warning("Web search failed for %r: %s", query, e)
        return ""
    if not results:
        return ""

    headers = {"User-Agent": "Mozilla/5.0 (compatible; HelpInMoscowBot/1.0)"}
    async with make_session(proxy, timeout=aiohttp.ClientTimeout(total=PAGE_TIMEOUT_S), headers=headers) as session:
        pages = await asyncio.gather(*(_read_page(session, r["href"]) for r in results[:PAGES_TO_READ]))

    blocks = []
    for i, r in enumerate(results):
        text = pages[i] if i < len(pages) and pages[i] else (r.get("body") or "")[:SNIPPET_CHARS]
        blocks.append(f"[{i + 1}] {r.get('title', '')}\nURL: {r['href']}\n{text}")
    return "\n\n".join(blocks)
