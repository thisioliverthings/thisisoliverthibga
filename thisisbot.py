# إعداد الـ Token الخاص بالبوت
import logging
import random
import json
import os
import time
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import NetworkError, Unauthorized, InvalidToken

API_TOKEN = '8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0'
OWNER_CHAT_ID = '7161132306'  # ضع رقم دردشة المالك هنا

# إعداد تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

DB_FILE = "user_data.json"
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

# حفظ بيانات المستخدمين
def save_user_data():
    with open(DB_FILE, "w") as f:
        json.dump(user_data, f)

# دالة للتحقق من وجود مستخدم في قاعدة البيانات
def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'balance': 100,  # رصيد افتراضي أولي
            'completed_challenges': [],
        }
        save_user_data()
    return user_data[user_id]

# إضافة دالة إعادة المحاولة التلقائية
def retry_after_delay(func, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            func()
            break
        except NetworkError as e:
            retries += 1
            wait_time = 2 ** retries  # مضاعفة وقت الانتظار بعد كل محاولة
            logger.error(f"NetworkError: {e}. إعادة المحاولة بعد {wait_time} ثانية...")
            time.sleep(wait_time)
        except Unauthorized as e:
            logger.error(f"Unauthorized: {e}. لا يمكن إكمال العملية.")
            break
        except InvalidToken as e:
            logger.error(f"InvalidToken: {e}. تحقق من صحة الـ Token.")
            break

# دالة لإشعار المالك عند حدوث خطأ
def notify_owner(message, context):
    context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Error occurred: {message}")

# أمر لعرض الرصيد
def balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user = get_user(user_id)
    update.message.reply_text(f"💰 رصيدك الحالي: {user['balance']} عملة.")

# أمر لجمع العملات
def earn(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user = get_user(user_id)
    earned_amount = random.randint(10, 50)
    user['balance'] += earned_amount
    save_user_data()
    update.message.reply_text(f"🎉 لقد حصلت على {earned_amount} عملة! رصيدك الحالي هو {user['balance']}.")

# أمر لبدء البوت
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("مرحبًا بك في بوت الاقتصاد! استخدم /balance لمعرفة رصيدك و/earn لجمع العملات.")

# أمر المساعدة
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("""
أوامر البوت المتاحة:
- /balance: لمعرفة رصيدك.
- /earn: لجمع العملات.
- /challenge: للحصول على تحديات.
    """)

# التعامل مع الرسائل العامة
def handle_message(update: Update, context: CallbackContext) -> None:
    try:
        update.message.reply_text("يرجى استخدام الأوامر المتاحة مثل /balance و/earn.")
    except (NetworkError, Unauthorized, InvalidToken) as e:
        logger.error(f"Exception occurred: {e}")
        notify_owner(f"Exception occurred: {e}", context)

# الدالة الرئيسية لتشغيل البوت
def main() -> None:
    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher

    # أوامر البوت
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("earn", earn))

    # التعامل مع الرسائل العامة
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # تشغيل البوت مع إعادة المحاولة عند فشل الاتصال
    retry_after_delay(updater.start_polling)

    # الحفاظ على البوت في وضع التشغيل
    updater.idle()

if __name__ == '__main__':
    main()