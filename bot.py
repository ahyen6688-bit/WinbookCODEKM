import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, TOTAL_SLOTS, ADMIN_ID, CHANNEL_ID

DATA_FILE = "data.json"

# ================== DATA ==================
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================== DAILY RESET (CHỈ RESET COUNT) ==================
def check_daily_reset(data):
    today = datetime.now().strftime("%Y-%m-%d")
    if data.get("last_reset") != today:
        data["count"] = 0
        data["last_reset"] = today
        save_data(data)

# ================== CHECK JOIN CHANNEL ==================
async def is_channel_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

# ================== /START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    check_daily_reset(data)

    text = (
        "🔥🔥 WINBOOK – LÀM NHIỆM VỤ NHẬN CODE 48K 🔥🔥\n\n"
        "📅 THỜI GIAN: 01/01 – 05/01/2026\n\n"
        "🎁 MỖI NGÀY 100 NGƯỜI\n"
        f"👥 ĐÃ NHẬN: {data['count']}/{TOTAL_SLOTS}\n\n"
        "📌 NHIỆM VỤ BẮT BUỘC:\n"
        "1️⃣ Tham gia kênh Telegram\n"
        "2️⃣ Like Fanpage Facebook\n"
        "3️⃣ Follow TikTok\n\n"
        "📸 Hoàn thành xong, bấm xác nhận và gửi ảnh cho CSKH"
    )

    keyboard = [
        [InlineKeyboardButton("1️⃣📢 THAM GIA KÊNH", url="https://t.me/winbookEvent")],
        [
            InlineKeyboardButton("2️⃣👍 LIKE FACEBOOK", url="https://facebook.com/tenfanpage"),
            InlineKeyboardButton("3️⃣🎵 FOLLOW TIKTOK", url="https://tiktok.com/@tentiktok")
        ],
        [
            InlineKeyboardButton("👩‍💼 CSKH 001", url="https://t.me/WinbookCSKH001"),
            InlineKeyboardButton("👨‍💼 CSKH 002", url="https://t.me/WinbookCSKH002")
        ],
        [InlineKeyboardButton("✅ XÁC NHẬN NHIỆM VỤ", callback_data="confirm")]
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

# ================== /KM ==================
async def km(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = load_data()
    check_daily_reset(data)

    # ADMIN TEST → KHÔNG TÍNH
    if uid == ADMIN_ID:
        await start(update, context)
        return

    # NGƯỜI ĐÃ NHẬN → KHÔNG NHẬN LẠI
    if uid in data["users"]:
        await update.message.reply_text(
            "⚠️ Bạn đã tham gia sự kiện trước đó.\n👉 Mỗi tài khoản chỉ được nhận 1 lần."
        )
        return

    # HẾT SLOT TRONG NGÀY
    if data["count"] >= TOTAL_SLOTS:
        await update.message.reply_text(
            "❌ Hôm nay đã đủ 100 người.\n👉 Vui lòng quay lại vào ngày mai."
        )
        return

    # NGƯỜI MỚI
    data["count"] += 1
    data["users"].append(uid)
    save_data(data)

    await start(update, context)

# ================== CALLBACK CONFIRM ==================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if not await is_channel_member(context, user.id):
        await query.message.reply_text(
            "❗ Bạn CHƯA tham gia kênh Telegram.\n👉 Vui lòng tham gia kênh trước khi xác nhận."
        )
        return

    await query.message.reply_text(
        "✅ Bạn đã bấm xác nhận nhiệm vụ.\n\n"
        "📌 Vui lòng đảm bảo:\n"
        "• Đã tham gia Telegram\n"
        "• Đã like Facebook\n"
        "• Đã follow TikTok\n\n"
        "📸 Gửi hình ảnh xác minh cho CSKH để được duyệt & nhận CODE."
    )

# ================== RESET (ADMIN) ==================
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    data = load_data()
    data["count"] = 0
    data["last_reset"] = datetime.now().strftime("%Y-%m-%d")
    save_data(data)
    await update.message.reply_text("🔄 Đã reset lượt hôm nay.")

# ================== MAIN ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("km", km))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CallbackQueryHandler(handle_callback))

    app.run_polling()

if __name__ == "__main__":
    main()
