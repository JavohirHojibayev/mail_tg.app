# 🤖 UZ-Potash Korporativ Pochta — Telegram Bot

Ushbu Telegram bot **UZ-Potash (Dehqonobod Kaliy Zavodi)** korporativ pochtasidagi barcha xodimlarning ismi va elektron pochta manzillarini qidirish, ko'rish hamda rasmiy **PDF** formatda eksport qilish uchun mo'ljallangan.

---

## 🌟 Asosiy Imkoniyatlar

- 👥 **120+ Xodimlar Katalogi:** Barcha korporativ pochta foydalanuvchilarining to'liq ro'yxati.
- 🔍 **Universal Qidiruv:** Katta-kichik harflar, Lotin va Krill yozuvlariga to'liq moslashgan (`Javohir` = `Жавоҳир` = `Жавохир`).
- 📄 **PDF Eksport:** Barcha xodimlarning nomi va pochtasi jamlangan rasmiy PDF ma'lumotnoma generatsiya qilish.
- 📱 **Doimiy Menyu:** Telegramning doimiy `[Menu]` tugmasi va qulay boshqaruv klaviaturasi.
- 🔒 **Xavfsiz Arxitektura:** Parollar va maxfiy kalitlar GitHub'ga chiqmaydi (`.gitignore` himoyasi).

---

## 📁 Loyiha Strukturasi

```
mail_tg.app/
├── 📄 bot.py                  # Botni ishga tushiruvchi asosiy fayl
├── ⚙️ config.py               # Konfiguratsiya (muhit o'zgaruvchilarini yuklash)
├── 🔐 .env.example            # Muhit sozlamalari namunasi (GitHub uchun xavfsiz)
├── 🚫 .gitignore              # Maxfiy va keraksiz fayllarni cheklash
├── 📦 requirements.txt        # Python bog'liqliklari
├── 🚀 run_bot.bat             # Windows uchun 1-bosishda ishga tushiruvchi
├── 🐧 run_bot.sh              # Linux server uchun ishga tushiruvchi skript
├── 📋 users_cache.json        # Xodimlar ma'lumotlari kesh bazasi
├── 📁 handlers/
│   ├── __init__.py
│   └── bot_handlers.py        # Telegram komandalari va interaktiv menyu
├── 📁 services/
│   ├── __init__.py
│   ├── data_manager.py        # Xodimlar ma'lumotlarini boshqarish va qidiruv
│   └── db_service.py          # PostgreSQL (vmail) bilan aloqa
├── 📁 utils/
│   ├── translit.py            # Lotin <-> Krill universal qidiruv
│   └── pdf_generator.py       # Rasmiy 3-ustunli PDF hujjat generatsiyasi
└── 📁 generated_docs/         # Generatsiya qilingan PDF fayllar papkasi
```

---

## 🚀 Ishga Tushirish (Windows)

1. **Repozitoriyani yuklab oling yoki oching:**
   ```cmd
   cd C:\Users\acer\Desktop\mail_tg.app
   ```

2. **Sozlamalarni kiritish:**
   `.env.example` faylidan nusxa olib `.env` yarating va parollarni kiriting:
   ```cmd
   copy .env.example .env
   ```

3. **Kutubxonalarni o'rnatish:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Botni ishga tushirish:**
   [run_bot.bat](file:///c:/Users/acer/Desktop/mail_tg.app/run_bot.bat) ni ishga tushiring yoki:
   ```cmd
   python bot.py
   ```

---

## 🐧 Linux Serverda O'rnatish (Ubuntu / Debian)

1. **Loyiha papkasiga o'ting:**
   ```bash
   cd /opt/mail_tg.app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   nano .env
   ```

2. **Systemd orqali 24/7 rejimda xizmat sifatida ishga tushirish:**
   ```ini
   # /etc/systemd/system/mail_tg_bot.service
   [Unit]
   Description=UZ-Potash Telegram Mail Bot
   After=network.target postgresql.service

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/opt/mail_tg.app
   ExecStart=/opt/mail_tg.app/venv/bin/python bot.py
   Restart=always
   RestartSec=5
   EnvironmentFile=/opt/mail_tg.app/.env

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable mail_tg_bot
   sudo systemctl start mail_tg_bot
   ```

---

## 📱 Bot Buyruqlari

| Buyruq | Tavsif |
|---|---|
| `/start` | Botni ishga tushirish va asosiy menyuni chiqarish |
| `/list` | Barcha xodimlar va ularning pochtalari ro'yxati |
| `/pdf` | Xodimlar ro'yxatini toza PDF formatda yuklab olish |
| `/search` | Qidiruv bo'limi |
| `/help` | Qo'llanma |
| *Ixtiyoriy matn* | Xodim ismini yozsangiz avtomatik topib beradi |

---

## 🔐 Xavfsizlik

- Barcha maxfiy kalitlar, parollar va tokenlar faqat **`.env`** faylida saqlanadi.
- `.env` fayli **`.gitignore`** orqali GitHub'ga chiqishdan 100% himoyalangan.
- GitHub'ga faqat xavfsiz **`.env.example`** namunasi yuklanadi.
