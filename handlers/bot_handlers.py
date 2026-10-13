import os
import logging
import math
from telebot import TeleBot
from telebot.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
)
from services.data_manager import DataManager
from utils.pdf_generator import generate_employees_pdf

logger = logging.getLogger(__name__)

PAGE_SIZE = 10

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, row_width=2)
    keyboard.add(
        KeyboardButton("📋 Xodimlar ro'yxati"),
        KeyboardButton("🔍 Qidirish")
    )
    keyboard.add(
        KeyboardButton("📥 PDF yuklab olish"),
        KeyboardButton("ℹ️ Yordam")
    )
    return keyboard

def build_pagination_text_and_markup(users: list, page: int, prefix: str = "pg"):
    total_users = len(users)
    total_pages = max(1, math.ceil(total_users / PAGE_SIZE))
    page = max(0, min(page, total_pages - 1))

    start_idx = page * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total_users)
    page_users = users[start_idx:end_idx]

    lines = [
        "📋 *DKZ AJ XODIMLAR RO'YXATI*",
        f"📊 _Sahifa: {page + 1} / {total_pages} (Jami: {total_users} nafar)_\n",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]

    for idx, u in enumerate(page_users, start=start_idx + 1):
        name = u.get("name") or u.get("email", "").split("@")[0]
        email = u.get("email", "")
        lines.append(f"*{idx}.* 👤 *{name}*\n     📧 `{email}`\n")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("💡 _Pochta manzilini nusxalash uchun ustiga bosing._")

    text = "\n".join(lines)

    # Inline navigatsiya tugmalari
    markup = InlineKeyboardMarkup()
    nav_row = []

    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"{prefix}:{page-1}"))
    else:
        nav_row.append(InlineKeyboardButton("⏹", callback_data="noop"))

    nav_row.append(InlineKeyboardButton(f"📄 {page+1} / {total_pages}", callback_data="noop"))

    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"{prefix}:{page+1}"))
    else:
        nav_row.append(InlineKeyboardButton("⏹", callback_data="noop"))

    markup.row(*nav_row)
    markup.add(
        InlineKeyboardButton(f"📥 Barchasini .PDF formatda yuklab olish ({total_users} nafar)", callback_data="export_pdf")
    )

    return text, markup

def format_user_card(user: dict) -> str:
    name = user.get("name") or user.get("email", "").split("@")[0]
    email = user.get("email", "Mavjud emas")

    card = (
        f"👤 *F.I.SH:* {name}\n"
        f"📧 *Pochta manzili:* `{email}`\n\n"
        f"👉 _Pochta manzilini nusxalash uchun ustiga bosing: `{email}`_"
    )
    return card

def send_pdf_document(bot: TeleBot, chat_id: int, users: list):
    wait_msg = bot.send_message(
        chat_id,
        "⏳ *PDF hujjat tayyorlanmoqda, kuting...*",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    try:
        pdf_path = generate_employees_pdf(users)
        with open(pdf_path, "rb") as f:
            bot.send_document(
                chat_id,
                f,
                caption=(
                    f"📄 *DKZ AJ mail xodimlar ro'yxati*\n\n"
                    f"👥 Jami: *{len(users)}* nafar xodim\n"
                    f"🌐 Rasmiy domen: `@uz-potash.uz`"
                ),
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
        try:
            bot.delete_message(chat_id, wait_msg.message_id)
        except Exception:
            pass
    except Exception as e:
        logger.error(f"PDF yuborishda xatolik: {e}")
        bot.edit_message_text(
            f"❌ PDF hujjat yaratishda xatolik yuz berdi: {str(e)}",
            chat_id=chat_id,
            message_id=wait_msg.message_id
        )


def register_handlers(bot: TeleBot, data_manager: DataManager):

    # Telegram komandalar menyusi
    try:
        bot.set_my_commands([
            BotCommand("list", "📋 Xodimlar ro'yxati (10 tadan)"),
            BotCommand("pdf", "📥 Ro'yxatni PDF yuklab olish"),
            BotCommand("search", "🔍 Xodim qidirish"),
            BotCommand("start", "🔄 Asosiy menyuni ko'rsatish"),
            BotCommand("help", "ℹ️ Yordam")
        ])
    except Exception as e:
        logger.warning(f"set_my_commands xatosi: {e}")

    # /start
    @bot.message_handler(commands=['start'])
    def cmd_start(message: Message):
        users_count = len(data_manager.get_users())
        text = (
            "👋 *Assalomu alaykum!*\n\n"
            "Bu *DKZ AJ* korporativ pochta xodimlari ma'lumotnoma boti.\n\n"
            f"📊 Tizimda jami: *{users_count}* nafar xodim pochtasi mavjud.\n\n"
            "📋 *Xodimlar ro'yxati:* 10 tadan sahifalangan holda xodimlar nomi va pochtasini ko'rish.\n"
            "🔍 *Tezkor qidiruv:* Xodim ismini lotin yoki krill, katta yoki kichik harflarda yozib yuboring.\n"
            "_Misol: `Javohir`, `жавоҳир ҳожибаев`, `Zaripov`..._\n\n"
            "Quyidagi menyu tugmalaridan birini tanlang 👇"
        )
        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

    # /help va Yordam tugmasi
    @bot.message_handler(commands=['help'])
    @bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
    def cmd_help(message: Message):
        text = (
            "📖 *QO'LLANMA VA IMKONIYATLAR*\n\n"
            "🔹 *Xodimlar ro'yxati:* '📋 Xodimlar ro'yxati' yoki /list — xodimlarni 10 tadan sahifalab ko'rish.\n"
            "🔹 *PDF Export:* '📥 PDF yuklab olish' yoki /pdf — 'DKZ AJ mail xodimlar ro'yxati' sarlavhali rasmiy PDF hujjat.\n"
            "🔹 *Qidirish:* Xodim ismini to'g'ridan-to'g'ri yozing. Lotin va Krill yozuvlariga to'liq moslashgan (`Javohir` = `Жавоҳир` = `Жавохир`).\n\n"
            "🌐 *Rasmiy domen:* `@uz-potash.uz`"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())

    # 📋 XODIMLAR RO'YXATI — 10 ta qatordan iborat pagination
    @bot.message_handler(commands=['list'])
    @bot.message_handler(func=lambda m: m.text == "📋 Xodimlar ro'yxati")
    def cmd_list(message: Message):
        users = data_manager.get_users()
        if not users:
            bot.send_message(
                message.chat.id,
                "⚠️ Hozircha xodimlar ma'lumotlari topilmadi.",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
            return

        text, markup = build_pagination_text_and_markup(users, page=0, prefix="pg")
        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=markup
        )

    # 📥 PDF YUKLAB OLISH
    @bot.message_handler(commands=['pdf'])
    @bot.message_handler(func=lambda m: m.text == "📥 PDF yuklab olish")
    def cmd_pdf(message: Message):
        users = data_manager.get_users()
        if not users:
            bot.send_message(message.chat.id, "⚠️ Xodimlar ma'lumotlari topilmadi.", reply_markup=get_main_keyboard())
            return
        send_pdf_document(bot, message.chat.id, users)

    # 🔍 Qidirish prompti
    @bot.message_handler(commands=['search'])
    @bot.message_handler(func=lambda m: m.text == "🔍 Qidirish")
    def btn_search_prompt(message: Message):
        bot.send_message(
            message.chat.id,
            "🔍 Qidirmoqchi bo'lgan xodimning ismini yozing:\n"
            "_(Lotin yoki Krill, katta yoki kichik harflarda yozishingiz mumkin)_\n\n"
            "Misol: `Javohir`, `жавоҳир ҳожибаев`, `Zaripov`, `Бадалов`...",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

    # Callback handler (Pagination & PDF)
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callbacks(call: CallbackQuery):
        data = call.data

        if data == "noop":
            bot.answer_callback_query(call.id)
            return

        # PDF yuklab olish
        if data == "export_pdf":
            bot.answer_callback_query(call.id, "PDF tayyorlanmoqda...")
            users = data_manager.get_users()
            send_pdf_document(bot, call.message.chat.id, users)
            return

        # 10 qatordan iborat pagination: pg:<page>
        if data.startswith("pg:"):
            page = int(data.split(":")[1])
            users = data_manager.get_users()
            text, markup = build_pagination_text_and_markup(users, page=page, prefix="pg")
            try:
                bot.edit_message_text(
                    text,
                    chat_id=call.message.chat.id,
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
        query = message.text.strip()
        if not query or query.startswith("/"):
            return

        users = data_manager.get_users(search=query)

        if not users:
            bot.send_message(
                message.chat.id,
                f"🔍 *\"{query}\"* bo'yicha hech qanday xodim topilmadi.\n\n"
                f"💡 Ismni boshqacha yozib ko'ring yoki barcha xodimlarni ko'ring: /list",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
            return

        if len(users) == 1:
            user = users[0]
            text = (
                f"✅ *Xodim topildi:*\n\n" +
                format_user_card(user)
            )
            bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())
        else:
            lines = [f"🔍 *\"{query}\"* bo'yicha {len(users)} ta xodim topildi:\n"]
            for idx, u in enumerate(users[:10], start=1):
                name = u.get("name") or u.get("email", "").split("@")[0]
                email = u.get("email", "")
                lines.append(f"*{idx}.* 👤 *{name}*\n     📧 `{email}`\n")

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(f"📥 Natijalarni .PDF yuklab olish", callback_data="export_pdf")
            )

            bot.send_message(
                message.chat.id,
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=markup
            )
