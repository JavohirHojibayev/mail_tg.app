import logging
import math
from telebot import TeleBot
from telebot.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from services.data_manager import DataManager
import config

logger = logging.getLogger(__name__)

# Asosiy klaviatura
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("📋 Xodimlar ro'yxati"),
        KeyboardButton("🔍 Qidirish")
    )
    keyboard.add(
        KeyboardButton("🏢 Bo'limlar"),
        KeyboardButton("🔑 Kirish (/login)")
    )
    keyboard.add(KeyboardButton("ℹ️ Yordam"))
    return keyboard

# Xodimlar sahifasi uchun Inline klaviatura
def build_users_page_keyboard(users: list, page: int, total_pages: int, prefix: str = "usrpage"):
    markup = InlineKeyboardMarkup(row_width=1)
    
    start_idx = page * config.PAGE_SIZE
    end_idx = min(start_idx + config.PAGE_SIZE, len(users))
    current_batch = users[start_idx:end_idx]

    for user in current_batch:
        name = user.get("name") or user.get("email", "").split("@")[0]
        email = user.get("email", "")
        dept = user.get("department", "")
        btn_text = f"👤 {name} - 📧 {email}"
        if dept:
            btn_text = f"👤 {name} ({dept})"
        markup.add(InlineKeyboardButton(text=btn_text, callback_data=f"user:{email}"))

    # Sahifalash tugmalari
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"{prefix}:{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{max(1, total_pages)}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"{prefix}:{page+1}"))

    if nav_buttons:
        markup.row(*nav_buttons)

    return markup

def format_user_card(user: dict) -> str:
    name = user.get("name") or user.get("email", "").split("@")[0]
    email = user.get("email", "Mavjud emas")
    position = user.get("position") or "Ko'rsatilmagan"
    dept = user.get("department") or "Ko'rsatilmagan"
    phone = user.get("phone") or "Ko'rsatilmagan"
    is_online = user.get("is_online", False)
    status_str = "🟢 Online" if is_online else "⚪️ Offline"

    card = (
        f"📋 *XODIM KARTASI*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *F.I.SH:* {name}\n"
        f"📧 *Pochta:* `{email}`\n"
        f"💼 *Lavozim:* {position}\n"
        f"🏢 *Bo'lim:* {dept}\n"
        f"📞 *Telefon:* `{phone}`\n"
        f"📶 *Holati:* {status_str}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💡 _Pochta manzilini nusxalash uchun ustiga bosing_"
    )
    return card


def register_handlers(bot: TeleBot, data_manager: DataManager):

    # /start
    @bot.message_handler(commands=['start'])
    def cmd_start(message: Message):
        text = (
            "👋 *Assalomu alaykum!*\n\n"
            "Bu *UZ-Potash* korporativ pochta xodimlari ma'lumotnoma boti.\n\n"
            "Ushbu bot orqali korporativ pochtadagi xodimlarning ism-familiyasi, "
            "pochta manzili, bo'limi va lavozimini oson topishingiz mumkin.\n\n"
            "Quyidagi tugmalardan birini tanlang yoki to'g'ridan-to'g'ri xodim ismini yozing 👇"
        )
        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

    # /help
    @bot.message_handler(commands=['help'])
    @bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
    def cmd_help(message: Message):
        text = (
            "📖 *BOTDAN FOYDALANISH BO'YICHA QO'LLANMA*\n\n"
            "🔹 *Xodimlar ro'yxati:* /list yoki '📋 Xodimlar ro'yxati' tugmasi\n"
            "🔹 *Tezkor qidiruv:* Shunchaki xodim ismi, familiyasi yoki pochtasini xabar qilib yuboring\n"
            "🔹 *Bo'limlar:* /departments yoki '🏢 Bo'limlar'\n"
            "🔹 *Tizimga kirish:* /login <email> <parol>\n"
            "   _Misol: `/login ali@uz-potash.uz 12345`_\n\n"
            "🌐 *Korporativ server:* `https://mail.uz-potash.uz`\n"
            "📧 *Domen:* `@uz-potash.uz`"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    # /list va tugma
    @bot.message_handler(commands=['list'])
    @bot.message_handler(func=lambda m: m.text == "📋 Xodimlar ro'yxati")
    def cmd_list(message: Message):
        users = data_manager.get_users()
        if not users:
            bot.send_message(
                message.chat.id,
                "⚠️ Hozircha xodimlar ma'lumotlari yuklanmadi.\n\n"
                "Iltimos, avval `/login email parol` buyrug'i orqali korporativ akkaunt bilan kiring "
                "yoki server ulanishini tekshiring.",
                parse_mode="Markdown"
            )
            return

        total_pages = math.ceil(len(users) / config.PAGE_SIZE)
        markup = build_users_page_keyboard(users, 0, total_pages, prefix="usrpage")
        bot.send_message(
            message.chat.id,
            f"👥 *Barcha xodimlar ro'yxati* (Jami: {len(users)} nafar):\n"
            f"Batafsil ma'lumot ko'rish uchun xodim ustiga bosing 👇",
            parse_mode="Markdown",
            reply_markup=markup
        )

    # /departments va tugma
    @bot.message_handler(commands=['departments'])
    @bot.message_handler(func=lambda m: m.text == "🏢 Bo'limlar")
    def cmd_departments(message: Message):
        departments = data_manager.get_departments()
        if not departments:
            bot.send_message(
                message.chat.id,
                "⚠️ Bo'limlar ro'yxati topilmadi. Avval `/login` qiling.",
                parse_mode="Markdown"
            )
            return

        markup = InlineKeyboardMarkup(row_width=1)
        for dept in departments:
            markup.add(InlineKeyboardButton(text=f"🏢 {dept}", callback_data=f"dept:{dept}"))

        bot.send_message(
            message.chat.id,
            "🏢 *Kompaniya bo'limlari:*\nKerakli bo'limdagi xodimlarni ko'rish uchun tanlang 👇",
            parse_mode="Markdown",
            reply_markup=markup
        )

    # Qidirish tugmasi
    @bot.message_handler(func=lambda m: m.text == "🔍 Qidirish")
    def btn_search_prompt(message: Message):
        bot.send_message(
            message.chat.id,
            "🔍 Qidirmoqchi bo'lgan xodimning *ism*, *familiya*, *lavozim* yoki *pochta* manzilini yozib yuboring:\n\n"
            "_Misol: Javohir, Buxgalter, admin..._",
            parse_mode="Markdown"
        )

    # /login buyrug'i
    @bot.message_handler(commands=['login'])
    @bot.message_handler(func=lambda m: m.text == "🔑 Kirish (/login)")
    def cmd_login(message: Message):
        parts = message.text.strip().split()
        if len(parts) < 3:
            bot.send_message(
                message.chat.id,
                "🔑 *Korporativ tizimga kirish:*\n\n"
                "Quyidagi formatda yuboring:\n"
                "`/login <email> <parol>`\n\n"
                "Misol:\n"
                "`/login ism@uz-potash.uz MaxfiyParol123`\n\n"
                "⚠️ _Xavfsizlik uchun parolingiz yozilgan xabar avtomatik o'chiriladi._",
                parse_mode="Markdown"
            )
            return

        email = parts[1]
        password = parts[2]

        # Xavfsizlik: foydalanuvchi yozgan parolni chatdan o'chirish
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass

        wait_msg = bot.send_message(message.chat.id, "🔄 Tizimga ulanmoqda, kuting...")

        ok, text = data_manager.authenticate_user(message.chat.id, email, password)
        if ok:
            bot.edit_message_text(
                f"✅ *Muvaffaqiyatli kirdingiz!*\n\n{text}\n"
                f"Endi barcha xodimlar va bo'limlar ma'lumotlarini ko'rishingiz mumkin.",
                chat_id=message.chat.id,
                message_id=wait_msg.message_id,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                f"❌ *Kirishda xatolik:*\n{text}\n\nIltimos, qayta urinib ko'ring.",
                chat_id=message.chat.id,
                message_id=wait_msg.message_id,
                parse_mode="Markdown"
            )

    # Callback query handler
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callbacks(call: CallbackQuery):
        data = call.data

        if data == "noop":
            bot.answer_callback_query(call.id)
            return

        # Sahifalash: usrpage:<page>
        if data.startswith("usrpage:"):
            page = int(data.split(":")[1])
            users = data_manager.get_users()
            total_pages = math.ceil(len(users) / config.PAGE_SIZE)
            markup = build_users_page_keyboard(users, page, total_pages, prefix="usrpage")
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
            except Exception:
                pass
            bot.answer_callback_query(call.id)
            return

        # Bo'lim bo'yicha sahifalash: deptpage:<dept>:<page>
        if data.startswith("deptpage:"):
            parts = data.split(":")
            dept = parts[1]
            page = int(parts[2])
            users = data_manager.get_users(department=dept)
            total_pages = math.ceil(len(users) / config.PAGE_SIZE)
            markup = build_users_page_keyboard(users, page, total_pages, prefix=f"deptpage:{dept}")
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
            except Exception:
                pass
            bot.answer_callback_query(call.id)
            return

        # Bo'lim tanlanganda: dept:<name>
        if data.startswith("dept:"):
            dept = data.split(":", 1)[1]
            users = data_manager.get_users(department=dept)
            if not users:
                bot.answer_callback_query(call.id, f"{dept} bo'limida xodimlar topilmadi.")
                return

            total_pages = math.ceil(len(users) / config.PAGE_SIZE)
            markup = build_users_page_keyboard(users, 0, total_pages, prefix=f"deptpage:{dept}")
            markup.add(InlineKeyboardButton("🔙 Bo'limlar ro'yxatiga", callback_data="back_depts"))

            bot.edit_message_text(
                f"🏢 *{dept}* bo'limi xodimlari ({len(users)} nafar):",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
            return

        # Bo'limlarga qaytish
        if data == "back_depts":
            departments = data_manager.get_departments()
            markup = InlineKeyboardMarkup(row_width=1)
            for d in departments:
                markup.add(InlineKeyboardButton(text=f"🏢 {d}", callback_data=f"dept:{d}"))
            bot.edit_message_text(
                "🏢 *Kompaniya bo'limlari:*\nKerakli bo'limdagi xodimlarni ko'rish uchun tanlang 👇",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
            return

        # Bitta xodim kartasini ko'rish: user:<email>
        if data.startswith("user:"):
            email = data.split(":", 1)[1]
            users = data_manager.get_users(search=email.split("@")[0])
            found = next((u for u in users if u.get("email") == email), None)
            if not found:
                # To'liq ro'yxatdan izlash
                all_u = data_manager.get_users()
                found = next((u for u in all_u if u.get("email") == email), None)

            if found:
                text = format_user_card(found)
                back_markup = InlineKeyboardMarkup()
                back_markup.add(InlineKeyboardButton("🔙 Xodimlar ro'yxatiga", callback_data="back_list"))
                bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="Markdown",
                    reply_markup=back_markup
                )
            else:
                bot.answer_callback_query(call.id, "Xodim ma'lumotlari topilmadi.")
            bot.answer_callback_query(call.id)
            return

        # Ro'yxatga qaytish
        if data == "back_list":
            users = data_manager.get_users()
            total_pages = math.ceil(len(users) / config.PAGE_SIZE)
            markup = build_users_page_keyboard(users, 0, total_pages, prefix="usrpage")
            bot.send_message(
                call.message.chat.id,
                f"👥 *Barcha xodimlar ro'yxati* (Jami: {len(users)} nafar):",
                parse_mode="Markdown",
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
            return

    # Matn orqali avtomatik xodim qidirish
    @bot.message_handler(func=lambda m: True)
    def auto_search(message: Message):
        query = message.text.strip()
        if not query or query.startswith("/"):
            return

        users = data_manager.get_users(search=query)
        if not users:
            bot.send_message(
                message.chat.id,
                f"🔍 *\"{query}\"* bo'yicha hech qanday xodim topilmadi.\n\n"
                f"💡 Qidiruv so'zini to'g'ri yozganingizni tekshiring yoki ro'yxatdan qidiring: /list",
                parse_mode="Markdown"
            )
            return

        if len(users) == 1:
            # Aniq 1 ta xodim topilsa kartasini ko'rsatish
            bot.send_message(
                message.chat.id,
                format_user_card(users[0]),
                parse_mode="Markdown"
            )
        else:
            total_pages = math.ceil(len(users) / config.PAGE_SIZE)
            markup = build_users_page_keyboard(users, 0, total_pages, prefix=f"srchpage:{query}")
            bot.send_message(
                message.chat.id,
                f"🔍 *\"{query}\"* bo'yicha {len(users)} ta natija topildi:\n"
                f"Batafsil ma'lumot uchun xodimni tanlang 👇",
                parse_mode="Markdown",
                reply_markup=markup
            )
