import telebot
import random
import json
import os
import time
import requests
from requests.exceptions import ConnectionError
from telebot.apihelper import ApiException

API_TOKEN = '7328823780:AAGgppB9_38ParQ2mdurprSFusMM97e1LAM'
bot = telebot.TeleBot(API_TOKEN)

DB_FILE = "user_data.json"
CHALLENGE_FILE = "challenges.json"

# تحميل البيانات المخزنة إذا كانت الملفات موجودة
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

if os.path.exists(CHALLENGE_FILE):
    with open(CHALLENGE_FILE, "r") as f:
        challenges = json.load(f)
else:
    challenges = {
        "daily": ["Solve the riddle: What has keys but can't open locks?", "Guess the number between 1 and 10."],
        "weekly": ["Write a funny story using the words 'dog', 'moon', and 'robot'.", "Create a meme about programming."]
    }

# حفظ البيانات إلى الملفات
def save_user_data():
    with open(DB_FILE, "w") as f:
        json.dump(user_data, f)

def save_challenges():
    with open(CHALLENGE_FILE, "w") as f:
        json.dump(challenges, f)

# إرسال تحديات
def send_challenge(chat_id, challenge_type):
    if challenge_type in challenges:
        challenge = random.choice(challenges[challenge_type])
        try:
            bot.send_message(chat_id, f"Today's challenge is: {challenge}")
        except (ConnectionError, ApiException) as e:
            print(f"Error sending message: {e}")
            retry_send_message(chat_id, f"Today's challenge is: {challenge}")
    else:
        bot.send_message(chat_id, "No challenges available at the moment.")

# محاولة إعادة إرسال الرسائل في حالة الفشل
def retry_send_message(chat_id, text, retries=5, delay=3):
    for attempt in range(retries):
        try:
            bot.send_message(chat_id, text)
            break
        except (ConnectionError, ApiException) as e:
            print(f"Retry {attempt + 1}/{retries} failed: {e}")
            time.sleep(delay)

# أوامر البوت المختلفة
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        bot.send_message(message.chat.id, "Welcome to the Challenge Bot! Use /challenge to get a challenge.")
    except (ConnectionError, ApiException) as e:
        print(f"Error sending message: {e}")
        retry_send_message(message.chat.id, "Welcome to the Challenge Bot! Use /challenge to get a challenge.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    try:
        bot.send_message(message.chat.id, """👋 مرحبا بك في بوت التحديات والإنجازات الجماعية!

🌟 مميزات البوت:

1. تحديات يومية وأسبوعية:

للحصول على تحدي يومي، استخدم الأمر /challenge.

2. نظام النقاط:

احصل على نقاط عند إكمال التحديات بنجاح.

3. التفاعل:

تحدث معنا وأخبرنا إذا كنت قد أكملت تحديًا! استخدم عبارة مثل "التحدي مكتمل" للحصول على نقاط إضافية.
""")
    except (ConnectionError, ApiException) as e:
        print(f"Error sending message: {e}")
        retry_send_message(message.chat.id, "Error sending help message. Please try again later.")

# لعبة النكت
@bot.message_handler(commands=['joke'])
def handle_joke(message):
    jokes = [
        "لماذا لا تذهب البرمجة إلى الشاطئ؟ لأنها لا تحب الغرق في الأخطاء!",
        "ما هو الشيء الذي لا يعمل بدون خطأ؟ البرنامج المثالي!"
    ]
    bot.send_message(message.chat.id, random.choice(jokes))

# اقتباسات
@bot.message_handler(commands=['quote'])
def handle_quote(message):
    quotes = [
        "النجاح هو القدرة على الذهاب من فشل إلى فشل دون فقدان الحماس - وينستون تشرشل",
        "إذا كنت تستطيع الحلم بشيء، يمكنك تحقيقه - والت ديزني"
    ]
    bot.send_message(message.chat.id, random.choice(quotes))

# لعبة الحظ
@bot.message_handler(commands=['luck'])
def handle_luck(message):
    lucky_number = random.randint(1, 10)
    bot.send_message(message.chat.id, "اختر رقمًا بين 1 و 10، وأرسل الرقم!")

    @bot.message_handler(func=lambda msg: msg.text.isdigit())
    def guess_number(msg):
        if int(msg.text) == lucky_number:
            bot.send_message(msg.chat.id, "🎉 تهانينا! لقد ربحت.")
        else:
            bot.send_message(msg.chat.id, "حاول مرة أخرى!")

# تحديات يومية
@bot.message_handler(commands=['challenge'])
def handle_challenge(message):
    chat_id = message.chat.id
    send_challenge(chat_id, 'daily')

# لوحة المتصدرين
@bot.message_handler(commands=['leaderboard'])
def handle_leaderboard(message):
    chat_id = message.chat.id
    try:
        bot.send_message(chat_id, "Leaderboard feature is coming soon!")
    except (ConnectionError, ApiException) as e:
        print(f"Error sending message: {e}")
        retry_send_message(chat_id, "Leaderboard feature is coming soon!")

# حقائق عشوائية
@bot.message_handler(commands=['fact'])
def handle_fact(message):
    facts = [
        "هل تعلم أن النحل يمكنه التعرف على الوجوه؟",
        "القطط تحلم مثل البشر أثناء النوم!"
    ]
    bot.send_message(message.chat.id, random.choice(facts))

# مسابقة الأسئلة
@bot.message_handler(commands=['quiz'])
def handle_quiz(message):
    questions = [
        {"question": "ما هي عاصمة فرنسا؟", "answer": "باريس"},
        {"question": "ما هو أكبر كوكب في نظامنا الشمسي؟", "answer": "المشتري"}
    ]
    question = random.choice(questions)
    bot.send_message(message.chat.id, question["question"])

    @bot.message_handler(func=lambda msg: msg.text.lower() == question["answer"].lower())
    def correct_answer(msg):
        bot.send_message(msg.chat.id, "🎉 إجابة صحيحة! لقد حصلت على 10 نقاط.")

# لعبة حجر ورقة مقص
@bot.message_handler(commands=['rps'])
def handle_rps(message):
    choices = ["حجر", "ورقة", "مقص"]
    bot.send_message(message.chat.id, "اختر: حجر، ورقة، مقص؟")

    @bot.message_handler(func=lambda msg: msg.text in choices)
    def play_rps(msg):
        user_choice = msg.text
        bot_choice = random.choice(choices)
        bot.send_message(msg.chat.id, f"اخترت: {bot_choice}")
        if user_choice == bot_choice:
            bot.send_message(msg.chat.id, "إنه تعادل!")
        elif (user_choice == "حجر" and bot_choice == "مقص") or (user_choice == "ورقة" and bot_choice == "حجر") or (user_choice == "مقص" and bot_choice == "ورقة"):
            bot.send_message(msg.chat.id, "🎉 أنت الفائز!")
        else:
            bot.send_message(msg.chat.id, "البوت فاز! حظًا أوفر في المرة القادمة.")

# التعامل مع الرسائل العامة
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {'points': 0, 'completed_challenges': []}
        save_user_data()

    if "challenge completed" in message.text.lower():
        user_data[user_id]['points'] += 10
        user_data[user_id]['completed_challenges'].append(message.text)
        save_user_data()
        bot.send_message(chat_id, "Congratulations! You've earned 10 points.")

    if "thank you" in message.text.lower():
        bot.send_message(chat_id, "You're welcome! Ready for more challenges?")

bot.polling(none_stop=True)