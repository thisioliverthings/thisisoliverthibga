import logging
import random
import json
import os
import time
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import NetworkError, RetryAfter, TimedOut

# إعداد الـ Token الخاص بالبوت
API_TOKEN = '7328823780:AAGgppB9_38ParQ2mdurprSFusMM97e1LAM'

# تفعيل نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# دالة إرسال التحدي مع معالجة أخطاء الشبكة
def send_message_safe(context, chat_id, message):
    try:
        context.bot.send_message(chat_id=chat_id, text=message)
    except NetworkError as e:
        logger.error(f"NetworkError occurred: {e}. Retrying...")
        time.sleep(5)  # الانتظار قليلاً قبل إعادة المحاولة
        try:
            context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.error(f"Failed again: {e}")
    except RetryAfter as e:
        logger.warning(f"Rate limit exceeded. Retrying after {e.retry_after} seconds.")
        time.sleep(e.retry_after)
        try:
            context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.error(f"Failed after retry: {e}")
    except TimedOut as e:
        logger.error(f"Timed out while sending message: {e}. Retrying...")
        time.sleep(5)
        try:
            context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.error(f"Failed after timeout retry: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

# دالة إرسال التحدي
def send_challenge(update: Update, context: CallbackContext, challenge_type: str):
    chat_id = update.message.chat_id
    challenge = f"Today's challenge is: {random.choice(['Solve a puzzle!', 'Write a story!', 'Code a function!'])}"
    
    send_message_safe(context, chat_id, challenge)

# التعامل مع الأمر /start
def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    message = "Welcome to the Challenge Bot! Use /challenge to get a challenge."
    send_message_safe(context, chat_id, message)

# التعامل مع الأمر /help
def help_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    keyboard = [
        [InlineKeyboardButton("المالك للإبلاغ عن مشكلة", url="https://t.me/oliceer")]  # ضع الرابط الخاص بك هنا
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = """👋 مرحبا بك في بوت التحديات!

🌟 مميزات البوت:
- تحديات يومية وأسبوعية: استخدم /challenge للحصول على التحديات.
- نظام النقاط: احصل على نقاط عند إكمال التحديات.
- تفاعل معنا وأكمل التحديات للحصول على المزيد من النقاط!"""
    
    try:
        context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in help command: {e}")

# التعامل مع الأمر /challenge
def challenge(update: Update, context: CallbackContext) -> None:
    send_challenge(update, context, 'daily')

# الدالة الرئيسية لتشغيل البوت
def main() -> None:
    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher

    # تسجيل الأوامر المختلفة
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("challenge", challenge))

    # تشغيل البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()