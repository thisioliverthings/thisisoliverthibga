import telebot
import random
import json
import os

API_TOKEN = '7328823780:AAGgppB9_38ParQ2mdurprSFusMM97e1LAM'
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
        bot.send_message(chat_id, f"Today's challenge is: {challenge}")
    else:
        bot.send_message(chat_id, "No challenges available at the moment.")

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Welcome to the Challenge Bot! Use /challenge to get a challenge.")
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, """👋 مرحبا بك في بوت التحديات والإنجازات الجماعية!

🌟 مميزات البوت:

1. تحديات يومية وأسبوعية:

للحصول على تحدي يومي، استخدم الأمر /challenge.

سنقوم بإرسال تحديات متنوعة وممتعة يمكنك حلها ومشاركة إنجازاتك.



2. نظام النقاط:

احصل على نقاط عند إكمال التحديات بنجاح.

يمكنك متابعة تقدمك في لوحة المتصدرين القادمة عبر الأمر /leaderboard.



3. التفاعل:

تحدث معنا وأخبرنا إذا كنت قد أكملت تحديًا! استخدم عبارة مثل "التحدي مكتمل" للحصول على نقاط إضافية.


""")
@bot.message_handler(commands=['challenge'])
def handle_challenge(message):
    chat_id = message.chat.id
    send_challenge(chat_id, 'daily')

@bot.message_handler(commands=['leaderboard'])
def handle_leaderboard(message):
    chat_id = message.chat.id
    # Here you would implement a leaderboard display based on user performance
    bot.send_message(chat_id, "Leaderboard feature is coming soon!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {'points': 0, 'completed_challenges': []}
        save_user_data()

    if "challenge completed" in message.text.lower():
        # Simple example of adding points for completed challenges
        user_data[user_id]['points'] += 10
        user_data[user_id]['completed_challenges'].append(message.text)
        save_user_data()
        bot.send_message(chat_id, "Congratulations! You've earned 10 points.")

    if "thank you" in message.text.lower():
        bot.send_message(chat_id, "You're welcome! Ready for more challenges?")

bot.polling(none_stop=True)