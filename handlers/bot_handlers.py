import os
import logging
from telebot import TeleBot
from telebot.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
)
from services.data_manager import DataManager
from utils.pdf_generator import generate_employees_pdf
import config

logger = logging.getLogger(__name__)

# Doimiy ko'rinib turadigan asosiy klaviatura
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
    """Xodimlar ro'yxatini PDF formatda yaratib foydalanuvchiga yuboradi"""
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
                    f"📄 *UZ-Potash Korporativ Pochta Ma'lumotnomasi*\n\n"
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

    # Telegram menyusi uchun doimiy komandalarni o'rnatish
    try:
        bot.set_my_commands([
            BotCommand("list", "📋 Barcha xodimlar va pochtalari"),
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
            "Bu *UZ-Potash* korporativ pochta xodimlari ma'lumotnoma boti.\n\n"
            f"📊 Tizimda jami: *{users_count}* nafar xodim pochtasi mavjud.\n\n"
            "📋 *Xodimlar ro'yxati:* Barcha xodimlarning nomi va pochtalarini to'liq ko'rish hamda PDF formatda yuklab olish.\n"
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
            "🔹 *Xodimlar ro'yxati:* '📋 Xodimlar ro'yxati' yoki /list — barcha 120+ xodimlarning ism-familiyasi va pochtasini chiqaradi.\n"
            "🔹 *PDF Export:* '📥 PDF yuklab olish' yoki /pdf — faqat xodim nomi va pochtasi jamlangan rasmiy PDF faylni beradi.\n"
            "🔹 *Qidirish:* Xodim ismini to'g'ridan-to'g'ri yozing. Katta-kichik, lotin yoki krill yozuvlariga to'liq moslashgan.\n\n"
            "🌐 *Korporativ pochta domeni:* `@uz-potash.uz`"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())

    # 📋 XODIMLAR RO'YXATI — BARCHA 120+ xodimlarni to'liq chiqarish + PDF yuklab olish tugmasi
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

        total_users = len(users)

        # Telegram 4096 belgilik cheklovi uchun xabarlarni bo'lib yuborish (har bir xabarda 45 ta xodim)
        chunk_size = 45
        chunks = [users[i:i + chunk_size] for i in range(0, total_users, chunk_size)]

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(f"📥 Barchasini .PDF formatda yuklab olish ({total_users} nafar)", callback_data="export_pdf")
        )

        for part_idx, chunk in enumerate(chunks, start=1):
            start_num = (part_idx - 1) * chunk_size + 1
            lines = [
                f"📋 *UZ-POTASH XODIMLAR RO'YXATI* (Qism {part_idx}/{len(chunks)})",
                f"📊 _Jami: {total_users} nafar xodim_\n",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ]

            for idx, u in enumerate(chunk, start=start_num):
                name = u.get("name") or u.get("email", "").split("@")[0]
                email = u.get("email", "")
                lines.append(f"*{idx}.* 👤 *{name}*\n     📧 `{email}`\n")

            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            # Oxirgi qismga PDF tugmasini ulash
            if part_idx == len(chunks):
                lines.append("💡 _Pochta manzilini nusxalash uchun ustiga bosing._")
                bot.send_message(
                    message.chat.id,
                    "\n".join(lines),
                    parse_mode="Markdown",
                    reply_markup=markup
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "\n".join(lines),
                    parse_mode="Markdown"
                )

        # Doimiy klaviatura ochiq turishini ta'minlash
        bot.send_message(
            message.chat.id,
            f"✅ Barcha *{total_users}* nafar xodim ro'yxati chiqarildi.\n\n"
            f"📄 PDF fayl olish uchun yuqoridagi tugmani yoki pastdagi **📥 PDF yuklab olish** menyusini bosing 👇",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
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

    # Callback handler
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callbacks(call: CallbackQuery):
        data = call.data

        if data == "export_pdf":
            bot.answer_callback_query(call.id, "PDF tayyorlanmoqda...")
            users = data_manager.get_users()
            send_pdf_document(bot, call.message.chat.id, users)
            return

        if data.startswith("user:"):
            email = data.split(":", 1)[1]
            users = data_manager.get_users()
            found = next((u for u in users if u.get("email", "").lower() == email.lower()), None)

            if found:
                text = format_user_card(found)
                bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())
            else:
                bot.answer_callback_query(call.id, "Xodim ma'lumotlari topilmadi.")
            bot.answer_callback_query(call.id)
            return

    # Foydalanuvchi istalgan matn yozganda avtomatik qidiruv (Lotin, Krill, Katta, Kichik)
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
            for idx, u in enumerate(users[:20], start=1):
                name = u.get("name") or u.get("email", "").split("@")[0]
                email = u.get("email", "")
                lines.append(f"*{idx}.* 👤 *{name}*\n     📧 `{email}`\n")

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(f"📥 Ushbu natijalarni PDF yuklab olish", callback_data="export_pdf")
            )

            bot.send_message(
                message.chat.id,
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=markup
            )
            # Doimiy menyu klaviaturasini ham yuborish
            bot.send_message(
                message.chat.id,
                "👇 Menyudan foydalanishingiz mumkin:",
                reply_markup=get_main_keyboard()
            )
