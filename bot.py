import os
import asyncio
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== VARIABLES ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
VENDORS_RAW = os.getenv("VENDORS")

GROUP_ID = -1003569725744
TOPICS = [7, 8]

ADMIN_VERIFY_ID = 8482440165  # burwusovy

# ================== LOAD VENDORS ==================
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

# ================== KEYBOARD ==================
def build_keyboard():
    buttons = []

    for name, username in VENDORS.items():
        buttons.append([
            InlineKeyboardButton(
                f"✉️ {name}",
                url=f"https://t.me/{username}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "✅ Zweryfikuj się",
            url="https://t.me/BotDoWeryfikacjiBot?start=verify"
        )
    ])

    return InlineKeyboardMarkup(buttons)

# ================== MESSAGE ==================
MESSAGE_TEXT = """
🛡️🔥 T¥LKØ L€G¡TN€ Z@KUP¥ 🔥🛡️

Kupuj tylko u sprawdzonych vendorów z listy poniżej.
Nie odpowiadamy za transakcje poza nimi.

📢 Na ten moment grupa jest BEZPŁATNA
Chcesz zostać vendorem? Kliknij przycisk poniżej.

👇 Wybierz vendora lub zweryfikuj się:
"""

# ================== SEND INFO ==================
async def send_info(bot: Bot):
    keyboard = build_keyboard()

    for topic in TOPICS:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=topic,
            text=MESSAGE_TEXT,
            reply_markup=keyboard
        )

# ================== SCHEDULER ==================
async def scheduler(bot: Bot):
    while True:
        await send_info(bot)
        await asyncio.sleep(60 * 60 * 12)

# ================== START HANDLER ==================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "verify" in text:
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
            "Witaj 👋\n"
            "Jeśli chcesz zostać vendorem, kliknij w grupie przycisk "
            "„Zweryfikuj się”."
        )

# ================== PHOTO HANDLER ==================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_photo"):
        return

    photo = update.message.photo[-1]
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name

    caption = f"📥 NOWA WERYFIKACJA\n👤 {username}"

    await context.bot.send_photo(
        chat_id=ADMIN_VERIFY_ID,
        photo=photo.file_id,
        caption=caption
    )

    await update.message.reply_text("✅ Zgłoszenie wysłane do administracji.")
    context.user_data["awaiting_photo"] = False

# ================== MAIN ==================
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot = app.bot

    app.add_handler(MessageHandler(filters.Regex("^/start"), start_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    asyncio.create_task(scheduler(bot))

    print("LEGIT VENDOR BOT STARTED")
    await app.initialize()
    await app.start()
    await app.idle()

# ================== RUN ==================
if __name__ == "__main__":
    asyncio.run(main())
