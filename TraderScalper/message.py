import telebot
from conf import telebot_token, chat_ids
import _thread


bot = telebot.TeleBot(telebot_token, parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, message.chat.id)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, 'buy')

def send(message):
    for c_id in chat_ids:
        bot.send_message(c_id, message)

def start():
    bot.polling()

def init():
    _thread.start_new_thread(start, () )

