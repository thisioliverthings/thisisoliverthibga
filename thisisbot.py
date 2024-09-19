import telebot
import random
import json
import os
import time
import requests
from requests.exceptions import ConnectionError
from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

API_TOKEN = 'YOUR_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

DB_FILE = "user_data.json"
CHALLENGE_FILE = "challenges.json"

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

def save_user_data():
    with open(DB_FILE, "w") as f:
        json.dump(user_data, f)

def save_challenges():
    with open(CHALLENGE_FILE, "w") as f:
        json.dump(challenges, f)

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

def retry_send_message(chat_id, text, retries=5, delay=3):
    """Attempt to resend the message in case of failure."""
    for attempt in range(retries):
        try:
            bot.send_message(chat_id, text)
            break
        except (ConnectionError, ApiException) as e:
            print(f"Retry {attempt + 1}/{retries} failed: {e}")
            time.sleep(delay)

@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        bot.send_message(message.chat.id, "Welcome to the Challenge Bot! Use /challenge to get a challenge.")
    except (ConnectionError, ApiException) as e:
        print(f"Error sending message: {e}")
        retry_send_message(message.chat.id, "Welcome to the Challenge Bot! Use /challenge to get a challenge.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="المالك للإبلاغ عن مشكلة", url="https://t.me/oliceer")
    keyboard.add(button)
    
    try:
        bot.send_message(message.chat.id, 
                         """**🔹 مرحبا بك في بوت التحديات!**

**🎯 الميزات:**

**1. تحديات يومية وأسبوعية:**  
استخدم `/challenge` للحصول على تحديات ممتعة.

**2. نظام النقاط:**  
اجمع النقاط بإكمال التحديات وتابع تقدمك عبر `/leaderboard`.

**3. التفاعل:**  
- استخدم "challenge completed" للحصول على نقاط إضافية.  
- استخدم "thank you" للرد على الشكر.

**4. ألعاب وترفيه:**  
- **نكتة:** `/joke`  
- **اقتباس:** `/quote`  
- **حظ:** `/luck`  
- **ألغاز:** `/quiz`  
- **حجر، ورقة، مقص:** `/rps`

**5. حقائق ممتعة:**  
- `/fact`

**📘 لمزيد من المعلومات، استخدم `/help`.**

**استمتع بالتحديات والألعاب!**""",
                         parse_mode='Markdown',
                         reply_markup=keyboard)
    except (ConnectionError, ApiException) as e:
        print(f"Error sending message: {e}")
        retry_send_message(message.chat.id, 
                           """**🔹 مرحبا بك في بوت التحديات!**

**🎯 الميزات:**

**1. تحديات يومية وأسبوعية:**  
استخدم `/challenge` للحصول على تحديات ممتعة.

**2. نظام النقاط:**  
اجمع النقاط بإكمال التحديات وتابع تقدمك عبر `/leaderboard`.

**3. التفاعل:**  
- استخدم "challenge completed" للحصول على نقاط إضافية.  
- استخدم "thank you" للرد على الشكر.

**4. ألعاب وترفيه:**  
- **نكتة:** `/joke`  
- **اقتباس:** `/quote`  
- **حظ:** `/luck`  
- **ألغاز:** `/quiz`  
- **حجر، ورقة، مقص:** `/rps`

**5. حقائق ممتعة:**  
- `/fact`

**📘 لمزيد من المعلومات، استخدم `/help`.**

**استمتع بالتحديات والألعاب!**""",
                           reply_markup=keyboard)

@bot.message_handler(commands=['challenge'])
def handle_challenge(message):
    chat_id = message.chat.id
    send_challenge(chat_id, 'daily')

@bot.message_handler(commands=['leaderboard'])
def handle_leaderboard(message):
    chat_id = message.chat.id
    try:
        bot.send_message(chat_id, "Leaderboard feature is coming soon!")
    except (ConnectionError, ApiException) as e:
        print(f"Error sending message: {e}")
        retry_send_message(chat_id, "Leaderboard feature is coming soon!")

@bot.message_handler(commands=['joke'])
def handle_joke(message):
    jokes = [
        "لماذا لا تذهب البرمجة إلى الشاطئ؟ لأنها لا تحب الغرق في الأخطاء!",
        "ما هو الشيء الذي لا يعمل بدون خطأ؟ البرنامج المثالي!"
    ]
    bot.send_message(message.chat.id, random.choice(jokes))

@bot.message_handler(commands=['quote'])
def handle_quote(message):
    quotes = [
        "النجاح هو القدرة على الذهاب من فشل إلى فشل دون فقدان الحماس - وينستون تشرشل",
        "إذا كنت تستطيع الحلم بشيء، يمكنك تحقيقه - والت ديزني"
    ]
    bot.send_message(message.chat.id, random.choice(quotes))

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

@bot.message_handler(commands=['fact'])
def handle_fact(message):
    facts = [
        "هل تعلم أن النحل يمكنه التعرف على الوجوه؟",
        "القطط تحلم مثل البشر أثناء النوم!"
    ]
    bot.send_message(message.chat.id, random.choice(facts))

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

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_text = message.text.strip().lower()

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

            response_message = "🎉 إجابة صحيحة! لقد حصلت على 10 نقاط."
        else:
            response_message = "الإجابة غير صحيحة. حاول مرة أخرى!"

        # إرسال استجابة للإجابة
        try:
            bot.send_message(chat_id, response_message)
        except (ConnectionError, ApiException) as e:
            print(f"Error sending message: {e}")
            retry_send_message(chat_id, response_message)
    
    # التعامل مع العبارات المتعلقة بإكمال التحديات
    elif "challenge completed" in user_text:
        if user_data[user_id]['completed_challenges']:
            user_data[user_id]['points'] += 10
            save_user_data()
            response_message = "🎉 تهانينا! لقد حصلت على 10 نقاط إضافية."
        else:
            response_message = "لم تقم بإكمال أي تحديات بعد."

        try:
            bot.send_message(chat_id, response_message)
        except (ConnectionError, ApiException) as e:
            print(f"Error sending message: {e}")
            retry_send_message(chat_id, response_message)

    # تعامل مع عبارات شكر
    elif "شكرا" in user_text :
        response_message = "على الرحب والسعة! هل ترغب في المزيد من التحديات?"
        try:
            bot.send_message(chat_id, response_message)
        except (ConnectionError, ApiException) as e:
            print(f"Error sending message: {e}")
            retry_send_message(chat_id, response_message)

    # توفير رسالة افتراضية لجميع الرسائل غير المعروفة
    else:
        response_message = "آسف، لم أفهم طلبك. يرجى استخدام الأوامر المتاحة مثل /challenge للحصول على التحديات."
        keyboard = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text="المطور للإبلاغ عن مشكلة", url="https://t.me/oliceer")
        keyboard.add(button)
        
        try:
            bot.send_message(chat_id, response_message, reply_markup=keyboard)
        except (ConnectionError, ApiException) as e:
            print(f"Error sending message: {e}")
            retry_send_message(chat_id, response_message)

bot.polling()
