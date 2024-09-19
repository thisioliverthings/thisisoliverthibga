import logging
import random
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# إعداد الـ Token الخاص بالبوت
API_TOKEN = '7328823780:AAGgppB9_38ParQ2mdurprSFusMM97e1LAM'

# تفعيل نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

DB_FILE = "user_data.json"
CHALLENGE_FILE = "challenges.json"

# تحميل بيانات المستخدمين
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

# تحميل تحديات
if os.path.exists(CHALLENGE_FILE):
    with open(CHALLENGE_FILE, "r") as f:
        challenges = json.load(f)
else:
    challenges = {
        "daily": ["Solve the riddle: What has keys but can't open locks?", "Guess the number between 1 and 10."],
        "weekly": ["Write a funny story using the words 'dog', 'moon', and 'robot'.", "Create a meme about programming."]
    }

# حفظ بيانات المستخدمين
def save_user_data():
    with open(DB_FILE, "w") as f:
        json.dump(user_data, f)

# حفظ التحديات
def save_challenges():
    with open(CHALLENGE_FILE, "w") as f:
        json.dump(challenges, f)

# دالة إرسال التحدي
def send_challenge(update: Update, context: CallbackContext, challenge_type: str):
    chat_id = update.message.chat_id
    if challenge_type in challenges:
        challenge = random.choice(challenges[challenge_type])
        context.bot.send_message(chat_id=chat_id, text=f"Today's challenge is: {challenge}")
    else:
        context.bot.send_message(chat_id=chat_id, text="No challenges available at the moment.")

# التعامل مع الأمر /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to the Challenge Bot! Use /challenge to get a challenge.")

# التعامل مع الأمر /help
def help_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("المالك للإبلاغ عن مشكلة", url="https://t.me/oliceer")]  # ضع الرابط الخاص بك هنا
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        """👋 مرحبا بك في بوت التحديات!

🌟 مميزات البوت:
- تحديات يومية وأسبوعية: استخدم /challenge للحصول على التحديات.
- نظام النقاط: احصل على نقاط عند إكمال التحديات.
- تفاعل معنا وأكمل التحديات للحصول على المزيد من النقاط!""",
        reply_markup=reply_markup
    )

# التعامل مع الأمر /challenge
def challenge(update: Update, context: CallbackContext) -> None:
    send_challenge(update, context, 'daily')

# التعامل مع الرسائل العامة
def handle_message(update: Update, context: CallbackContext) -> None:
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

        context.bot.send_message(chat_id=chat_id, text=response_message)

    # التعامل مع العبارات المتعلقة بإكمال التحديات
    elif "challenge completed" in user_text:
        if user_data[user_id]['completed_challenges']:
            user_data[user_id]['points'] += 10
            save_user_data()
            response_message = "تهانينا! لقد حصلت على 10 نقاط إضافية."
        else:
            response_message = "لم تقم بإكمال أي تحديات بعد."

        context.bot.send_message(chat_id=chat_id, text=response_message)

    # تعامل مع عبارات الشكر
    elif "thank you" in user_text:
        context.bot.send_message(chat_id=chat_id, text="على الرحب والسعة! هل ترغب في المزيد من التحديات؟")

    # توفير رسالة افتراضية للرسائل غير المعروفة
    else:
        context.bot.send_message(chat_id=chat_id, text="آسف، لم أفهم طلبك. يرجى استخدام الأوامر المتاحة مثل /challenge للحصول على التحديات.")

# الدالة الرئيسية لتشغيل البوت
def main() -> None:
    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher

    # تسجيل الأوامر المختلفة
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("challenge", challenge))

    # تسجيل الرسائل العامة
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # تشغيل البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()