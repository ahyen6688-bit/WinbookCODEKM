import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import BOT_TOKEN, TOTAL_SLOTS, ADMIN_ID

DATA_FILE = "data.json"

# ================== DATA ==================
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================== STEP TRACKING ==================
user_steps = {}  # {user_id: {"tg": False, "fb": False, "tt": False}}

def get_steps(user_id):
    if user_id not in user_steps:
        user_steps[user_id] = {"tg": False, "fb": False, "tt": False}
    return user_steps[user_id]

# ================== /START & /KM ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = load_data()

    # ĐÃ NHẬN RỒI
    if uid in data["users"]:
        await update.message.reply_text(
            "⚠️ Bạn đã bấm nhận rồi.\n"
            "👉 Mỗi Telegram chỉ được nhận 1 lần."
        )
        return

    # HẾT SLOT
    if data["count"] >= TOTAL_SLOTS:
        await update.message.reply_text(
            "❌ Khuyến mãi đã đủ 100 người.\n"
            "👉 Hẹn bạn quay lại ngày mai nhé ❤️"
        )
        return

    # LẦN ĐẦU → TĂNG SỐ
    data["count"] += 1
    data["users"].append(uid)
    save_data(data)

    text = (
        "🔥🔥 WINBOOK – LÀM NHIỆM VỤ NHẬN 48K TIỀN THẬT 🔥🔥\n\n"
        "🎁 KHUYẾN MÃI HÔM NAY DÀNH CHO 100 NGƯỜI\n"
        f"👥 ĐÃ NHẬN: {data['count']}/{TOTAL_SLOTS}\n\n"
        "📣 YÊU CẦU THAM GIA:\n"
        "1️⃣ Tham gia kênh Telegram\n"
        "2️⃣ Like fanpage Facebook\n"
        "3️⃣ Follow TikTok\n\n"
        "📸 Hoàn thành xong gửi ảnh cho CSKH\n"
        "👇 Bấm đủ các nút rồi xác nhận"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("1️⃣📢 THAM GIA KÊNH", url="https://t.me/winbookEvent")],
        [
            InlineKeyboardButton("2️⃣👍 LIKE FANPAGE", url="https://facebook.com/tenfanpage"),
            InlineKeyboardButton("3️⃣🎵 FOLLOW TIKTOK", url="https://www.tiktok.com/@tentiktok")
        ],
        [
            InlineKeyboardButton("👩‍💼 TELE CS001", url="https://t.me/WinbookCSKH001"),
            InlineKeyboardButton("👨‍💼 TELE CS002", url="https://t.me/WinbookCSKH002")
        ],
        [InlineKeyboardButton("✅ XÁC NHẬN KHUYẾN MÃI", callback_data="confirm")]
    ])

    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# ================== CALLBACK ==================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    steps = get_steps(uid)

    if query.data == "confirm":
        if not all(steps.values()):
            await query.message.reply_text(
                "❗ Bạn CHƯA hoàn thành đủ nhiệm vụ.\n"
                "👉 Vui lòng hoàn thành đủ nhiệm vụ phía trên."
            )
            return

        await query.message.reply_text(
            "✅ Đã ghi nhận xác nhận của bạn.\n\n"
            "📸 Vui lòng gửi ảnh xác minh cho CSKH để được duyệt & nhận CODE."
        )

# ================== RESET ==================
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    save_data({"count": 0, "users": []})
    await update.message.reply_text("🔄 Đã reset khuyến mãi.")

# ================== MAIN ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("km", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CallbackQueryHandler(handle_callback))

    app.run_polling()

if __name__ == "__main__":
    main()
