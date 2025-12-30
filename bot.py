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

# ================== DAILY RESET COUNT (GIỮ USERS) ==================
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

# ================== /START (CHỈ HIỂN THỊ) ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    # 🔄 RESET COUNT KHI QUA NGÀY MỚI (KHÔNG TÍNH ADMIN)
    check_daily_reset(data)

    text = (
        "🔥🔥 WINBOOK – LÀM NHIỆM VỤ NHẬN 48K TIỀN THẬT 🔥🔥\n\n"
        "📅 THỜI GIAN SỰ KIỆN: 01/01 – 05/01/2026\n\n"
        "🎁 KHUYẾN MÃI HÔM NAY DÀNH CHO 100 NGƯỜI\n"
        f"👥 ĐÃ NHẬN: {data['count']}/{TOTAL_SLOTS}\n\n"
        "📣 YÊU CẦU THAM GIA:\n"
        "1️⃣ THAM GIA KÊNH WINBOOK\n"
        "2️⃣ FOLLOW TIKTOK WINBOOK\n"
        "3️⃣ LIKE FANPAGE + CHIA SẺ 01 HỘI NHÓM\n"
        "   • CHIA SẺ TRANG CÁ NHÂN\n"
        "   • TAG 03 BẠN BÈ (CÓ TRÊN 200 BẠN BÈ)\n"
        "4️⃣ ĐĂNG KÝ 01 TÀI KHOẢN GAME (NẾU CHƯA CÓ)\n\n"
        "📸 SAU KHI HOÀN THÀNH → GỬI ẢNH CHO CSKH\n\n"
        "👇 BẤM ĐỦ CÁC NÚT, SAU ĐÓ XÁC NHẬN"
    )

    keyboard = [
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
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

# ================== /KM (ĐẾM SLOT THEO NGÀY – ADMIN KHÔNG TÍNH) ==================
async def km(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = load_data()

    # 🔄 AUTO RESET COUNT KHI QUA NGÀY MỚI
    check_daily_reset(data)

    # ADMIN TEST → KHÔNG TÍNH
    if uid == ADMIN_ID:
        await start(update, context)
        return

    # NGƯỜI CŨ → KHÔNG NHẬN LẠI
    if uid in data["users"]:
        await update.message.reply_text(
            "⚠️ Bạn đã bấm nhận rồi.\n👉 Mỗi Telegram chỉ được nhận 1 lần."
        )
        return

    # HẾT SLOT TRONG NGÀY
    if data["count"] >= TOTAL_SLOTS:
        await update.message.reply_text(
            "❌ Khuyến mãi hôm nay đã đủ 100 người.\n👉 Hẹn bạn quay lại ngày mai nhé ❤️"
        )
        return

    # NGƯỜI MỚI TRONG NGÀY
    data["count"] += 1
    data["users"].append(uid)
    save_data(data)

    await start(update, context)

# ================== CALLBACK ==================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        user = query.from_user

        mention = (
            f"@{user.username}"
            if user.username
            else f"<a href='tg://user?id={user.id}'>{user.full_name}</a>"
        )

        if not await is_channel_member(context, user.id):
            await query.message.reply_text(
                f"❗ {mention} chưa tham gia kênh Winbook.\n"
                "👉 Vui lòng tham gia kênh trước khi xác nhận.",
                parse_mode="HTML"
            )
            return

        await query.message.reply_text(
            f"✅ {mention} đã hoàn thành nhiệm vụ.\n\n"
            "📸 Vui lòng gửi hình ảnh xác minh (like Facebook + follow TikTok) cho CSKH để được duyệt & nhận CODE.",
            parse_mode="HTML"
        )

# ================== RESET (THỦ CÔNG – GIỮ USERS) ==================
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    data = load_data()
    data["count"] = 0
    data["last_reset"] = datetime.now().strftime("%Y-%m-%d")
    save_data(data)
    await update.message.reply_text("🔄 Đã reset lượt hôm nay (không xóa người cũ).")

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
