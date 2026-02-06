import os
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
VENDORS_RAW = os.getenv("VENDORS")

TOPIC_AUTO = int(os.getenv("TOPIC_AUTO"))   # 7
TOPIC_WTB = int(os.getenv("TOPIC_WTB"))     # 8

GROUP_ID = -1003569725744
ADMIN_VERIFY_ID = 8482440165

VERIFY_LINK = "https://t.me/BotDoWeryfikacjiBot?start=verify"

# ================= LOAD VENDORS =================
def load_vendors():
    vendors = {}
    if not VENDORS_RAW:
        return vendors
    for pair in VENDORS_RAW.split(","):
        if ":" in pair:
            name, username = pair.split(":", 1)
            vendors[name.strip()] = username.strip()
    return vendors

VENDORS = load_vendors()

# ================= KEYBOARD =================
def build_keyboard():
    buttons = []
    row = []

    for name, username in VENDORS.items():
        row.append(
            InlineKeyboardButton(f"✉️ {name}", url=f"https://t.me/{username}")
        )
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton("✅ Zweryfikuj się", url=VERIFY_LINK)
    ])

    return InlineKeyboardMarkup(buttons)

# ================= MESSAGE =================
MESSAGE_TEXT = """
🛡️🔥 T¥LKØ L€G¡TN€ Z@KUP¥ 🔥🛡️

Kupuj tylko u sprawdzonych vendorów z listy poniżej.
Nie odpowiadamy za transakcje poza nimi.

📢 Na ten moment grupa jest BEZPŁATNA
Chcesz zostać vendorem? Kliknij przycisk poniżej.

👇 Wybierz vendora lub zweryfikuj się:
"""

# ================= AUTO LOOP (topic 7) =================
async def auto_loop(app):
    await asyncio.sleep(10)
    while True:
        await app.bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_AUTO,
            text=MESSAGE_TEXT,
            reply_markup=build_keyboard()
        )
        await asyncio.sleep(60 * 60 * 25)

# ================= GROUP LISTENER =================
async def group_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.is_topic_message:
        return

    if update.message.message_thread_id == TOPIC_WTB:
        await context.bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_WTB,
            text=MESSAGE_TEXT,
            reply_markup=build_keyboard()
        )

# ================= /START =================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "verify" in update.message.text:
        await update.message.reply_text(
            "🛡️ Chcesz się zweryfikować?\n\n"
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

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_listener))
    app.add_handler(MessageHandler(filters.Regex("^/start"), start_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    asyncio.get_event_loop().create_task(auto_loop(app))

    print("LEGIT VENDOR BOT STARTED")
    app.run_polling()

# ================= RUN =================
if __name__ == "__main__":
    main()
