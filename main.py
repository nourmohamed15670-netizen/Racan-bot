import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# بيانات الأقسام والمواد
# =========================

SECTIONS = {
    "guidance": {
        "name": "🌱 Guidance – الإرشاد",
        "subjects": [
            "ميكنة زراعية",
            "المجتمع الريفي المحلي",
            "تغير السلوك البشري",
            "تطبيقات الحاسب الآلي",
            "اقتصاد ميكرو",
            "الإرشاد الريفي",
            "تنظيم المجتمع الريفي",
        ],
    },

    "economy": {
        "name": "💰 Economy – الاقتصاد",
        "subjects": [
            "أسس محاسبة زراعية",
            "ميكنة زراعية",
            "اقتصاد ميكرو",
            "تطبيقات حاسب آلي",
            "اقتصاد موارد زراعية",
            "تنظيم مجتمع ريفي",
            "الإرشاد الريفي",
        ],
    },
}


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "🌱 Guidance – الإرشاد",
                callback_data="section_guidance"
            )
        ],
        [
            InlineKeyboardButton(
                "💰 Economy – الاقتصاد",
                callback_data="section_economy"
            )
        ],
    ]

    await update.message.reply_text(
        "✨ Racan\n\n"
        "أهلاً بيك في بوت ✨ Racan\n"
        "اختار القسم:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# عرض المواد
# =========================

async def show_subjects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    section = query.data.replace("section_", "")
    context.user_data["section"] = section

    section_name = SECTIONS[section]["name"]
    subjects = SECTIONS[section]["subjects"]

    keyboard = []

    for i, subject in enumerate(subjects):
        keyboard.append([
            InlineKeyboardButton(
                f"📚 {subject}",
                callback_data=f"subject_{section}_{i}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 رجوع", callback_data="home")
    ])

    await query.edit_message_text(
        f"✨ Racan\n\n"
        f"{section_name}\n\n"
        f"اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# اختيار المادة
# =========================

async def show_types(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    section = parts[1]
    subject_index = int(parts[2])

    subject = SECTIONS[section]["subjects"][subject_index]

    context.user_data["section"] = section
    context.user_data["subject"] = subject

    keyboard = [
        [
            InlineKeyboardButton(
                "🎓 محاضرات",
                callback_data=f"lectures_{section}_{subject_index}"
            )
        ],
        [
            InlineKeyboardButton(
                "📝 سكاشن",
                callback_data=f"sections_{section}_{subject_index}"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 رجوع",
                callback_data=f"section_{section}"
            )
        ],
    ]

    await query.edit_message_text(
        f"✨ Racan\n\n"
        f"📚 المادة:\n{subject}\n\n"
        f"اختر نوع المحتوى:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# المحاضرات / السكاشن
# =========================

async def show_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")

    content_type = parts[0]
    section = parts[1]
    subject_index = int(parts[2])

    subject = SECTIONS[section]["subjects"][subject_index]

    if content_type == "lectures":
        title = "🎓 المحاضرات"
    else:
        title = "📝 السكاشن"

    keyboard = [
        [
            InlineKeyboardButton(
                "🔙 رجوع",
                callback_data=f"subject_{section}_{subject_index}"
            )
        ]
    ]

    await query.edit_message_text(
        f"✨ Racan\n\n"
        f"📚 {subject}\n"
        f"{title}\n\n"
        f"📂 لا توجد ملفات مضافة حتى الآن.\n\n"
        f"سنضيف ملفات الـPDF هنا.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# الصفحة الرئيسية
# =========================

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🌱 Guidance – الإرشاد",
                callback_data="section_guidance"
            )
        ],
        [
            InlineKeyboardButton(
                "💰 Economy – الاقتصاد",
                callback_data="section_economy"
            )
        ],
    ]

    await query.edit_message_text(
        "✨ Racan\n\n"
        "اختار القسم:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# التعامل مع الأزرار
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    data = query.data

    if data == "home":
        await home(update, context)

    elif data.startswith("section_"):
        await show_subjects(update, context)

    elif data.startswith("subject_"):
        await show_types(update, context)

    elif data.startswith("lectures_") or data.startswith("sections_"):
        await show_content(update, context)


# =========================
# تشغيل البوت
# =========================

def main():

    TOKEN = os.getenv("BOT_TOKEN")

    if not TOKEN:
        raise ValueError(
            "BOT_TOKEN غير موجود. أضفه في Environment Variables."
        )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✨ Racan Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
