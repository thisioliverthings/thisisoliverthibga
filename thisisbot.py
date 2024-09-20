import logging
import sqlite3
from contextlib import closing
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
import random

# إعداد الـ Token الخاص بالبوت
API_TOKEN = '8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0'
OWNER_CHAT_ID = '7161132306'

# تفعيل نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إعداد قاعدة البيانات
DATABASE_FILE = "user_data.db"

def init_db():
    with closing(sqlite3.connect(DATABASE_FILE)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'العربية',
                balance REAL DEFAULT 0,
                account_number TEXT UNIQUE
            )
        ''')
        conn.commit()

def generate_account_number():
    return str(random.randint(1000000000, 9999999999))  # رقم حساب مكون من 10 أرقام

def save_user_data(user_id, language, balance, account_number):
    with closing(sqlite3.connect(DATABASE_FILE)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, language, balance, account_number)
            VALUES (?, ?, ?, ?)
        ''', (user_id, language, balance, account_number))
        conn.commit()

def load_user_data(user_id):
    with closing(sqlite3.connect(DATABASE_FILE)) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT language, balance, account_number FROM users WHERE user_id = ?', (user_id,))
        data = cursor.fetchone()
    return data if data else ('العربية', 0, None)

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    language, balance, account_number = load_user_data(user_id)
    if account_number is None:  # إذا لم يكن هناك رقم حساب، قم بإنشائه
        account_number = generate_account_number()
        save_user_data(user_id, language, balance, account_number)
    context.bot.send_message(chat_id=update.message.chat_id, text="🎉 مرحبًا بك في بوتنا الرائع! استخدم الأمر 'help' لمساعدتك.")

def help_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("✨ القسم 1: الأوامر الأساسية", callback_data='help_section_1')],
        [InlineKeyboardButton("💰 القسم 2: نظام النقاط", callback_data='help_section_2')],
        [InlineKeyboardButton("🌍 القسم 3: إدارة اللغة", callback_data='help_section_3')],
        [InlineKeyboardButton("🎟️ القسم 4: العضويات", callback_data='help_section_4')],
        [InlineKeyboardButton("🎁 القسم 5: العروض والمكافآت", callback_data='help_section_5')],
        [InlineKeyboardButton("🔍 حسابي", callback_data='account_info')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='help_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("📚 مرحبًا! اختر قسمًا لعرض الشرح:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    help_texts = {
        'help_section_1': "📜 <b>الأوامر الأساسية:</b><br><ul><li>1️⃣ <b>تغيير اللغة:</b> اكتب '<code>تغيير اللغة</code>' لتغيير لغة البوت.</li> ... </ul>",
        'help_section_2': "📊 <b>نظام النقاط والمحفظة:</b><br><ul><li>1️⃣ <b>رصيدك:</b> اكتب '<code>رصيدي</code>' لعرض رصيدك.</li> ... </ul>",
        'help_section_3': "🌐 <b>إدارة اللغة:</b><br><ul><li>1️⃣ <b>اختيار اللغة:</b> اختر لغتك عند بدء التفاعل.</li> ... </ul>",
        'help_section_4': "💼 <b>العضويات والاشتراكات:</b><br><ul><li>1️⃣ <b>الترقية:</b> اكتب '<code>ترقية [نوع العضوية]</code>' لترقية حسابك.</li> ... </ul>",
        'help_section_5': "🎁 <b>عروض ومكافآت خاصة:</b><br><ul><li>1️⃣ <b>العروض:</b> اكتب '<code>العروض</code>' لعرض العروض الحالية المتاحة لك.</li> ... </ul>",
        'account_info': "ℹ️ <b>معلومات حسابك:</b><br>رقم حسابك هو: <code>{}</code><br>رصيدك الحالي هو: <code>{}</code><br>اللغة المستخدمة هي: <code>{}</code>"
    }
    
    help_text = help_texts.get(query.data)
    if query.data == 'account_info':
        user_id = query.from_user.id
        language, balance, account_number = load_user_data(user_id)
        help_text = help_texts['account_info'].format(account_number, balance, language)
    
    if help_text:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='help_menu')]])
        query.edit_message_text(text=help_text, parse_mode='HTML', reply_markup=reply_markup)
    elif query.data == 'help_menu':
        help_command(update, context)

def handle_commands(update: Update, context: CallbackContext) -> None:
    command = update.message.text
    user_id = update.message.from_user.id
    language, balance, account_number = load_user_data(user_id)

    try:
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
            save_user_data(user_id, language, balance, account_number)
            update.message.reply_text(f"💵 تم إيداع <b>{amount}</b> بنجاح. رصيدك الجديد هو <b>{balance}</b>.", parse_mode='HTML')
        elif command.startswith('سحب'):
            amount = float(command.split()[1])
            if amount <= balance:
                balance -= amount
                save_user_data(user_id, language, balance, account_number)
                update.message.reply_text(f"💸 تم سحب <b>{amount}</b> بنجاح. رصيدك الجديد هو <b>{balance}</b>.", parse_mode='HTML')
            else:
                update.message.reply_text("❌ رصيدك غير كافٍ لإجراء هذه العملية.")
        elif command.startswith('تحويل'):
            parts = command.split()
            amount = float(parts[1])
            recipient = parts[3]

            recipient_data = load_user_data(int(recipient))
            if recipient_data:
                recipient_balance = recipient_data[1]
                if amount <= balance:
                    balance -= amount
                    recipient_balance += amount
                    save_user_data(user_id, language, balance, account_number)
                    save_user_data(int(recipient), recipient_data[0], recipient_balance, recipient_data[2])
                    update.message.reply_text(f"➡️ تم تحويل <b>{amount}</b> إلى <b>{recipient}</b> بنجاح.", parse_mode='HTML')
                else:
                    update.message.reply_text("❌ رصيدك غير كافٍ لإجراء هذه العملية.")
            else:
                update.message.reply_text("❓ لم يتم العثور على المستخدم الذي تحاول التحويل إليه.")
        elif command == 'رصيدي':
            update.message.reply_text(f"💰 رصيدك الحالي هو: <b>{balance}</b>.", parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error processing command '{command}' for user {user_id}: {e}")
        update.message.reply_text("❗ حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى.")

def main() -> None:
    init_db()
    updater = Updater(API_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", handle_commands))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_commands))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()