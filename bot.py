import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, TOTAL_SLOTS, ADMIN_ID

DATA_FILE = "data.json"

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    text = (
        "🎁 KHUYẾN MÃI HÔM NAY\n"
        f"👥 Đã nhận: {data['count']}/{TOTAL_SLOTS}\n\n"
        "👇 Bấm nút bên dưới để xác nhận nhận KM"
    )

    keyboard = [[InlineKeyboardButton("✅ XÁC NHẬN NHẬN KM", callback_data="join")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def join_km(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_data()
    user_id = query.from_user.id

    # chặn bấm lại
    if user_id in data["users"]:
        await query.edit_message_text("❗ Bạn đã nhận KM rồi.")
        return

    # hết slot
    if data["count"] >= TOTAL_SLOTS:
        await query.edit_message_text("❌ Hết lượt hôm nay. Hẹn bạn ngày mai nha ❤️")
        return

    # nhận KM
    data["count"] += 1
    data["users"].append(user_id)
    save_data(data)

    await query.edit_message_text(
        f"🎉 NHẬN KM THÀNH CÔNG\n"
        f"👉 Bạn là người thứ #{data['count']}\n"
        f"📩 Vui lòng inbox admin để nhận KM"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    save_data({"count": 0, "users": []})
    await update.message.reply_text("🔄 Đã reset lượt KM hôm nay.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CallbackQueryHandler(join_km))
    app.run_polling()

if __name__ == "__main__":
    main()
