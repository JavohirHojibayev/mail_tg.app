# 🤖 UZ-Potash Korporativ Pochta — Telegram Bot (@dkzmail_bot)

Ushbu Telegram bot **UZ-Potash** korporativ pochtasidagi (`mail.uz-potash.uz` / iRedMail) barcha xodimlarning ism-familiyasi, lavozimi, bo'limi, telefon raqami va elektron pochtasini qidirish va ko'rish uchun mo'ljallangan.

---

## 🌟 Imkoniyatlari

- 👥 **Barcha xodimlar katalogi:** Sahifalab ko'rish (pagination)
- 🔍 **Tezkor qidiruv:** Ism, familiya, lavozim yoki pochta orqali izlash
- 🏢 **Bo'limlar filtri:** Bo'limlar kesimida xodimlarni saralash
- 📋 **Xodim kartasi:** To'liq ma'lumotlar va pochtani 1 bosishda nusxalash
- 🔑 **Ikki xil ulanish mexanizmi:**
  1. **PostgreSQL (`vmail`)**: Server ichida bevosita ulanish
  2. **REST API (`https://mail.uz-potash.uz/api`)**: Korporativ login orqali
- ⚡️ **Lokal kesh (Offline Fallback):** Server bilan vaqtincha aloqa uzilganda ham ma'lumotlar saqlanadi

---

## 🚀 Ishga Tushirish (Windows)

1. Ushbu papkaga kiring:
   ```cmd
   cd C:\Users\acer\Desktop\mail_tg.app
   ```

2. `.env` faylida sozlamalarni tekshiring:
   ```env
   BOT_TOKEN=8875078214:AAFJZgddl_Rm5E21SjfUR36FvpZJRvt9lWI
   ```

3. Botni ishga tushiring:
   ```cmd
   run_bot.bat
   ```
   yoki
   ```cmd
   python bot.py
   ```

---

## 🐧 Linux Serverda O'rnatish va Ishga Tushirish

1. Loyihani serverga nusxalang:
   ```bash
   cd /opt/mail_tg.app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. `.env` faylini sozlang:
   ```env
   BOT_TOKEN=8875078214:AAFJZgddl_Rm5E21SjfUR36FvpZJRvt9lWI
   DB_HOST=127.0.0.1
   DB_USER=vmailadmin
   DB_PASSWORD=YOUR_DB_PASSWORD
   ```

3. Systemd servisi orqali doimiy ishga tushirish:
   ```ini
   # /etc/systemd/system/dkzmail_bot.service
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

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable dkzmail_bot
   sudo systemctl start dkzmail_bot
   ```

---

## 📱 Bot Buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni ishga tushirish va asosiy menyu |
| `/list` | Barcha xodimlar ro'yxati (sahifalar bilan) |
| `/departments` | Kompaniya bo'limlari ro'yxati |
| `/login <email> <parol>` | Korporativ pochta orqali tizimga kirish |
| `/help` | Qo'llanma |
| *Ixtiyoriy matn* | Shunchaki xodim ismini yozsangiz avtomatik qidiradi |
