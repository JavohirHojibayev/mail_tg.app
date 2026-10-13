import logging
import math
from telebot import TeleBot
from telebot.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
)
from services.data_manager import DataManager
from services.user_prefs import get_user_lang, set_user_lang
from utils.pdf_generator import generate_employees_pdf
from utils.locales import t, LANGUAGES

logger = logging.getLogger(__name__)

PAGE_SIZE = 10

def get_main_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Foydalanuvchi tili bo'yicha asosiy reply menyu tugmalari"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, row_width=2)
    keyboard.add(
        KeyboardButton(t("btn_list", lang)),
        KeyboardButton(t("btn_search", lang))
    )
    keyboard.add(
        KeyboardButton(t("btn_pdf", lang)),
        KeyboardButton(t("btn_help", lang))
    )
    keyboard.add(
        KeyboardButton(t("btn_lang", lang))
    )
    return keyboard

def get_lang_inline_markup() -> InlineKeyboardMarkup:
    """Tilni tanlash uchun inline tugmalar"""
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang:ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="set_lang:en")
    )
    return markup

def send_language_prompt(bot: TeleBot, chat_id: int):
    """Til tanlash kerakligini takidlovchi xabar"""
    text = (
        "🌐 *Пожалуйста, выберите язык интерфейса / Please select language:*\n\n"
        "⚠️ _Для работы со справочником необходимо выбрать один из 2 языков:_\n"
        "_To use the corporate directory, please select one of the 2 languages:_"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_lang_inline_markup())

def update_bot_commands_for_lang(bot: TeleBot, chat_id: int, lang: str):
    """Telegram komandalar menyusini tanlangan tilda sozlash"""
    try:
        commands = [
            BotCommand("list", t("cmd_list", lang)),
            BotCommand("pdf", t("cmd_pdf", lang)),
            BotCommand("search", t("cmd_search", lang)),
            BotCommand("help", t("cmd_help", lang)),
            BotCommand("lang", t("cmd_lang", lang)),
            BotCommand("start", t("cmd_start", lang)),
        ]
        bot.set_my_commands(commands)
    except Exception as e:
        logger.warning(f"set_my_commands xatosi: {e}")

def build_pagination_text_and_markup(users: list, page: int, lang: str = "ru", prefix: str = "pg"):
    total_users = len(users)
    total_pages = max(1, math.ceil(total_users / PAGE_SIZE))
    page = max(0, min(page, total_pages - 1))

    start_idx = page * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total_users)
    page_users = users[start_idx:end_idx]

    lines = [
        t("pagination_header", lang),
        t("pagination_page_info", lang, page=page + 1, total_pages=total_pages, total_users=total_users),
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]

    for idx, u in enumerate(page_users, start=start_idx + 1):
        name = u.get("name") or u.get("email", "").split("@")[0]
        email = u.get("email", "")
        lines.append(f"*{idx}.* 👤 *{name}*\n     📧 `{email}`\n")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(t("pagination_footer", lang))

    text = "\n".join(lines)

    # Inline navigatsiya tugmalari
    markup = InlineKeyboardMarkup()
    nav_row = []

    if page > 0:
        nav_row.append(InlineKeyboardButton(t("btn_prev", lang), callback_data=f"{prefix}:{page-1}"))
    else:
        nav_row.append(InlineKeyboardButton("⏹", callback_data="noop"))

    nav_row.append(InlineKeyboardButton(f"📄 {page+1} / {total_pages}", callback_data="noop"))

    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(t("btn_next", lang), callback_data=f"{prefix}:{page+1}"))
    else:
        nav_row.append(InlineKeyboardButton("⏹", callback_data="noop"))

    markup.row(*nav_row)
    markup.add(
        InlineKeyboardButton(t("btn_export_all_pdf", lang, total_users=total_users), callback_data="export_pdf")
    )

    return text, markup

def format_user_card(user: dict, lang: str = "ru") -> str:
    name = user.get("name") or user.get("email", "").split("@")[0]
    email = user.get("email", "Mavjud emas")
    return t("user_card", lang, name=name, email=email)

def send_pdf_document(bot: TeleBot, chat_id: int, users: list, lang: str = "ru"):
    wait_msg = bot.send_message(
        chat_id,
        t("pdf_wait", lang),
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(lang)
    )
    try:
        pdf_path = generate_employees_pdf(users)
        with open(pdf_path, "rb") as f:
            bot.send_document(
                chat_id,
                f,
                caption=t("pdf_caption", lang, count=len(users)),
                parse_mode="Markdown",
                reply_markup=get_main_keyboard(lang)
            )
        try:
            bot.delete_message(chat_id, wait_msg.message_id)
        except Exception:
            pass
    except Exception as e:
        logger.error(f"PDF yuborishda xatolik: {e}")
        bot.edit_message_text(
            f"❌ PDF xatosi: {str(e)}",
            chat_id=chat_id,
            message_id=wait_msg.message_id
        )

def register_handlers(bot: TeleBot, data_manager: DataManager):

    # Standart buyruqlar menyusini o'rnatish
    try:
        bot.set_my_commands([
            BotCommand("list", "📋 Список сотрудников / Employee list"),
            BotCommand("pdf", "📥 Скачать PDF / Download PDF"),
            BotCommand("search", "🔍 Поиск / Search"),
            BotCommand("help", "ℹ️ Помощь / Help"),
            BotCommand("lang", "🌐 Выбор языка / Select language"),
            BotCommand("start", "🔄 Главное меню / Start"),
        ])
    except Exception as e:
        logger.warning(f"set_my_commands xatosi: {e}")

    # /start
    @bot.message_handler(commands=['start'])
    def cmd_start(message: Message):
        chat_id = message.chat.id
        lang = get_user_lang(chat_id)

        # Start bosilganda tilni tanlash kerakligi doim takidlanadi
        send_language_prompt(bot, chat_id)

        if lang:
            users_count = len(data_manager.get_users())
            bot.send_message(
                chat_id,
                t("start_text", lang, count=users_count),
                parse_mode="Markdown",
                reply_markup=get_main_keyboard(lang)
            )

    # /lang komandasi
    @bot.message_handler(commands=['lang'])
    def cmd_lang(message: Message):
        send_language_prompt(bot, message.chat.id)

    # /help va Yordam tugmasi
    @bot.message_handler(commands=['help'])
    @bot.message_handler(func=lambda m: m.text in [
        t("btn_help", "ru"), t("btn_help", "en"), "ℹ️ Yordam", "ℹ️ Помощь", "ℹ️ Help"
    ])
    def cmd_help(message: Message):
        lang = get_user_lang(message.chat.id) or "ru"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("💬 Javohir Hojibayev (Telegram)", url="https://t.me/Javohir_Hojibayev")
        )
        markup.add(
            InlineKeyboardButton("💬 Nurbek Jumayev (Telegram)", url="https://t.me/nurbekjumayev")
        )
        bot.send_message(
            message.chat.id,
            t("help_text", lang),
            parse_mode="Markdown",
            reply_markup=markup,
            disable_web_page_preview=True
        )

    # 📋 Ro'yxat komandasi (/list)
    @bot.message_handler(commands=['list'])
    @bot.message_handler(func=lambda m: m.text in [
        t("btn_list", "ru"), t("btn_list", "en"), "📋 Список сотрудников", "📋 Employee List", "📋 Xodimlar ro'yxati"
    ])
    def cmd_list(message: Message):
        lang = get_user_lang(message.chat.id) or "ru"
        users = data_manager.get_users()
        if not users:
            bot.send_message(
                message.chat.id,
                "⚠️ Список пуст / Directory empty.",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard(lang)
            )
            return

        text, markup = build_pagination_text_and_markup(users, page=0, lang=lang, prefix="pg")
        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=markup
        )

    # 📥 PDF yuklab olish (/pdf)
    @bot.message_handler(commands=['pdf'])
    @bot.message_handler(func=lambda m: m.text in [
        t("btn_pdf", "ru"), t("btn_pdf", "en"), "📥 Скачать PDF", "📥 Download PDF", "📥 PDF yuklab olish"
    ])
    def cmd_pdf(message: Message):
        lang = get_user_lang(message.chat.id) or "ru"
        users = data_manager.get_users()
        if not users:
            bot.send_message(
                message.chat.id,
                "⚠️ Список пуст / Directory empty.",
                reply_markup=get_main_keyboard(lang)
            )
            return
        send_pdf_document(bot, message.chat.id, users, lang=lang)

    # 🔍 Qidirish prompti (/search)
    @bot.message_handler(commands=['search'])
    @bot.message_handler(func=lambda m: m.text in [
        t("btn_search", "ru"), t("btn_search", "en"), "🔍 Поиск", "🔍 Search", "🔍 Qidirish"
    ])
    def btn_search_prompt(message: Message):
        lang = get_user_lang(message.chat.id) or "ru"
        bot.send_message(
            message.chat.id,
            t("search_prompt", lang),
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(lang)
        )

    # 🌐 Til almashtirish tugmasi
    @bot.message_handler(func=lambda m: m.text in [
        t("btn_lang", "ru"), t("btn_lang", "en"), "🌐 Язык / Language", "🌐 Language / Язык"
    ])
    def btn_lang_prompt(message: Message):
        send_language_prompt(bot, message.chat.id)

    # Callback handler (Til tanlash, Pagination & PDF)
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callbacks(call: CallbackQuery):
        data = call.data
        chat_id = call.message.chat.id

        if data == "noop":
            bot.answer_callback_query(call.id)
            return

        # 1. Til tanlash
        if data.startswith("set_lang:"):
            lang = data.split(":")[1]
            set_user_lang(chat_id, lang)
            bot.answer_callback_query(call.id, "✅")
            update_bot_commands_for_lang(bot, chat_id, lang)

            # Til o'rnatilganligi haqida xabar
            bot.send_message(
                chat_id,
                t("lang_selected_confirm", lang),
                parse_mode="Markdown"
            )

            # Asosiy salomlashish va menyuni chiqarish
            users_count = len(data_manager.get_users())
            bot.send_message(
                chat_id,
                t("start_text", lang, count=users_count),
                parse_mode="Markdown",
                reply_markup=get_main_keyboard(lang)
            )
            return

        # 2. PDF yuklab olish
        if data == "export_pdf":
            lang = get_user_lang(chat_id) or "ru"
            bot.answer_callback_query(call.id, "PDF...")
            users = data_manager.get_users()
            send_pdf_document(bot, chat_id, users, lang=lang)
            return

        # 3. 10 qatordan iborat pagination: pg:<page>
        if data.startswith("pg:"):
            page = int(data.split(":")[1])
            lang = get_user_lang(chat_id) or "ru"
            users = data_manager.get_users()
            text, markup = build_pagination_text_and_markup(users, page=page, lang=lang, prefix="pg")
            try:
                bot.edit_message_text(
                    text,
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    parse_mode="Markdown",
                    reply_markup=markup
                )
            except Exception:
                pass
            bot.answer_callback_query(call.id)
            return

    # Foydalanuvchi istalgan matn yozganda avtomatik qidiruv
    @bot.message_handler(func=lambda m: True)
    def handle_text_search(message: Message):
        chat_id = message.chat.id
        query = message.text.strip()
        if not query or query.startswith("/"):
            return

        lang = get_user_lang(chat_id)
        if not lang:
            # Agar foydalanuvchi hali tilni tanlamagan bo'lsa, avval tilni tanlashni so'raymiz
            send_language_prompt(bot, chat_id)
            return

        users = data_manager.get_users(search=query)

        if not users:
            bot.send_message(
                chat_id,
                t("search_not_found", lang, query=query),
                parse_mode="Markdown",
                reply_markup=get_main_keyboard(lang)
            )
            return

        if len(users) == 1:
            user = users[0]
            text = (
                t("search_found_single", lang) +
                format_user_card(user, lang)
            )
            bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_main_keyboard(lang))
        else:
            header = t("search_found_multiple", lang, query=query, count=len(users))
            lines = [header]
            for idx, u in enumerate(users[:10], start=1):
                name = u.get("name") or u.get("email", "").split("@")[0]
                email = u.get("email", "")
                lines.append(f"*{idx}.* 👤 *{name}*\n     📧 `{email}`\n")

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(t("btn_results_pdf", lang), callback_data="export_pdf")
            )

            bot.send_message(
                chat_id,
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=markup
            )
