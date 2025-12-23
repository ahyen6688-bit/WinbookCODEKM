import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, TOTAL_SLOTS, ADMIN_ID, CHANNEL_ID, GROUP_ID

DATA_FILE = "data.json"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def is_member(bot, user_id, chat_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    text = (
    "🔥🔥 WINBOOK – LÀM NHIỆM VỤ NHẬN TIỀN THẬT 🔥🔥\n\n"
    "📅 THỜI GIAN SỰ KIỆN: 01/01 – 05/01/2026\n\n"
    "🎁 KHUYẾN MÃI HÔM NAY DÀNH CHO 100 NGƯỜI\n"
    f"👥 ĐÃ NHẬN: {data['count']}/{TOTAL_SLOTS}\n\n"
    "📣 YÊU CẦU THAM GIA:\n"
    "1️⃣ THAM GIA KÊNH WINBOOK\n"
    "2️⃣ FOLLOW TIKTOK WINBOOK\n"
    "3️⃣ LIKE FANPAGE + CHIA SẺ 03 HỘI NHÓM\n"
    "   • CHIA SẺ TRANG CÁ NHÂN\n"
    "   • TAG 03 BẠN BÈ (CÓ TRÊN 200 BẠN BÈ)\n"
    "4️⃣ ĐĂNG KÝ 01 TÀI KHOẢN GAME (NẾU CHƯA CÓ)\n\n"
    "📸 GỬI ẢNH FOLLOW TIKTOK & FANPAGE\n"
    "👉 LIÊN HỆ CSKH ĐỂ XÁC NHẬN CODE\n\n"
    "👇 HOÀN THÀNH NHIỆM VỤ, BẤM NÚT XÁC NHẬN ĐỂ NHẬN KHUYẾN MÃI"
)
    keyboard = [
    [
        InlineKeyboardButton("📢 THAM GIA KÊNH", url="https://t.me/winbookEvent")
    ],
    [
        InlineKeyboardButton("👍 LIKE FANPAGE", url="https://www.facebook.com/profile.php?id=100076695622884"),
        InlineKeyboardButton(
            "🎵 FOLLOW TIKTOK",
            url="https://www.tiktok.com/@winbook888?_r=1&_t=ZS-92LwUEoDMPs"
        )
    ],
    [
        InlineKeyboardButton("👩‍💼 TELE CS001", url="https://t.me/WinbookCSKH001"),
        InlineKeyboardButton("👨‍💼 TELE CS002", url="https://t.me/WinbookCSKH002")
    ],
    [
        InlineKeyboardButton("✅ XÁC NHẬN KHUYẾN MÃI", callback_data="join")
    ]
]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )


async def join_km(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_data()
    user_id = query.from_user.id
    bot = context.bot

    if not await is_member(bot, user_id, CHANNEL_ID):
        await query.edit_message_text(
            "❌ Bạn CHƯA tham gia KÊNH Telegram.\n"
            "👉 Vui lòng tham gia kênh rồi quay lại bấm xác nhận."
        )
        return

    if not await is_member(bot, user_id, GROUP_ID):
        await query.edit_message_text(
            "❌ Bạn CHƯA tham gia NHÓM CHAT.\n"
            "👉 Vui lòng tham gia nhóm rồi quay lại bấm xác nhận."
        )
        return

    if user_id in data["users"]:
        await query.edit_message_text("❗ Bạn đã nhận KM rồi.")
        return

    if data["count"] >= TOTAL_SLOTS:
        await query.edit_message_text("❌ Hết lượt hôm nay. Hẹn bạn ngày mai nha ❤️")
        return

    data["count"] += 1
    data["users"].append(user_id)
    save_data(data)

    await query.edit_message_text(
        "🎉 NHẬN KM THÀNH CÔNG\n"
        f"👉 Bạn là người thứ #{data['count']}\n"
        "📩 Vui lòng inbox admin để nhận KM"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    save_data({"count": 0, "users": []})
    await update.message.reply_text("🔄 Đã reset lượt KM hôm nay.")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("km", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CallbackQueryHandler(join_km))

    app.run_polling()


if __name__ == "__main__":
    main()
