import logging
import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
from datetime import datetime

# إعداد الـ Token الخاص بالبوت
API_TOKEN = '8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0'
OWNER_CHAT_ID = '7161132306'  # ضع رقم دردشة المالك هنا

# تفعيل نظام التسجيل لمراقبة الأخطاء
error_log_file = "error_log.txt"
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(error_log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_FILE = "user_data.json"

# تحميل بيانات المستخدمين
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

# حفظ بيانات المستخدمين
def save_user_data():
    with open(DB_FILE, "w") as f:
        json.dump(user_data, f)

# التعامل مع الرسائل العامة
def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_text = update.message.text.strip().lower()

    user_language = user_data.get(user_id, {}).get('language', 'العربية')

    responses = {
        "العربية": {
            "رصيدي": "رصيدك الحالي: {balance}",
            "سحب": "لقد قمت بسحب {amount}!",
            "إيداع": "لقد قمت بإيداع {amount}!",
            "شكرًا": "على الرحب والسعة! هل تحتاج إلى مساعدة أخرى؟",
            "تغيير اللغة": "اختر لغتك:",
            "مساعدة": "للحصول على المساعدة، يرجى اتباع الأوامر التالية:"
        },
        "English": {
            "my balance": "Your current balance is: {balance}",
            "withdraw": "You have withdrawn {amount}!",
            "deposit": "You have deposited {amount}!",
            "thank you": "You're welcome! Do you need any more help?",
            "change language": "Choose your language:",
            "help": "To get help, please follow these commands:"
        }
    }

    if "رصيدي" in user_text:
        balance = user_data.get(user_id, {}).get('balance', 0)
        response_message = responses[user_language]["رصيدي"].format(balance=balance)
        context.bot.send_message(chat_id=update.message.chat_id, text=response_message)

    elif user_text.startswith("سحب"):
        try:
            amount = int(user_text.split()[1])
            if user_data.get(user_id, {}).get('balance', 0) >= amount:
                user_data[user_id]['balance'] -= amount
                save_user_data()
                response_message = responses[user_language]["سحب"].format(amount=amount)
                context.bot.send_message(chat_id=update.message.chat_id, text=response_message)
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text="رصيدك غير كافٍ.")
        except (IndexError, ValueError):
            context.bot.send_message(chat_id=update.message.chat_id, text="يرجى تحديد المبلغ بشكل صحيح.")

    elif user_text.startswith("إيداع"):
        try:
            amount = int(user_text.split()[1])
            user_data[user_id]['balance'] += amount
            save_user_data()
            response_message = responses[user_language]["إيداع"].format(amount=amount)
            context.bot.send_message(chat_id=update.message.chat_id, text=response_message)
        except (IndexError, ValueError):
            context.bot.send_message(chat_id=update.message.chat_id, text="يرجى تحديد المبلغ بشكل صحيح.")

    elif "شكرًا" in user_text:
        context.bot.send_message(chat_id=update.message.chat_id, text=responses[user_language]["شكرًا"])

    elif "تغيير اللغة" in user_text:
        change_language(update, context)

    elif "مساعدة" in user_text:
        help_command(update, context)

    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="لم أفهم طلبك. حاول مرة أخرى.")

# دالة عرض المساعدة
def help_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("القسم 1: الأوامر الأساسية", callback_data='help_section_1')],
        [InlineKeyboardButton("القسم 2: نظام النقاط", callback_data='help_section_2')],
        [InlineKeyboardButton("القسم 3: إدارة اللغة", callback_data='help_section_3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "مرحبًا! اختر قسمًا لعرض الشرح:",
        reply_markup=reply_markup
    )

# دالة للتعامل مع أزرار الشرح
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    help_texts = {
        'help_section_1': (
            "📜 **الأوامر الأساسية:**\n"
            "1. **بدء:** اكتب 'start' - لبدء التفاعل مع البوت.\n"
            "2. **تغيير اللغة:** اكتب 'change language' - لتغيير لغة البوت.\n"
            "3. **مساعدة:** اكتب 'help' - لعرض تعليمات الاستخدام."
        ),
        'help_section_2': (
            "📊 **نظام النقاط:**\n"
            "1. **رصيدك:** اكتب 'رصيدي' لمعرفة رصيدك الحالي.\n"
            "2. **إيداع:** اكتب 'إيداع [المبلغ]' لإيداع المال في رصيدك.\n"
            "3. **سحب:** اكتب 'سحب [المبلغ]' لسحب المال من رصيدك."
        ),
        'help_section_3': (
            "🌐 **إدارة اللغة:**\n"
            "1. **اختيار اللغة:** عند بدء التفاعل مع البوت، يمكنك اختيار لغتك.\n"
            "2. **تغيير اللغة:** اكتب 'تغيير اللغة' لتغيير اللغة لاحقًا."
        )
    }

    response_message = help_texts.get(query.data, "قسم غير معروف.")
    query.answer()
    query.edit_message_text(text=response_message)

# التعامل مع الأمر /start
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data.setdefault(user_id, {'language': 'العربية', 'balance': 0})
    save_user_data()

    keyboard = [
        [InlineKeyboardButton("العربية", callback_data='set_language_ar')],
        [InlineKeyboardButton("English", callback_data='set_language_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "مرحبًا بك! من فضلك اختر لغتك:",
        reply_markup=reply_markup
    )

# التعامل مع تغيير اللغة
def set_language(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    language = 'العربية' if query.data == 'set_language_ar' else 'English'

    user_data.setdefault(user_id, {})['language'] = language
    save_user_data()

    context.bot.send_message(
        chat_id=user_id,
        text=f"تم تغيير اللغة إلى: {language}"
    )

    query.answer()  # تأكيد الضغط على الزر

# التعامل مع الأمر /change_language
def change_language(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("العربية", callback_data='set_language_ar')],
        [InlineKeyboardButton("English", callback_data='set_language_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "اختر لغتك:",
        reply_markup=reply_markup
    )

# الدالة الرئيسية لتشغيل البوت
def main() -> None:
    updater = Updater(API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # تسجيل الأوامر المختلفة
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('change_language', change_language))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CallbackQueryHandler(set_language, pattern='^set_language_'))

    # تشغيل البوت
    try:
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Error starting the bot: {e}")
        with open(error_log_file, "a") as f:
            f.write(f"{datetime.now()}: {e}\n")

if __name__ == '__main__':
    main()