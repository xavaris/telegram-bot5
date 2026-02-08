import os
import asyncio
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
VENDORS_RAW = os.getenv("VENDORS")

WTB_COOLDOWN = int(os.getenv("WTB_COOLDOWN"))
WTS_INTERVAL = int(os.getenv("WTS_INTERVAL"))

GROUP_ID = -1003569725744
TOPIC_WTB = 8
TOPIC_WTS = 7

VERIFY_LINK = "https://t.me/BotDoWeryfikacjiBot?start=verify"

# ================== LOAD VENDORS ==================
def load_vendors():
    vendors = {}
    for pair in VENDORS_RAW.split(","):
        name, username = pair.split(":")
        vendors[name.strip()] = username.strip()
    return vendors

VENDORS = load_vendors()

# ================== KEYBOARD ==================
def build_keyboard():
    rows = []
    row = []

    for name, username in VENDORS.items():
        row.append(
            InlineKeyboardButton(f"✉️ {name}", url=f"https://t.me/{username}")
        )
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    rows.append([
        InlineKeyboardButton("✅ Zweryfikuj się", url=VERIFY_LINK)
    ])

    return InlineKeyboardMarkup(rows)

# ================== MESSAGE ==================
MESSAGE_TEXT = """
🛡️🔥 T¥LKØ L€G¡TN€ Z@KUP¥ 🔥🛡️

Kupuj tylko u sprawdzonych vendorów z listy poniżej.
Nie odpowiadamy za transakcje poza nimi.

👇 Wybierz vendora lub zweryfikuj się:
"""

# ================== MEMORY ==================
last_wtb_time = 0
last_wtb_msg_id = None
last_wts_msg_id = None

# ================== WTS LOOP ==================
async def wts_loop(app):
    global last_wts_msg_id

    while True:
        msg = await app.bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_WTS,
            text=MESSAGE_TEXT,
            reply_markup=build_keyboard()
        )

        if last_wts_msg_id:
            try:
                await app.bot.delete_message(
                    chat_id=GROUP_ID,
                    message_id=last_wts_msg_id
                )
            except:
                pass

        last_wts_msg_id = msg.message_id
        await asyncio.sleep(WTS_INTERVAL)

# ================== GROUP LISTENER ==================
async def group_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_wtb_time, last_wtb_msg_id

    if not update.message or not update.message.is_topic_message:
        return

    if update.message.message_thread_id != TOPIC_WTB:
        return

    now = time.time()
    if now - last_wtb_time < WTB_COOLDOWN:
        return

    msg = await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=TOPIC_WTB,
        text=MESSAGE_TEXT,
        reply_markup=build_keyboard()
    )

    if last_wtb_msg_id:
        try:
            await context.bot.delete_message(
                chat_id=GROUP_ID,
                message_id=last_wtb_msg_id
            )
        except:
            pass

    last_wtb_msg_id = msg.message_id
    last_wtb_time = now

# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_listener)
    )

    asyncio.get_event_loop().create_task(wts_loop(app))

    print("LEGIT VENDOR BOT STARTED")
    app.run_polling()

# ================== RUN ==================
if __name__ == "__main__":
    main()
