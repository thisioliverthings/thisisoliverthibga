import logging
import random
import json
import os
import redis.asyncio as redis
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

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
async def balance(update: Update, context) -> None:
    user_id = update.message.from_user.id
    user = await get_user_data(user_id)
    await update.message.reply_text(f"💰 رصيدك الحالي: {user['balance']} عملة.")

# أمر لجمع العملات
async def earn(update: Update, context) -> None:
    user_id = update.message.from_user.id
    user = await get_user_data(user_id)
    earned_amount = random.randint(10, 50)
    user['balance'] += earned_amount
    await save_user_data(user_id, user)
    await update.message.reply_text(f"🎉 لقد حصلت على {earned_amount} عملة! رصيدك الحالي هو {user['balance']}.")

# أمر لبدء البوت
async def start(update: Update, context) -> None:
    await update.message.reply_text("مرحبًا بك في بوت الاقتصاد! استخدم /balance لمعرفة رصيدك و/earn لجمع العملات.")

# أمر المساعدة
async def help_command(update: Update, context) -> None:
    await update.message.reply_text("""
أوامر البوت المتاحة:
- /balance: لمعرفة رصيدك.
- /earn: لجمع العملات.
- /challenge: للحصول على تحديات.
    """)

# التعامل مع الرسائل العامة
async def handle_message(update: Update, context) -> None:
    await update.message.reply_text("يرجى استخدام الأوامر المتاحة مثل /balance و/earn.")

# دالة لإرسال إشعار للمالك عند حدوث خطأ
async def notify_owner(message, context):
    await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Error occurred: {message}")

# التعامل مع الأخطاء
async def handle_error(update: Update, context) -> None:
    error = context.error
    logger.error(f"Exception occurred: {error}")
    await notify_owner(f"Exception occurred: {error}", context)

# الدالة الرئيسية لتشغيل البوت
async def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    # أوامر البوت
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("earn", earn))

    # التعامل مع الرسائل العامة
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # التعامل مع الأخطاء
    application.add_error_handler(handle_error)

    # تشغيل البوت
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()