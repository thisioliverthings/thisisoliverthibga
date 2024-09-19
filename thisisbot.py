import logging
import random
import json
import os
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.error import NetworkError, Unauthorized, InvalidToken

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

# دالة إرسال التحدي
async def send_challenge(update: Update, context: CallbackContext, challenge_type: str):
    chat_id = update.message.chat_id
    challenges = {
        "daily": ["Solve the riddle: What has keys but can't open locks?", "Guess the number between 1 and 10."],
        "weekly": ["Write a funny story using the words 'dog', 'moon', and 'robot'.", "Create a meme about programming."]
    }
    if challenge_type in challenges:
        challenge = random.choice(challenges[challenge_type])
        await context.bot.send_message(chat_id=chat_id, text=f"Today's challenge is: {challenge}")
    else:
        await context.bot.send_message(chat_id=chat_id, text="No challenges available at the moment.")

# التعامل مع الأمر /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Welcome to the Challenge Bot! Use /challenge to get a challenge.")

# التعامل مع الأمر /help
async def help_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("المالك للإبلاغ عن مشكلة", url="https://t.me/oliceer")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        """👋 مرحبا بك في بوت التحديات!

🌟 مميزات البوت:
- تحديات يومية وأسبوعية: استخدم /challenge للحصول على التحديات.
- نظام النقاط: احصل على نقاط عند إكمال التحديات.
- تفاعل معنا وأكمل التحديات للحصول على المزيد من النقاط!""",
        reply_markup=reply_markup
    )

# التعامل مع الأمر /challenge
async def challenge(update: Update, context: CallbackContext) -> None:
    await send_challenge(update, context, 'daily')

# الدالة لإرسال إشعار للمالك عند حدوث خطأ
async def notify_owner(message, context):
    await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Error occurred: {message}")

# التعامل مع الرسائل العامة
async def handle_message(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user_text = update.message.text.strip().lower()

    # إذا لم يكن المستخدم موجودًا في قاعدة البيانات
    if user_id not in user_data:
        user_data[user_id] = {
            'points': 0,
            'completed_challenges': [],
            'active_challenge': None
        }
        save_user_data()

    try:
        # معالجة التحديات النشطة
        if user_data[user_id]['active_challenge']:
            active_challenge = user_data[user_id]['active_challenge']
            expected_answer = active_challenge['answer'].strip().lower()

            if user_text == expected_answer:
                user_data[user_id]['points'] += 10
                user_data[user_id]['completed_challenges'].append(active_challenge['question'])
                user_data[user_id]['active_challenge'] = None
                save_user_data()
                response_message = "إجابة صحيحة! لقد حصلت على 10 نقاط."
            else:
                response_message = "الإجابة غير صحيحة. حاول مرة أخرى!"

            await context.bot.send_message(chat_id=chat_id, text=response_message)

        # التعامل مع العبارات المتعلقة بإكمال التحديات
        elif "challenge completed" in user_text:
            if user_data[user_id]['completed_challenges']:
                user_data[user_id]['points'] += 10
                save_user_data()
                response_message = "تهانينا! لقد حصلت على 10 نقاط إضافية."
            else:
                response_message = "لم تقم بإكمال أي تحديات بعد."

            await context.bot.send_message(chat_id=chat_id, text=response_message)

        # تعامل مع عبارات الشكر
        elif "thank you" in user_text:
            await context.bot.send_message(chat_id=chat_id, text="على الرحب والسعة! هل ترغب في المزيد من التحديات؟")

        # توفير رسالة افتراضية للرسائل غير المعروفة
        else:
            await context.bot.send_message(chat_id=chat_id, text="آسف، لم أفهم طلبك. يرجى استخدام الأوامر المتاحة مثل /challenge للحصول على التحديات.")

    except (NetworkError, Unauthorized, InvalidToken) as e:
        logger.error(f"Exception occurred: {e}")
        await notify_owner(f"Exception occurred: {e}", context)

# الدالة الرئيسية لتشغيل البوت
async def main() -> None:
    updater = Updater(API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # تسجيل الأوامر المختلفة
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("challenge", challenge))

    # تسجيل الرسائل العامة
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # تشغيل البوت
    await updater.start_polling()
    await updater.idle()

if __name__ == '__main__':
    asyncio.run(main())