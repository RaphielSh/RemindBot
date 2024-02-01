from dotenv import load_dotenv
import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
import os
import csv

load_dotenv()
TG_TOKEN=os.getenv("TELEGRAM_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")

bot = telebot.TeleBot(TG_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Привет!")
    if(os.path.isfile(str(user_id)+".csv")):return
    f = open(str(message.chat.id)+".csv", "w")
    f.write()
    f.close()


c1 = types.BotCommand(command='view', description='View your tasks')
c2 = types.BotCommand(command='add', description='Add new task')
c3 = types.BotCommand(command='delete', description='Delete task')
bot.set_my_commands([c1,c2,c3])


#Task operations
@bot.message_handler(commands=['view'])
def view_tasks(message):
    with open(str(message.chat.id)+".csv") as file:
        read = csv.reader(file, delimiter=',')
        for row in read:
            if row[0] == 1:
                bot.send_message(message.chat.id, "Каждый(-ую) "+row[1]+' в '+row[2]+' '+row[3])
                continue
            bot.send_message(message.chat.id, row[1]+' в '+row[2]+' '+row[3])
            

@bot.message_handler(commands=['add'])
def add_task(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    one_time = types.InlineKeyboardButton('Оповестить один раз', callback_data='one_time')
    repeat = types.InlineKeyboardButton('Повторять', callback_data='repeat')
    markup.add(one_time)
    markup.add(repeat)
    bot.send_message(message.chat.id, "Хотите сделать оповещение регулярным?", reply_markup=markup)
    
@bot.callback_query_handler(func=lambda call:True)
def set_task(callback):
    with open(str(callback.chat.id)+".csv", mode='a') as file:
        # write = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        match callback.data:
            case 'one_time':
                print()
            case 'repeat':
                print()

@bot.message_handler(commands=['delete'])
def delete_task(message):
    f = open(str(message.chat.id)+".csv", "r")
    f.close()


bot.infinity_polling()