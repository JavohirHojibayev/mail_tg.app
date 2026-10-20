# 📬 DKZ Mail Telegram Bot

"Dehqonobod Kaliy Zavodi" AJ korporativ pochta foydalanuvchilari ma'lumotnomasi va qidiruv tizimi uchun Telegram boti.

---

## ⚡ Asosiy Imkoniyatlar

- 🔍 **Aqlli Qidiruv** — Xodim F.I.SH, lavozim, pochta, mobil, ofis va ichki raqamlari bo'yicha tezkor qidiruv (Lotin va Kirill alifbolari qo'llab-quvvatlanadi).
- 📄 **PDF Eksport** — Xodimlar ma'lumotnomasi va qidiruv natijalarini rasmiy PDF jadval shaklida yuklab olish.
- 🌐 **Ko'p Tilli Interfeys** — O'zbek va Rus tillari (`UZ` / `RU`).
- 🔄 **Avtomatik Sinxronizatsiya** — Server bazasi (PostgreSQL / vmail) bilan real vaqtda fonda yangilanish va kesh tizimi.
- 📱 **Tezkor Aloqa** — Telefon raqamlar ustiga bosganda avtomatik terish (dialer) va pochtani bir bosishda nusxalash.

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Bog'liqliklarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. Muhit parametrlarini sozlash
`.env.example` namunasidan `.env` faylini yarating va kerakli konfiguratsiya parametrlarini kiriting:
```bash
cp .env.example .env
```

### 3. Botni ishga tushirish
```bash
python bot.py
```

---

## 📌 Asosiy Buyruqlar

| Buyruq | Tavsif |
|---|---|
| `/start` | Botni ishga tushirish va tilni tanlash |
| `/list` | Xodimlar ro'yxatini sahifalab ko'rish |
| `/search` | F.I.SH, pochta yoki raqamlar bo'yicha qidiruv |
| `/pdf` | To'liq ma'lumotnomani PDF formatida yuklab olish |
| `/lang` | Interfeys tilini o'zgartirish |
| `/help` | Qo'llanma va yordam |
