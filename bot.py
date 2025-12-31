import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import BOT_TOKEN, TOTAL_SLOTS, ADMIN_ID, CHANNEL_ID

DATA_FILE = "data.json"

# ================== CLICK TRACKING ==================
user_steps = {}
# { user_id: {"fb": False, "tt": False} }

def get_steps(uid):
    if uid not in user_steps:
        user_steps[uid] = {"fb": False, "tt": False}
    return user_steps[uid]

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
        "🔥🔥 WINBOOK – LÀM NHIỆM VỤ NHẬN 48K TIỀN THẬT 🔥🔥\n\n"
        "📅 THỜI GIAN SỰ KIỆN: 01/01 – 05/01/2026\n\n"
        "🎁 KHUYẾN MÃI HÔM NAY DÀNH CHO 100 NGƯỜI\n"
        f"👥 ĐÃ NHẬN: {data['count']}/{TOTAL_SLOTS}\n\n"
        "📣 YÊU CẦU THAM GIA:\n"
        "1️⃣ THAM GIA KÊNH WINBOOK\n"
        "2️⃣ FOLLOW TIKTOK WINBOOK\n"
        "3️⃣ LIKE FANPAGE + CHIA SẺ 01 HỘI NHÓM GAME BÀI TRÊN 5000 THÀNH VIÊN\n"
        "   • CHIA SẺ TRANG CÁ NHÂN\n"
        "   • TAG 03 BẠN BÈ (CÓ TRÊN 200 BẠN BÈ)\n"
        "4️⃣ ĐĂNG KÝ 01 TÀI KHOẢN GAME (NẾU CHƯA CÓ)\n\n"
        "📸 SAU KHI HOÀN THÀNH → GỬI ẢNH CHO CSKH\n\n"
        "👇 BẤM ĐỦ CÁC NÚT, SAU ĐÓ XÁC NHẬN"
    )

    keyboard = [
        [InlineKeyboardButton("1️⃣📢 THAM GIA KÊNH", url="https://t.me/winbookEvent")],
        [
            InlineKeyboardButton("2️⃣👍 FACEBOOK", callback_data="fb"),
            InlineKeyboardButton("3️⃣🎵 TIKTOK", callback_data="tt")
        ],
        [InlineKeyboardButton("✅ XÁC NHẬN NHIỆM VỤ", callback_data="confirm")],
        [
            InlineKeyboardButton("👩‍💼 CSKH 001", url="https://t.me/WinbookCSKH001"),
            InlineKeyboardButton("👨‍💼 CSKH 002", url="https://t.me/WinbookCSKH002")
        ]
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

# ================== /KM ==================
async def km(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_type = update.message.chat.type  # private / group / supergroup

    data = load_data()
    check_daily_reset(data)

    # 🚫 ADMIN Ở ĐÂU CŨNG KHÔNG TÍNH
    if uid == ADMIN_ID:
        await start(update, context)
        return

    # ❌ CHAT RIÊNG → CHỈ ĐỂ XEM, KHÔNG TÍNH
    if chat_type == "private":
        await start(update, context)
        return

    # 👉 TỚI ĐÂY = USER THƯỜNG TRONG NHÓM → MỚI TÍNH

    # ❌ ĐÃ NHẬN RỒI
    if uid in data["users"]:
        await update.message.reply_text(
            "⚠️ Bạn đã tham gia sự kiện trước đó.\n👉 Mỗi tài khoản chỉ được nhận 1 lần."
        )
        return

    # ❌ HẾT SLOT
    if data["count"] >= TOTAL_SLOTS:
        await update.message.reply_text(
            "❌ Hôm nay đã đủ 100 người.\n👉 Vui lòng quay lại vào ngày mai."
        )
        return

    # ✅ USER HỢP LỆ TRONG NHÓM
    data["count"] += 1
    data["users"].append(uid)
    save_data(data)

    await start(update, context)

# ================== CALLBACK ==================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    steps = get_steps(uid)

    # FACEBOOK
    if query.data == "fb":
        steps["fb"] = True
        await query.message.reply_text(
            "👍 VUI LÒNG HOÀN THÀNH NHIỆM VỤ Facebook.\n👉 Truy cập: https://facebook.com/tenfanpage"
        )
        return

    # TIKTOK
    if query.data == "tt":
        steps["tt"] = True
        await query.message.reply_text(
            "🎵 VUI LÒNG HOÀN THÀNH NHIỆM VỤ TikTok.\n👉 Truy cập: https://www.tiktok.com/@winbook888?_r=1&_t=ZS-91Md0CumhMK"
        )
        return

    # XÁC NHẬN
    if query.data == "confirm":
        # check tham gia channel
        if not await is_channel_member(context, uid):
            await query.message.reply_text(
                "❗ Bạn CHƯA tham gia kênh Telegram.\n👉 Vui lòng tham gia kênh trước."
            )
            return

        missing = []
        if not steps["fb"]:
            missing.append("Facebook")
        if not steps["tt"]:
            missing.append("TikTok")

        if missing:
            await query.message.reply_text(
                "❗ Bạn CHƯA hoàn thành:\n"
                + " • " + "\n • ".join(missing)
                + "\n👉 Vui lòng bấm đủ các nút trước khi xác nhận."
            )
            return

        await query.message.reply_text(
            "✅ Bạn đã hoàn thành nhiệm vụ.\n\n"
            "📸 Vui lòng gửi hình ảnh xác minh (Facebook + TikTok) cho CSKH để được duyệt & nhận CODE."
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
