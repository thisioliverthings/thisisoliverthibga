import logging
import random
import json
import os
import asyncio
import redis.asyncio as redis  # استخدام redis-py بدلاً من aioredis
from aiohttp import ClientSession
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import NetworkError, Unauthorized, InvalidToken

# إعداد الـ Token الخاص بالبوت
API_TOKEN = '8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0'
OWNER_CHAT_ID = '7161132306'

# إعداد تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# إعداد Redis
REDIS_URL = 'redis://localhost'
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# دالة لحفظ البيانات في Redis
async def save_user_data(user_id, data):
    await redis_client.hset(f"user:{user_id}", mapping=data)

# دالة لاسترجاع البيانات من Redis
async def get_user_data(user_id):
    user_data = await redis_client.hgetall(f"user:{user_id}")
    if not user_data:
        user_data = {
            'balance': 100,  # رصيد افتراضي أولي
            'completed_challenges': [],
        }
        await save_user_data(user_id, user_data)
    return user_data

# أمر لعرض الرصيد
def balance(update: Update, context) -> None:
    user_id = update.message.from_user.id
    user = asyncio.run(get_user_data(user_id))
    update.message.reply_text(f"💰 رصيدك الحالي: {user['balance']} عملة.")

# أمر لجمع العملات
def earn(update: Update, context) -> None:
    user_id = update.message.from_user.id
    user = asyncio.run(get_user_data(user_id))
    earned_amount = random.randint(10, 50)
    user['balance'] += earned_amount
    asyncio.run(save_user_data(user_id, user))
    update.message.reply_text(f"🎉 لقد حصلت على {earned_amount} عملة! رصيدك الحالي هو {user['balance']}.")

# أمر لبدء البوت
def start(update: Update, context) -> None:
    update.message.reply_text("مرحبًا بك في بوت الاقتصاد! استخدم /balance لمعرفة رصيدك و/earn لجمع العملات.")

# أمر المساعدة
def help_command(update: Update, context) -> None:
    update.message.reply_text("""
أوامر البوت المتاحة:
- /balance: لمعرفة رصيدك.
- /earn: لجمع العملات.
- /challenge: للحصول على تحديات.
    """)

# التعامل مع الرسائل العامة
def handle_message(update: Update, context) -> None:
    update.message.reply_text("يرجى استخدام الأوامر المتاحة مثل /balance و/earn.")

# دالة لإرسال إشعار للمالك عند حدوث خطأ
def notify_owner(message, context):
    context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Error occurred: {message}")

# التعامل مع الأخطاء
def handle_error(update: Update, context) -> None:
    error = context.error
    logger.error(f"Exception occurred: {error}")
    notify_owner(f"Exception occurred: {error}", context)

# تحسين استدعاءات API باستخدام aiohttp
async def fetch_external_data(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

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

    # التعامل مع الأخطاء
    dispatcher.add_error_handler(handle_error)

    # تشغيل البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()