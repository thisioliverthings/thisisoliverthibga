import telebot
import random
import re
import json
from nltk import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
import os
import nltk
nltk.download('vader_lexicon')
import nltk
nltk.download('punkt_tab')
API_TOKEN = '7328823780:AAGgppB9_38ParQ2mdurprSFusMM97e1LAM'
bot = telebot.TeleBot(API_TOKEN)

DB_FILE = "user_data.json"
LEARNED_DATA_FILE = "learned_data.json"

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

if os.path.exists(LEARNED_DATA_FILE):
    with open(LEARNED_DATA_FILE, "r") as f:
        learned_data = json.load(f)
else:
    learned_data = {}

responses = {
    'default': ["I’m not sure how to respond to that. Can you clarify?"],
    'thanks': ["You’re welcome! Anything else I can help with?"],
    'greetings': ["Hello! How can I assist you today?", "Hi there! What’s up?"],
    'math': ["The result is"],
    'name_known': ["Hey {name}, nice to see you again!"],
    'name_unknown': ["I don’t know your name yet. What is it?"],
    'age_known_just_now': ["Got it! You’re {age} years old."],
    'age_known': ["I remember, you’re {age} years old."],
    'age_unknown': ["I don’t know your age yet. How old are you?"]
}

def save_user_data():
    with open(DB_FILE, "w") as f:
        json.dump(user_data, f)

def save_learned_data():
    with open(LEARNED_DATA_FILE, "w") as f:
        json.dump(learned_data, f)

def analyze_sentiment_vader(text):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    
    if sentiment['compound'] > 0.5:
        return "It sounds like you're feeling really good!"
    elif 0 < sentiment['compound'] <= 0.5:
        return "It seems like you're in a positive mood."
    elif sentiment['compound'] < -0.5:
        return "It seems like you're feeling quite down."
    elif -0.5 <= sentiment['compound'] < 0:
        return "It looks like you're a bit down."
    else:
        return None

def evaluate_expression(expression):
    try:
        result = eval(expression)
        return result
    except Exception:
        return random.choice(responses['default'])

def learn_from_conversation_v2(user_input):
    new_words = word_tokenize(user_input)
    for word in new_words:
        if word not in learned_data:
            learned_data[word] = {"count": 1, "contexts": [user_input]}
        else:
            learned_data[word]["count"] += 1
            learned_data[word]["contexts"].append(user_input)
    save_learned_data()

def save_conversation(user_id, user_input):
    if 'conversation_history' not in user_data[user_id]:
        user_data[user_id]['conversation_history'] = []
    user_data[user_id]['conversation_history'].append(user_input)
    save_user_data()

def check_things(user_input, user_id):
    user_input = user_input.lower()
    if user_id not in user_data:
        user_data[user_id] = {}
    
    save_conversation(user_id, user_input)
    
    responses_list = []
    sentiment_response = analyze_sentiment_vader(user_input)
    
    name_match = re.search(r'\bmy\s*name\s*is\s*(\w+)\b', user_input, re.IGNORECASE)
    if name_match:
        user_data[user_id]['name'] = name_match.group(1)
        save_user_data()
        responses_list.append(f"Nice to meet you, {user_data[user_id]['name']}!")
    
    name_related_pattern = r"\b(?:what\s+is\s+my\s+name|my\s+name\s+is\s+what|who\s+am\s+i)\b"
    if re.search(name_related_pattern, user_input):
        if 'name' in user_data[user_id]:
            name = user_data[user_id]['name']
            responses_list.append(f"Your name is {name}, right?")
        else:
            responses_list.append("I don’t know your name yet. What is it?")
    
    age_match = re.search(r'\bi\s*m\s*(\d{1,2})\s*years?\s*old\b', user_input, re.IGNORECASE)
    if age_match:
        user_data[user_id]['age'] = int(age_match.group(1))
        save_user_data()
        responses_list.append(f"Got it, you’re {user_data[user_id]['age']} years old!")
    
    if re.search(r'\bhow\s+old\s+am\s+i\b', user_input, re.IGNORECASE):
        if 'age' in user_data[user_id]:
            age = user_data[user_id]['age']
            responses_list.append(f"You are {age} years old!")
        else:
            responses_list.append("I don’t know your age yet. Can you tell me how old you are?")
    
    numscatcher = r"\b\d+(?:\.\d+)?(?:[\+\-\*/]\d+(?:\.\d+)?)*\b"
    math_expressions = re.findall(numscatcher, user_input)
    if math_expressions:
        results = [evaluate_expression(expr) for expr in math_expressions]
        responses_list.append(f"The result is: {', '.join(map(str, results))}")
    
    learn_from_conversation_v2(user_input)
    
    if re.search(r'\b(thank|thanks|thank you)\b', user_input, re.IGNORECASE):
        responses_list.append(random.choice(responses['thanks']))
    elif re.search(r'\bhello|hi\b', user_input, re.IGNORECASE):
        responses_list.append(random.choice(responses['greetings']))
    else:
        for key in responses:
            if re.search(key, user_input, re.IGNORECASE):
                responses_list.append(random.choice(responses[key]))
    
    if not responses_list:
        responses_list.append(random.choice(responses['default']))
    
    if sentiment_response:
        responses_list.append(sentiment_response)
    
    return " ".join(responses_list)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    user_input = message.text
    response = check_things(user_input, user_id)
    bot.send_message(message.chat.id, response)

bot.polling(none_stop=True)