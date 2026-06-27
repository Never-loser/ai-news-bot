#!/usr/bin/env python3
"""
ربات تلگرام اخبار هوش مصنوعی
هر روز صبح (۸:۰۰) و شب (۲۰:۰۰) اخبار AI می‌فرسته
"""

import asyncio
import logging
import os
from datetime import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from news_fetcher import fetch_ai_news
from translator import translate_to_persian

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID",   "YOUR_CHAT_ID_HERE")
NEWS_COUNT = 5   # تعداد خبر در هر نوبت


# ─── Helpers ───────────────────────────────────────────────────────────────────
async def send_news(context: ContextTypes.DEFAULT_TYPE, chat_id: str = None):
    """اخبار رو بگیر، ترجمه کن و بفرست"""
    target = chat_id or CHAT_ID
    logger.info(f"📡 Fetching news for chat {target}...")

    await context.bot.send_message(
        chat_id=target,
        text="⏳ در حال دریافت آخرین اخبار هوش مصنوعی..."
    )

    articles = fetch_ai_news(count=NEWS_COUNT)
    if not articles:
        await context.bot.send_message(
            chat_id=target,
            text="❌ متأسفانه در دریافت اخبار مشکلی پیش آمد. لطفاً بعداً دوباره امتحان کنید."
        )
        return

    header = "🤖 *اخبار هوش مصنوعی امروز*\n" + "─" * 30 + "\n\n"
    await context.bot.send_message(chat_id=target, text=header, parse_mode="Markdown")

    for i, article in enumerate(articles, 1):
        title_fa   = translate_to_persian(article["title"])
        summary_fa = translate_to_persian(article["summary"]) if article.get("summary") else ""

        msg = (
            f"📰 *خبر {i}*\n"
            f"*{title_fa}*\n"
        )
        if summary_fa:
            msg += f"\n{summary_fa}\n"
        msg += f"\n🔗 [مطالعه کامل]({article['url']})"
        if article.get("source"):
            msg += f"\n📌 منبع: {article['source']}"

        await context.bot.send_message(
            chat_id=target,
            text=msg,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        await asyncio.sleep(0.5)   # جلوگیری از flood

    footer = "\n✅ *پایان اخبار امروز*\nبرای دریافت اخبار جدید: /news"
    await context.bot.send_message(chat_id=target, text=footer, parse_mode="Markdown")
    logger.info("✅ News sent successfully.")


# ─── Command Handlers ──────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام! من ربات اخبار هوش مصنوعی هستم.\n\n"
        "📅 هر روز *صبح ساعت ۸* و *شب ساعت ۸* آخرین اخبار AI رو برات می‌فرستم.\n\n"
        "دستورات:\n"
        "• /news — دریافت فوری اخبار\n"
        "• /help — راهنما\n"
        "• /status — وضعیت ربات",
        parse_mode="Markdown"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *راهنمای ربات*\n\n"
        "این ربات هر روز دو بار اخبار هوش مصنوعی رو از Google News می‌گیره، "
        "به فارسی ترجمه می‌کنه و برات می‌فرسته.\n\n"
        "⏰ زمان‌بندی:\n"
        "• صبح: ۰۸:۰۰\n"
        "• شب: ۲۰:۰۰\n\n"
        "دستورات:\n"
        "• /news — دریافت فوری اخبار\n"
        "• /status — وضعیت ربات",
        parse_mode="Markdown"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = context.job_queue.jobs()
    job_list = "\n".join([f"• {j.name}" for j in jobs]) or "هیچ جابی فعال نیست"
    await update.message.reply_text(
        f"✅ *ربات فعال است*\n\n"
        f"📋 جاب‌های زمان‌بندی‌شده:\n{job_list}",
        parse_mode="Markdown"
    )


async def news_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /news — ارسال فوری اخبار"""
    chat_id = str(update.effective_chat.id)
    await send_news(context, chat_id=chat_id)


# ─── Scheduled Jobs ────────────────────────────────────────────────────────────
async def morning_news(context: ContextTypes.DEFAULT_TYPE):
    logger.info("🌅 Morning news job triggered")
    await send_news(context)


async def evening_news(context: ContextTypes.DEFAULT_TYPE):
    logger.info("🌙 Evening news job triggered")
    await send_news(context)


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("news",   news_cmd))

    # Scheduled jobs (UTC — ایران UTC+3:30 است)
    # ۸ صبح ایران = ۴:۳۰ UTC   |   ۸ شب ایران = ۱۶:۳۰ UTC
    job_queue = app.job_queue
    job_queue.run_daily(morning_news, time=time(4, 30), name="morning_news")
    job_queue.run_daily(evening_news, time=time(16, 30), name="evening_news")

    logger.info("🚀 Bot started! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
