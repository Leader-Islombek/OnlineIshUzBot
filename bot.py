import json
import re
import time
from datetime import datetime
import asyncio

import aiohttp
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

SENT_JOBS_FILE = "sent_jobs.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def load_sent_jobs():
    try:
        with open(SENT_JOBS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_sent_jobs(job_ids):
    with open(SENT_JOBS_FILE, "w") as f:
        json.dump(job_ids, f)

async def fetch_jobs():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.freelancer.com/jobs", headers=headers) as resp:
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    job_cards = soup.select("div.JobSearchCard-item")[:20]
    for card in job_cards:
        title = card.select_one("a.JobSearchCard-primary-heading-link")
        description = card.select_one("p.JobSearchCard-primary-description")
        link = "https://www.freelancer.com" + title.get("href") if title else ""
        price_block = card.select_one("div.JobSearchCard-secondary-price")
        price_text = price_block.text.strip() if price_block else "Noma'lum"
        job_id_match = re.search(r"/(\d+)", link)
        job_id = job_id_match.group(1) if job_id_match else str(time.time())

        jobs.append({
            "id": job_id,
            "title": title.text.strip() if title else "No title",
            "description": description.text.strip() if description else "",
            "price": price_text,
            "link": link
        })
    return jobs

def convert_price_to_som(price_text):
    match = re.search(r"\$([\d,.]+)", price_text)
    if match:
        usd = float(match.group(1).replace(",", ""))
        som = round(usd * 12500)
        return f"{price_text} (~{som:,} so'm)"
    return price_text

async def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target='uz').translate(text)
    except:
        return text

async def send_job_summary(context: ContextTypes.DEFAULT_TYPE):
    sent_ids = load_sent_jobs()
    jobs = await fetch_jobs()
    new_jobs = [job for job in jobs if job["id"] not in sent_ids][:15]

    for job in new_jobs:
        translated_title = await translate_text(job["title"])
        translated_desc = await translate_text(job["description"])
        price = convert_price_to_som(job["price"])

        message = f"""🛠️ Yangi ish e’loni: {translated_title}
💬 Tavsif: {translated_desc}
💰 Narxi: {price}
🔗 Link: {job['link']}"""

        await context.bot.send_message(chat_id=CHANNEL_ID, text=message)
        sent_ids.append(job["id"])

    save_sent_jobs(sent_ids)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("🤖 Bot ishga tushdi!")
    await send_job_summary(context)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"✅ Ishlayapti! ({now})")

async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("🕵️ Yangi ishlar yuborilyapti...")
    await send_job_summary(context)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("summary", summary_command))

    # Bot ishga tushganda darhol yuboradi
    app.job_queue.run_once(send_job_summary, 10)

    # Har 6 soatda (kuniga 4 marta) yuboradi
    app.job_queue.run_repeating(send_job_summary, interval=6 * 60 * 60, first=6 * 60 * 60)

    print("🤖 Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()