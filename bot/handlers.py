import logging
import re
import time

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.chat_action import ChatActionSender

from . import geo
from .config import Config
from .db import Database
from .i18n import (
    DEFAULT_LANG,
    LANGUAGES,
    PLACE_CATEGORIES,
    TOPIC_QUESTIONS,
    TOPIC_SEARCH,
    TOPICS,
    all_labels,
    language_name,
    place_label,
    t,
    topic_label,
)
from .llm import LLM, LLMBusy, markdown_to_telegram_html
from .voice import Transcriber

log = logging.getLogger(__name__)

TOPIC_CACHE_SECONDS = 6 * 60 * 60
TELEGRAM_LIMIT = 4000
ROUTE_WAIT_SECONDS = 10 * 60  # how long the bot waits for "from — to" after the route button
# "Red Square — MSU", "from Red Square to MSU", "Кремль -> ВДНХ", "от Кремля до ВДНХ"
ROUTE_SPLIT = re.compile(r"\s*(?:—|–|->|→|=>|\s-\s|\bto\b|\bдо\b)\s*", re.IGNORECASE)
ROUTE_FROM = re.compile(r"^\s*(?:from|от|из|с)\s+", re.IGNORECASE)
ROUTE_MODES = [("route_transit", "mt"), ("route_walk", "pd"), ("route_car", "auto")]

# Button label (in any language) -> what it does
TOPIC_BUTTONS = all_labels(lambda lang: [(topic_label(lang, k), k) for k in TOPICS])
NEARBY_BUTTONS = all_labels(lambda lang: [(t(lang, "nearby"), "nearby")])
ROUTE_BUTTONS = all_labels(lambda lang: [(t(lang, "route"), "route")])
LANGUAGE_BUTTONS = all_labels(lambda lang: [(t(lang, "language"), "language")])


def language_keyboard() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=label, callback_data=f"lang:{code}") for code, (label, _) in LANGUAGES.items()]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    topics = [KeyboardButton(text=topic_label(lang, k)) for k in TOPICS]
    rows = [topics[i:i + 2] for i in range(0, len(topics), 2)]
    rows.append([KeyboardButton(text=t(lang, "nearby")), KeyboardButton(text=t(lang, "route"))])
    rows.append([KeyboardButton(text=t(lang, "language"))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def route_keyboard(lang: str, start: dict, end: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=t(lang, key), url=geo.route_link(start["lat"], start["lon"], end["lat"], end["lon"], mode))]
        for key, mode in ROUTE_MODES])


def split_route(text: str) -> tuple[str | None, str]:
    """'Red Square — MSU' -> ('Red Square', 'MSU'); 'MSU' -> (None, 'MSU')."""
    parts = [p.strip(" ,.?!") for p in ROUTE_SPLIT.split(ROUTE_FROM.sub("", text), maxsplit=1)]
    if len(parts) == 2 and parts[0] and parts[1]:
        return parts[0], parts[1]
    return None, parts[-1]


def location_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "send_location"), request_location=True)],
            [KeyboardButton(text=t(lang, "language"))],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def places_keyboard(lang: str) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=place_label(lang, c), callback_data=f"place:{c}") for c in PLACE_CATEGORIES]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def rating_keyboard(answer_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👍", callback_data=f"rate:{answer_id}:1"),
        InlineKeyboardButton(text="👎", callback_data=f"rate:{answer_id}:-1"),
    ]])


def setup_router(config: Config, db: Database, llm: LLM, transcriber: Transcriber) -> Router:
    router = Router()
    topic_cache: dict[tuple[str, str], tuple[float, str]] = {}
    route_waiting: dict[int, float] = {}  # user id -> when the route button was pressed

    def waits_for_route(message: Message) -> bool:
        started = route_waiting.get(message.from_user.id)
        return started is not None and time.time() - started < ROUTE_WAIT_SECONDS

    def user_lang(message_or_query) -> str:
        user = message_or_query.from_user
        lang = db.get_lang(user.id)
        if lang:
            return lang
        code = (user.language_code or "").split("-")[0]
        return code if code in LANGUAGES else DEFAULT_LANG

    async def send_answer(message: Message, placeholder: Message | None, question: str, answer: str,
                          lang: str) -> None:
        answer_id = db.log_answer(message.from_user.id, lang, question, answer)
        markup = rating_keyboard(answer_id)
        text = markdown_to_telegram_html(answer)[:TELEGRAM_LIMIT]
        try:
            if placeholder:
                await placeholder.edit_text(text, parse_mode="HTML", disable_web_page_preview=True,
                                            reply_markup=markup)
            else:
                await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup)
        except TelegramBadRequest:
            # The model produced something Telegram can't parse: send it as plain text.
            plain = answer[:TELEGRAM_LIMIT]
            if placeholder:
                await placeholder.edit_text(plain, disable_web_page_preview=True, reply_markup=markup)
            else:
                await message.answer(plain, disable_web_page_preview=True, reply_markup=markup)

    async def answer_with_llm(message: Message, question: str, lang: str, cache_key=None,
                              search_query: str | None = None) -> None:
        if cache_key and cache_key in topic_cache:
            saved_at, cached = topic_cache[cache_key]
            if time.time() - saved_at < TOPIC_CACHE_SECONDS:
                await send_answer(message, None, question, cached, lang)
                return

        mine, total = db.usage_today(message.from_user.id)
        if mine >= config.user_daily_limit:
            await message.answer(t(lang, "limit_user"))
            return
        if total >= config.global_daily_limit:
            await message.answer(t(lang, "limit_global"))
            return

        placeholder = await message.answer(t(lang, "thinking"))
        try:
            async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
                answer = await llm.ask(
                    message.from_user.id,
                    language_name(lang),
                    question,
                    remember=cache_key is None,
                    strict_language=cache_key is not None,
                    search_query=search_query,
                )
        except LLMBusy:
            log.warning("LLM rate limited")
            await placeholder.edit_text(t(lang, "busy"))
            return
        except Exception:
            log.exception("LLM request failed")
            await placeholder.edit_text(t(lang, "error"))
            return

        db.add_usage(message.from_user.id)
        if cache_key:
            topic_cache[cache_key] = (time.time(), answer)
        await send_answer(message, placeholder, question, answer, lang)

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        if db.get_lang(message.from_user.id) is None:
            await message.answer(t(user_lang(message), "choose_language"), reply_markup=language_keyboard())
            return
        lang = user_lang(message)
        await message.answer(t(lang, "welcome"), parse_mode="HTML", reply_markup=main_keyboard(lang))

    @router.message(Command("chooselanguage", "language"))
    async def choose_language(message: Message) -> None:
        await message.answer(t(user_lang(message), "choose_language"), reply_markup=language_keyboard())

    @router.message(Command("help"))
    async def help_cmd(message: Message) -> None:
        lang = user_lang(message)
        await message.answer(t(lang, "help"), reply_markup=main_keyboard(lang))

    @router.callback_query(F.data.startswith("lang:"))
    async def language_chosen(query: CallbackQuery) -> None:
        lang = query.data.split(":", 1)[1]
        if lang not in LANGUAGES:
            await query.answer()
            return
        db.set_lang(query.from_user.id, lang)
        await query.answer()
        await query.message.edit_text(t(lang, "language_selected"))
        await query.message.answer(t(lang, "welcome"), parse_mode="HTML", reply_markup=main_keyboard(lang))

    @router.message(F.text.in_(LANGUAGE_BUTTONS))
    async def language_button(message: Message) -> None:
        await choose_language(message)

    @router.message(F.text.in_(NEARBY_BUTTONS))
    async def nearby_button(message: Message) -> None:
        lang = user_lang(message)
        route_waiting.pop(message.from_user.id, None)
        await message.answer(t(lang, "nearby_ask"), reply_markup=location_keyboard(lang))

    @router.message(F.text.in_(ROUTE_BUTTONS))
    async def route_button(message: Message) -> None:
        lang = user_lang(message)
        route_waiting[message.from_user.id] = time.time()
        await message.answer(t(lang, "route_ask"), reply_markup=location_keyboard(lang))

    @router.message(F.location)
    async def location_received(message: Message) -> None:
        lang = user_lang(message)
        db.set_location(message.from_user.id, message.location.latitude, message.location.longitude)
        if waits_for_route(message):
            # The location is the start of the route: now we only need where to go.
            await message.answer(t(lang, "route_dest_ask"), reply_markup=main_keyboard(lang))
            return
        await message.answer("✅ 📍", reply_markup=main_keyboard(lang))
        await message.answer(t(lang, "nearby_choose"), reply_markup=places_keyboard(lang))

    async def build_route(message: Message, lang: str) -> None:
        start_text, end_text = split_route(message.text)
        waiting = await message.answer(t(lang, "thinking"))
        async with ChatActionSender.find_location(bot=message.bot, chat_id=message.chat.id):
            if start_text:
                start = await geo.geocode(start_text, lang, config.proxy_url)
            else:
                location = db.get_location(message.from_user.id)
                start = {"name": t(lang, "route_from_here"), "lat": location[0], "lon": location[1]} if location else None
            end = await geo.geocode(end_text, lang, config.proxy_url)

        if start is None and not start_text:
            await waiting.edit_text(t(lang, "route_need_start"))
            return
        missing = [text for text, place in ((start_text, start), (end_text, end)) if text and place is None]
        if missing:
            await waiting.edit_text(t(lang, "route_not_found").format(place=_escape(missing[0])), parse_mode="HTML")
            return

        route_waiting.pop(message.from_user.id, None)
        km = geo.distance_m(start["lat"], start["lon"], end["lat"], end["lon"]) / 1000
        text = (f"🧭 <b>{_escape(start['name'])}</b>\n→ <b>{_escape(end['name'])}</b>\n\n"
                f"{t(lang, 'route_distance').format(km=f'{km:.1f}')}\n{t(lang, 'route_choose')}")
        await waiting.edit_text(text, parse_mode="HTML", reply_markup=route_keyboard(lang, start, end))

    @router.callback_query(F.data.startswith("place:"))
    async def place_chosen(query: CallbackQuery) -> None:
        lang = user_lang(query)
        category = query.data.split(":", 1)[1]
        location = db.get_location(query.from_user.id)
        await query.answer()
        if category not in PLACE_CATEGORIES or location is None:
            await query.message.answer(t(lang, "location_again"), reply_markup=location_keyboard(lang))
            return

        lat, lon = location
        map_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text=t(lang, "open_on_map"), url=geo.search_link(category, lat, lon))]])
        waiting = await query.message.answer(t(lang, "thinking"))
        try:
            async with ChatActionSender.find_location(bot=query.bot, chat_id=query.message.chat.id):
                places = await geo.find_nearby(category, lat, lon, lang, proxy=config.proxy_url)
        except Exception:
            # The free OSM servers are often overloaded: send a map search instead.
            log.warning("Nearby search failed, sending a map link", exc_info=True)
            places = []
        if not places:
            await waiting.edit_text(f"{place_label(lang, category)}\n{t(lang, 'nearby_map')}", reply_markup=map_button)
            return

        lines = [f"<b>{place_label(lang, category)}</b>"]
        for p in places:
            name = p["name"] or t(lang, category)
            link = geo.route_link(lat, lon, p["lat"], p["lon"])
            line = f'• {_escape(name)} ({round(p["distance"])} m) <a href="{link}">{t(lang, "open_map")}</a>'
            if p["hours"]:
                line += f"\n   🕒 {_escape(p['hours'])}"
            lines.append(line)
        await waiting.edit_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True,
                                reply_markup=map_button)

    @router.message(F.text.in_(TOPIC_BUTTONS))
    async def topic_button(message: Message) -> None:
        lang = user_lang(message)
        route_waiting.pop(message.from_user.id, None)
        topic = TOPIC_BUTTONS[message.text]
        await answer_with_llm(message, TOPIC_QUESTIONS[topic], lang, cache_key=(topic, lang),
                              search_query=TOPIC_SEARCH[topic])

    @router.callback_query(F.data.startswith("rate:"))
    async def rated(query: CallbackQuery) -> None:
        _, answer_id, value = query.data.split(":")
        db.rate(int(answer_id), query.from_user.id, 1 if value == "1" else -1)
        await query.answer(t(user_lang(query), "thanks"))
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass

    @router.message(Command("stats"))
    async def stats(message: Message) -> None:
        if message.from_user.id not in config.admin_ids:
            return
        s = db.stats()
        langs = ", ".join(f"{lang} {n}" for lang, n in s["languages"]) or "-"
        bad = "\n".join(f"• {_escape(q[:120])}" for (q,) in s["bad"]) or "-"
        await message.answer(
            f"<b>📊 Статистика</b>\n\n"
            f"Пользователей: {s['users']} (сегодня новых {s['users_today']})\n"
            f"Вопросов: {s['questions']} (сегодня {s['questions_today']})\n"
            f"Оценки: 👍 {s['likes']} · 👎 {s['dislikes']}\n"
            f"Языки: {langs}\n\n"
            f"<b>Последние вопросы с 👎:</b>\n{bad}",
            parse_mode="HTML",
        )

    @router.message(F.voice)
    async def voice_question(message: Message) -> None:
        lang = user_lang(message)
        if not (config.voice and transcriber.available):
            await message.answer(t(lang, "voice_off"))
            return
        try:
            async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
                audio = await message.bot.download(message.voice)
                text = await transcriber.transcribe(audio.read())
        except Exception:
            log.exception("Voice transcription failed")
            text = ""
        if not text:
            await message.answer(t(lang, "voice_error"))
            return
        await message.answer(f"{t(lang, 'voice_heard')} <i>{_escape(text)}</i>", parse_mode="HTML")
        await answer_with_llm(message, text, lang)

    @router.message(Command("route"))
    async def route_cmd(message: Message) -> None:
        await route_button(message)

    @router.message(F.text)
    async def free_question(message: Message) -> None:
        lang = user_lang(message)
        if waits_for_route(message) and not message.text.startswith("/"):
            await build_route(message, lang)
            return
        await answer_with_llm(message, message.text, lang)

    return router


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
