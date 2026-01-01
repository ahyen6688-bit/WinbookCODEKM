import json
from datetime import datetime, timedelta
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

# ================== TIME (VN) ==================
def vn_today():
    return (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d")

# ================== AUTO DAILY RESET ==================
def auto_daily_reset(data):
    today = vn_today()
    if data.get("last_reset") == today:
        return
    data["count"] = 0
    data["users_today"] = []
    data["last_reset"] = today
    save_data(data)

# ================== CHECK JOIN CHANNEL ==================
async def is_channel_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

# ================== NOTIFY ADMIN ==================
async def notify_admin_km(context, user, slot_number, joined):
    status = "✅ ĐÃ THAM GIA CHANNEL" if joined else "❌ CHƯA THAM GIA CHANNEL"
    username = f"@{user.username}" if user.username else "(không có username)"
    time_vn = (datetime.utcnow() + timedelta(hours=7)).strftime("%H:%M:%S %d-%m-%Y")

    text = (
        "📢 USER BẤM /KM\n\n"
        f"👤 Tên: {user.full_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 ID: {user.id}\n"
        f"🎯 Thứ tự: {slot_number}/{TOTAL_SLOTS}\n"
        f"{status}\n"
        f"⏰ Thời gian: {time_vn}"
    )

    await context.bot.send_message(ADMIN_ID, text)

# ================== /START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    text = (
        "🔥🔥 WINBOOK – LÀM NHIỆM VỤ NHẬN 48K TIỀN THẬT 🔥🔥\n\n"
        "📅 THỜI GIAN SỰ KIỆN: 01/01 – 05/01/2026\n\n"
        "🎁 KHUYẾN MÃI HÔM NAY DÀNH CHO 100 NGƯỜI\n"
        f"👥 ĐÃ NHẬN: {data['count']}/{TOTAL_SLOTS}\n\n"
        "📣 YÊU CẦU THAM GIA:\n"
        "1️⃣ THAM GIA KÊNH WINBOOK\n"
        "2️⃣ FOLLOW TIKTOK WINBOOK\n"
        "3️⃣ LIKE FANPAGE + CHIA SẺ BÀI VIẾT KM 48K VÀO 03 HỘI NHÓM GAME BÀI TRÊN 5000 THÀNH VIÊN\n"
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
    user = update.effective_user
    chat_type = update.message.chat.type

    data = load_data()
    auto_daily_reset(data)

    if uid == ADMIN_ID or chat_type == "private":
        await start(update, context)
        return

    if uid in data.get("users", []):
    await update.message.reply_text(
        "❌ Bạn đã nhận khuyến mãi trước đó rồi.\n"
        "👉 Mỗi tài khoản chỉ được nhận 1 lần duy nhất."
    )
    return

    if data["count"] >= TOTAL_SLOTS:
        await update.message.reply_text(
            "❌ Hôm nay đã đủ 100 người.\n👉 Vui lòng quay lại vào ngày mai."
        )
        return

    # TÍNH SLOT
    data["count"] += 1
    data["users_today"].append(uid)   # để đếm 100/ngày
    data["users"].append(uid)         # chặn vĩnh viễn
    save_data(data)


    slot_number = data["count"]
    joined = await is_channel_member(context, uid)

    await notify_admin_km(context, user, slot_number, joined)
    await start(update, context)

# ================== CALLBACK ==================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    steps = get_steps(uid)

    if query.data == "fb":
        steps["fb"] = True
        await query.message.reply_text(
            "👍 Vui lòng hoàn thành nhiệm vụ Facebook:\n"
            "👉 https://www.facebook.com/profile.php?id=100076695622884\n\n"
            "✅ Sau khi xong, quay lại bấm *Xác nhận*",
            parse_mode="Markdown"
        )
        return

    if query.data == "tt":
        steps["tt"] = True
        await query.message.reply_text(
            "🎵 Vui lòng hoàn thành nhiệm vụ TikTok:\n"
            "👉 https://www.tiktok.com/@winbook888?_r=1&_t=ZS-91Md0CumhMK\n\n"
            "✅ Sau khi xong, quay lại bấm *Xác nhận*",
            parse_mode="Markdown"
        )
        return

    if query.data == "confirm":
        if not await is_channel_member(context, uid):
            await query.message.reply_text(
                "❗ Bạn **CHƯA tham gia** kênh Telegram.",
                parse_mode="Markdown"
            )
            return

        missing = []
        if not steps["fb"]:
            missing.append("Facebook")
        if not steps["tt"]:
            missing.append("TikTok")

        if missing:
            await query.message.reply_text(
                "❗ Bạn **CHƯA hoàn thành**:\n• " + "\n• ".join(missing),
                parse_mode="Markdown"
            )
            return

        await query.message.reply_text(
            "✅ Bạn đã **hoàn thành nhiệm vụ**.\n"
            "📸 Vui lòng **gửi ảnh xác minh** cho CSKH."
        )

# ================== MAIN ==================
def main():
    data = load_data()
    auto_daily_reset(data)

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("km", km))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
