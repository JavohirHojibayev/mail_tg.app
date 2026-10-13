"""
Ko'p tilli (Multi-language) lokalizatsiya moduli.
Rus (ru) va Ingliz (en) tillari, shuningdek O'zbek (uz) tili qo'llab-quvvatlanadi.
"""

LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

TEXTS = {
    "ru": {
        "select_lang_prompt": (
            "🌐 *Пожалуйста, выберите язык интерфейса:*\n\n"
            "⚠️ _Для продолжения работы со справочником необходимо выбрать язык:_\n"
            "_To continue, please select your language:_"
        ),
        "lang_selected_confirm": "✅ Язык интерфейса успешно установлен: *Русский*",
        "btn_list": "📋 Список сотрудников",
        "btn_search": "🔍 Поиск",
        "btn_pdf": "📥 Скачать PDF",
        "btn_help": "ℹ️ Помощь",
        "btn_lang": "🌐 Язык / Language",
        "start_text": (
            "👋 *Здравствуйте!*\n\n"
            "Это официальный справочный Telegram-бот корпоративной почты *АО «ДКЗ»* (`uz-potash.uz`).\n\n"
            "📊 Всего в системе: *{count}* адресов сотрудников.\n\n"
            "📋 *Список сотрудников:* Просмотр списка по 10 человек с постраничной навигацией.\n"
            "🔍 *Быстрый поиск:* Отправьте имя сотрудника латиницей или кириллицей.\n"
            "_Пример: `Javohir`, `Hojibayev`, `javohir hojibayev`, `жавоҳир ҳожибаев`..._\n\n"
            "Выберите нужный раздел из меню ниже 👇"
        ),
        "help_text": (
            "📖 *СПРАВКА И ПОДДЕРЖКА*\n\n"
            "🔹 *Список сотрудников:* Нажмите «📋 Список сотрудников» или команду /list — постраничный просмотр по 10 записей.\n"
            "🔹 *Экспорт в PDF:* Нажмите «📥 Скачать PDF» или команду /pdf — скачать официальный PDF-документ.\n"
            "🔹 *Поиск:* Напишите имя или фамилию (поддерживаются латиница, кириллица, о/а).\n"
            "🔹 *Смена языка:* Нажмите «🌐 Язык / Language» или команду /lang.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📩 *ОТКРЫТИЕ НОВОЙ КОРПОРАТИВНОЙ ПОЧТЫ:*\n"
            "Для открытия нового почтового ящика или по техническим вопросам обращайтесь к ответственным специалистам:\n\n"
            "1. 👤 *Javohir Hojibayev*\n"
            "   ✈️ Telegram: [@Javohir_Hojibayev](https://t.me/Javohir_Hojibayev)\n"
            "   📞 Телефон: `+998 94 542 41 21`\n\n"
            "2. 👤 *Nurbek Jumayev*\n"
            "   ✈️ Telegram: [@nurbekjumayev](https://t.me/nurbekjumayev)\n"
            "   📞 Телефон: `+998 94 175 86 52`\n\n"
            "🌐 *Официальный почтовый домен:* `@uz-potash.uz`"
        ),
        "search_prompt": (
            "🔍 Введите имя или фамилию сотрудника для поиска:\n"
            "_(Можно писать на латинице или кириллице, строчными или заглавными буквами)_\n\n"
            "Пример: `Javohir`, `Hojibayev`, `javohir hojibayev`, `жавоҳир ҳожибаев`..."
        ),
        "pagination_header": "📋 *СПИСОК СОТРУДНИКОВ АО «ДКЗ»*",
        "pagination_page_info": "📊 _Страница: {page} / {total_pages} (Всего: {total_users} чел.)_\n",
        "pagination_footer": "💡 _Нажмите на адрес электронной почты для копирования._",
        "btn_prev": "⬅️ Назад",
        "btn_next": "Вперед ➡️",
        "btn_export_all_pdf": "📥 Скачать всё в .PDF ({total_users} чел.)",
        "btn_results_pdf": "📥 Скачать результаты в .PDF",
        "user_card": (
            "👤 *Ф.И.О:* {name}\n"
            "📧 *Эл. почта:* `{email}`\n\n"
            "👉 _Нажмите на адрес для копирования: `{email}`_"
        ),
        "search_found_single": "✅ *Сотрудник найден:*\n\n",
        "search_found_multiple": "🔍 По запросу *\"{query}\"* найдено {count} сотрудников:\n\n",
        "search_not_found": (
            "🔍 По запросу *\"{query}\"* сотрудники не найдены.\n\n"
            "💡 Попробуйте ввести имя иначе или посмотрите полный список: /list"
        ),
        "pdf_wait": "⏳ *PDF документ формируется, пожалуйста подождите...*",
        "pdf_caption": (
            "📄 *DKZ AJ mail xodimlar ro'yxati*\n\n"
            "👥 Всего сотрудников: *{count}*\n"
            "🌐 Официальный домен: `@uz-potash.uz`"
        ),
        "contact_javohir": "💬 Javohir Hojibayev (Telegram)",
        "contact_nurbek": "💬 Nurbek Jumayev (Telegram)",
        "cmd_list": "📋 Список сотрудников (по 10 чел.)",
        "cmd_pdf": "📥 Скачать список в PDF",
        "cmd_search": "🔍 Поиск сотрудника",
        "cmd_start": "🔄 Главное меню",
        "cmd_help": "ℹ️ Помощь и контакты",
        "cmd_lang": "🌐 Выбрать язык / Change language",
    },
    "en": {
        "select_lang_prompt": (
            "🌐 *Please select interface language:*\n\n"
            "⚠️ _To continue using the corporate directory, please select your language:_\n"
            "_Для продолжения выберите язык:_"
        ),
        "lang_selected_confirm": "✅ Interface language set to: *English*",
        "btn_list": "📋 Employee List",
        "btn_search": "🔍 Search",
        "btn_pdf": "📥 Download PDF",
        "btn_help": "ℹ️ Help",
        "btn_lang": "🌐 Language / Язык",
        "start_text": (
            "👋 *Welcome!*\n\n"
            "This is the official corporate email directory bot for *JSC \"DKZ\"* (`uz-potash.uz`).\n\n"
            "📊 Total directory entries: *{count}* employee emails.\n\n"
            "📋 *Employee List:* Browse employees paginated by 10 per page.\n"
            "🔍 *Quick Search:* Send employee name in Latin or Cyrillic.\n"
            "_Example: `Javohir`, `Hojibayev`, `javohir hojibayev`, `жавоҳир ҳожибаев`..._\n\n"
            "Please choose an option from the menu below 👇"
        ),
        "help_text": (
            "📖 *HELP & SUPPORT*\n\n"
            "🔹 *Employee Directory:* Click \"📋 Employee List\" or send /list — browse employees 10 per page.\n"
            "🔹 *PDF Export:* Click \"📥 Download PDF\" or send /pdf — download full official PDF document.\n"
            "🔹 *Search:* Type any name or surname (Latin, Cyrillic, and phonetic matches supported).\n"
            "🔹 *Language:* Click \"🌐 Language / Язык\" or send /lang to switch language.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📩 *CREATING A NEW CORPORATE EMAIL:*\n"
            "To request a new corporate email address or for email assistance, please contact the administrators:\n\n"
            "1. 👤 *Javohir Hojibayev*\n"
            "   ✈️ Telegram: [@Javohir_Hojibayev](https://t.me/Javohir_Hojibayev)\n"
            "   📞 Phone: `+998 94 542 41 21`\n\n"
            "2. 👤 *Nurbek Jumayev*\n"
            "   ✈️ Telegram: [@nurbekjumayev](https://t.me/nurbekjumayev)\n"
            "   📞 Phone: `+998 94 175 86 52`\n\n"
            "🌐 *Official domain:* `@uz-potash.uz`"
        ),
        "search_prompt": (
            "🔍 Enter employee name or surname to search:\n"
            "_(You can write in Latin or Cyrillic, lower or uppercase letters)_\n\n"
            "Example: `Javohir`, `Hojibayev`, `javohir hojibayev`, `жавоҳир ҳожибаев`..."
        ),
        "pagination_header": "📋 *JSC \"DKZ\" EMPLOYEE DIRECTORY*",
        "pagination_page_info": "📊 _Page: {page} / {total_pages} (Total: {total_users} employees)_\n",
        "pagination_footer": "💡 _Tap on an email address to copy it._",
        "btn_prev": "⬅️ Prev",
        "btn_next": "Next ➡️",
        "btn_export_all_pdf": "📥 Download all in .PDF ({total_users} emp.)",
        "btn_results_pdf": "📥 Download results in .PDF",
        "user_card": (
            "👤 *Name:* {name}\n"
            "📧 *Corporate Email:* `{email}`\n\n"
            "👉 _Tap to copy email address: `{email}`_"
        ),
        "search_found_single": "✅ *Employee found:*\n\n",
        "search_found_multiple": "🔍 Found {count} employees for *\"{query}\"*:\n\n",
        "search_not_found": (
            "🔍 No employees found for *\"{query}\"*.\n\n"
            "💡 Try typing differently or view full directory: /list"
        ),
        "pdf_wait": "⏳ *Generating PDF document, please wait...*",
        "pdf_caption": (
            "📄 *DKZ AJ mail xodimlar ro'yxati*\n\n"
            "👥 Total employees: *{count}*\n"
            "🌐 Official domain: `@uz-potash.uz`"
        ),
        "contact_javohir": "💬 Javohir Hojibayev (Telegram)",
        "contact_nurbek": "💬 Nurbek Jumayev (Telegram)",
        "cmd_list": "📋 Employee list (10 per page)",
        "cmd_pdf": "📥 Download PDF list",
        "cmd_search": "🔍 Search employee",
        "cmd_start": "🔄 Main menu",
        "cmd_help": "ℹ️ Help and contacts",
        "cmd_lang": "🌐 Select language",
    }
}

def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Belgilangan til bo'yicha matnni qaytaradi (standart 'ru')"""
    if lang not in TEXTS:
        lang = "ru"
    template = TEXTS[lang].get(key, TEXTS["ru"].get(key, ""))
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template
