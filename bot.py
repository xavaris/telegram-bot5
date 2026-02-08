import os
import asyncio
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
VENDORS_RAW = os.getenv("VENDORS")

TOPIC_7 = int(os.getenv("TOPIC_AUTO"))   # 7
TOPIC_8 = int(os.getenv("TOPIC_WTB"))    # 8

COOLDOWN_7 = int(os.getenv("COOLDOWN_TOPIC_7"))
COOLDOWN_8 = int(os.getenv("COOLDOWN_TOPIC_8"))

GROUP_ID = -1003569725744
ADMIN_VERIFY_ID = 8482440165

VERIFY_LINK = "https://t.me/BotDoWeryfikacjiBot?start=verify"

# ================= LOAD VENDORS =================
def load_vendors():
    vendors = {}
    for pair in VENDORS_RAW.split(","):
        name, username = pair.split(":")
        vendors[name.strip()] = username.strip()
    return vendors

VENDORS = load_vendors()

# ================= KEYBOARD =================
def build_keyboard():
    rows, row = [], []
    for name, username in VENDORS.items():
        row.append(InlineKeyboardButton(f"✉️ {name}", url=f"https://t.me/{username}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([InlineKeyboardButton("✅ Zweryfikuj się", url=VERIFY_LINK)])
    return InlineKeyboardMarkup(rows)

# ================= MESSAGE =================
TEXT = """
🛡️🔥 T¥LKØ L€G¡TN€ Z@KUP¥ 🔥🛡️

Kupuj tylko u sprawdzonych vendorów z listy poniżej.
Nie odpowiadamy za transakcje poza nimi.

👇 Wybierz vendora lub zweryfikuj się:
"""

# ================= MEMORY =================
last7_msg = None
last8_msg = None
last7_time = 0
last8_time = 0

# ================= LOOP =================
async def sender_loop(app):
    global last7_msg, last8_msg, last7_time, last8_time

    await asyncio.sleep(10)

    while True:
        now = time.time()

        if now - last7_time >= COOLDOWN_7:
            if last7_msg:
                try:
                    await app.bot.delete_message(GROUP_ID, last7_msg)
                except:
                    pass

            m7 = await app.bot.send_message(
                chat_id=GROUP_ID,
                message_thread_id=TOPIC_7,
                text=TEXT,
                reply_markup=build_keyboard()
            )
            last7_msg = m7.message_id
            last7_time = now

        if now - last8_time >= COOLDOWN_8:
            if last8_msg:
                try:
                    await app.bot.delete_message(GROUP_ID, last8_msg)
                except:
                    pass

            m8 = await app.bot.send_message(
                chat_id=GROUP_ID,
                message_thread_id=TOPIC_8,
                text=TEXT,
                reply_markup=build_keyboard()
            )
            last8_msg = m8.message_id
            last8_time = now

        await asyncio.sleep(30)

# ================= /START =================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "verify" in update.message.text:
        await update.message.reply_text(
            "🛡️ Weryfikacja vendora\n\n"
            "Wyślij zdjęcie towaru wraz z:\n"
            "➡️ swoim @username\n"
            "➡️ aktualną datą i godziną\n\n"
            "⏱ Do 24h vendor zostanie przyznany."
        )
        context.user_data["awaiting_photo"] = True
    else:
        await update.message.reply_text(
            "Witaj 👋\nKliknij w grupie przycisk „Zweryfikuj się”."
        )

# ================= PHOTO =================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_photo"):
        return

    photo = update.message.photo[-1]
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name

    await context.bot.send_photo(
        chat_id=ADMIN_VERIFY_ID,
        photo=photo.file_id,
        caption=f"📥 NOWA WERYFIKACJA\n👤 {username}"
    )

    await update.message.reply_text("✅ Zgłoszenie wysłane do administracji.")
    context.user_data["awaiting_photo"] = False

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.Regex("^/start"), start_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    asyncio.get_event_loop().create_task(sender_loop(app))

    print("BOT STARTED")
    app.run_polling()

# ================= RUN =================
if __name__ == "__main__":
    main()
