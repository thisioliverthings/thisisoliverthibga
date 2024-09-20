import logging
import json
import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

# إعداد الـ Token الخاص بالبوت
API_TOKEN = '8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0'
OWNER_CHAT_ID = '7161132306'

# تفعيل نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إعداد قاعدة البيانات
DATABASE_FILE = "user_data.db"

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'العربية',
            balance REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# حفظ بيانات المستخدم
def save_user_data(user_id, language, balance):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, language, balance)
        VALUES (?, ?, ?)
    ''', (user_id, language, balance))
    conn.commit()
    conn.close()

# تحميل بيانات المستخدم
def load_user_data(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT language, balance FROM users WHERE user_id = ?', (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data if data else ('العربية', 0)

# التعامل مع الرسائل العامة
def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    language, balance = load_user_data(user_id)
    save_user_data(user_id, language, balance)
    context.bot.send_message(chat_id=update.message.chat_id, text="🎉 مرحبًا بك في بوتنا الرائع! استخدم الأمر 'help' لمساعدتك.")

# دالة عرض المساعدة
def help_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("✨ القسم 1: الأوامر الأساسية", callback_data='help_section_1')],
        [InlineKeyboardButton("💰 القسم 2: نظام النقاط", callback_data='help_section_2')],
        [InlineKeyboardButton("🌍 القسم 3: إدارة اللغة", callback_data='help_section_3')],
        [InlineKeyboardButton("🎟️ القسم 4: العضويات", callback_data='help_section_4')],
        [InlineKeyboardButton("🎁 القسم 5: العروض والمكافآت", callback_data='help_section_5')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='help_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("📚 مرحبًا! اختر قسمًا لعرض الشرح:", reply_markup=reply_markup)

# دالة للتعامل مع أزرار الشرح
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    help_texts = {
        'help_section_1': (
            "📜 <b>الأوامر الأساسية:</b><br>"
            "<ul>"
            "<li>1️⃣ <b>تغيير اللغة:</b> اكتب '<code>تغيير اللغة</code>' لتغيير لغة البوت.</li>"
            "<li>2️⃣ <b>مساعدة:</b> اكتب '<code>help</code>' لعرض التعليمات.</li>"
            "<li>3️⃣ <b>الإعدادات:</b> اضبط إعداداتك باستخدام '<code>settings</code>'.</li>"
            "<li>4️⃣ <b>المعلومات:</b> تعرف على البوت عبر '<code>info</code>'.</li>"
            "<li>5️⃣ <b>اقتراحات:</b> شارك اقتراحاتك بكتابة '<code>اقتراح</code>'.</li>"
            "<li>6️⃣ <b>التحقق من حالة الحساب:</b> اكتب '<code>حالة</code>' للتحقق من حالة حسابك والمكافآت المحتملة.</li>"
            "</ul>"
        ),
        'help_section_2': (
            "📊 <b>نظام النقاط والمحفظة:</b><br>"
            "<ul>"
            "<li>1️⃣ <b>رصيدك:</b> اكتب '<code>رصيدي</code>' لعرض رصيدك.</li>"
            "<li>2️⃣ <b>إيداع:</b> استخدم '<code>إيداع [المبلغ]</code>' لإضافة الأموال إلى حسابك.</li>"
            "<li>3️⃣ <b>سحب:</b> اكتب '<code>سحب [المبلغ]</code>' لسحب الأموال.</li>"
            "<li>4️⃣ <b>تحويل:</b> أرسل أموالًا إلى مستخدم آخر باستخدام '<code>تحويل [المبلغ] إلى [المستخدم]</code>'.</li>"
            "<li>5️⃣ <b>المكافآت اليومية:</b> احصل على مكافأتك اليومية بكتابة '<code>المكافأة</code>'.</li>"
            "<li>6️⃣ <b>مستوى العضوية:</b> تحقق من مستوى عضويتك الحالي باستخدام '<code>العضوية</code>'.</li>"
            "<li>7️⃣ <b>سجل المعاملات:</b> اكتب '<code>المعاملات</code>' لعرض تاريخ معاملاتك المالية.</li>"
            "</ul>"
        ),
        'help_section_3': (
            "🌐 <b>إدارة اللغة:</b><br>"
            "<ul>"
            "<li>1️⃣ <b>اختيار اللغة:</b> اختر لغتك عند بدء التفاعل.</li>"
            "<li>2️⃣ <b>تغيير اللغة:</b> استخدم '<code>تغيير اللغة</code>' لتبديل اللغة.</li>"
            "<li>3️⃣ <b>اللغات المتاحة:</b> اكتب '<code>اللغات</code>' لعرض قائمة اللغات المتوفرة.</li>"
            "<li>4️⃣ <b>تفضيلات اللغة:</b> قم بحفظ اللغة المفضلة لديك بكتابة '<code>حفظ اللغة</code>'.</li>"
            "</ul>"
        ),
        'help_section_4': (
            "💼 <b>العضويات والاشتراكات:</b><br>"
            "<ul>"
            "<li>1️⃣ <b>الترقية:</b> اكتب '<code>ترقية [نوع العضوية]</code>' لترقية حسابك.</li>"
            "<li>2️⃣ <b>التحقق من العضوية:</b> استخدم '<code>العضوية</code>' للتحقق من مستوى عضويتك الحالي.</li>"
            "<li>3️⃣ <b>إلغاء الاشتراك:</b> إذا كنت ترغب في إلغاء الاشتراك، اكتب '<code>إلغاء الاشتراك</code>'.</li>"
            "</ul>"
        ),
        'help_section_5': (
            "🎁 <b>عروض ومكافآت خاصة:</b><br>"
            "<ul>"
            "<li>1️⃣ <b>العروض:</b> اكتب '<code>العروض</code>' لعرض العروض الحالية المتاحة لك.</li>"
            "<li>2️⃣ <b>المكافأة الخاصة:</b> تحقق من وجود مكافأة خاصة بكتابة '<code>مكافأة خاصة</code>'.</li>"
            "<li>3️⃣ <b>المسابقات الشهرية:</b> شارك في المسابقات الشهرية باستخدام '<code>مسابقة الشهر</code>'.</li>"
            "</ul>"
        )
    }

    help_text = help_texts.get(query.data)
    if help_text:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='help_menu')]])
        query.edit_message_text(text=help_text, parse_mode='HTML', reply_markup=reply_markup)
    elif query.data == 'help_menu':
        help_command(update, context)

# دالة التعامل مع الأوامر
def handle_commands(update: Update, context: CallbackContext) -> None:
    command = update.message.text
    user_id = update.message.from_user.id
    language, balance = load_user_data(user_id)

    if command == '/start':
        handle_message(update, context)
    elif command == 'help':
        help_command(update, context)
    elif command == 'تغيير اللغة':
        update.message.reply_text("⚙️ يرجى تحديد اللغة الجديدة.")
    elif command == 'settings':
        update.message.reply_text("🛠️ هنا يمكنك ضبط إعداداتك.")
    elif command == 'info':
        update.message.reply_text("ℹ️ هذا بوت يساعدك في إدارة حسابك.")
    elif command.startswith('إيداع'):
        amount = float(command.split()[1])
        balance += amount
        save_user_data(user_id, language, balance)
        update.message.reply_text(f"💵 تم إيداع <b>{amount}</b> بنجاح. رصيدك الجديد هو <b>{balance}</b>.", parse_mode='HTML')
    elif command.startswith('سحب'):
        amount = float(command.split()[1])
        if amount <= balance:
            balance -= amount
            save_user_data(user_id, language, balance)
            update.message.reply_text(f"💸 تم سحب <b>{amount}</b> بنجاح. رصيدك الجديد هو <b>{balance}</b>.", parse_mode='HTML')
        else:
            update.message.reply_text("❌ رصيدك غير كافٍ لإجراء هذه العملية.")
    elif command.startswith('تحويل'):
        parts = command.split()
        amount = float(parts[1])
        recipient = parts[3]

        # تحقق من وجود المستخدم
        recipient_data = load_user_data(int(recipient))
        if recipient_data:
            recipient_balance = recipient_data[1]
            if amount <= balance:
                balance -= amount
                recipient_balance += amount
                save_user_data(user_id, language, balance)
                save_user_data(int(recipient), recipient_data[0], recipient_balance)
                update.message.reply_text(f"➡️ تم تحويل <b>{amount}</b> إلى <b>{recipient}</b> بنجاح.", parse_mode='HTML')
            else:
                update.message.reply_text("❌ رصيدك غير كافٍ لإجراء هذه العملية.")
        else:
            update.message.reply_text("❓ لم يتم العثور على المستخدم الذي تحاول التحويل إليه.")
    elif command == 'رصيدي':
        update.message.reply_text(f"💰 رصيدك الحالي هو: <b>{balance}</b>.", parse_mode='HTML')

# الدالة الرئيسية لتشغيل البوت
def main() -> None:
    init_db()  # تأكد من تهيئة قاعدة البيانات عند بدء تشغيل البوت
    updater = Updater(API_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", handle_message))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_commands))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()