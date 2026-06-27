# 🤖 ربات تلگرام اخبار هوش مصنوعی

هر روز **صبح ساعت ۸** و **شب ساعت ۸** آخرین اخبار AI رو از Google News می‌گیره، به فارسی ترجمه می‌کنه و می‌فرسته.

---

## ⚙️ راه‌اندازی

### ۱. ساختن ربات تلگرام

1. توی تلگرام به **@BotFather** پیام بده
2. دستور `/newbot` رو بفرست
3. یه اسم و username برای ربات انتخاب کن
4. **BOT TOKEN** رو که بهت می‌ده کپی کن

### ۲. گرفتن Chat ID

1. ربات رو پیدا کن و `/start` بفرست
2. این آدرس رو توی مرورگر باز کن (TOKEN رو جایگزین کن):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
3. دنبال `"chat":{"id":` بگرد — اون عدد **CHAT ID** توئه

### ۳. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### ۴. تنظیم متغیرهای محیطی

**لینوکس/مک:**
```bash
export TELEGRAM_BOT_TOKEN="توکن_ربات_اینجا"
export TELEGRAM_CHAT_ID="چت_آیدی_اینجا"
```

**ویندوز (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN="توکن_ربات_اینجا"
$env:TELEGRAM_CHAT_ID="چت_آیدی_اینجا"
```

**یا مستقیم توی `bot.py` (خط ۱۸-۱۹):**
```python
BOT_TOKEN = "توکن_ربات_اینجا"
CHAT_ID   = "چت_آیدی_اینجا"
```

### ۵. اجرا

```bash
python bot.py
```

---

## 📋 دستورات ربات

| دستور | توضیح |
|-------|-------|
| `/start` | شروع و معرفی ربات |
| `/news` | دریافت فوری اخبار |
| `/status` | وضعیت ربات و جاب‌ها |
| `/help` | راهنما |

---

## 🕐 زمان‌بندی

| نوبت | ساعت ایران | ساعت UTC |
|------|------------|----------|
| صبح | ۰۸:۰۰ | ۰۴:۳۰ |
| شب  | ۲۰:۰۰ | ۱۶:۳۰ |

> برای تغییر ساعت، فایل `bot.py` خط‌های `run_daily` رو ویرایش کن.

---

## 🔄 اجرای دائمی (سرور لینوکس)

**با systemd:**
```bash
# /etc/systemd/system/ainewsbot.service
[Unit]
Description=AI News Telegram Bot
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/ai_news_bot
Environment="TELEGRAM_BOT_TOKEN=..."
Environment="TELEGRAM_CHAT_ID=..."
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable ainewsbot
sudo systemctl start ainewsbot
```

**با screen (ساده‌تر):**
```bash
screen -S aibot
python bot.py
# Ctrl+A D برای detach
```

---

## ⚡ محدودیت‌ها

- **ترجمه**: از MyMemory API رایگان استفاده می‌کنه (روزانه ~۵۰۰۰ کاراکتر). برای استفاده بیشتر، یه ایمیل رو در پارامتر `de` اضافه کن یا از DeepL API بزن.
- **اخبار**: Google News RSS محدودیت rate ندارد.

---

## 📁 ساختار فایل‌ها

```
ai_news_bot/
├── bot.py           # فایل اصلی — هندلرها و scheduler
├── news_fetcher.py  # دریافت اخبار از Google News RSS
├── translator.py    # ترجمه انگلیسی به فارسی
├── requirements.txt # وابستگی‌های پایتون
└── README.md        # این فایل
```
