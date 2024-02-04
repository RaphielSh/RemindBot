from dotenv import load_dotenv
import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove, CallbackQuery
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import os
import re
import csv
import pandas as pd

load_dotenv()
TG_TOKEN=os.getenv("TELEGRAM_TOKEN")
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_CB=CallbackData("calendar_1", "action", "year", "month", "day")
bot = telebot.TeleBot(TG_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Привет!")
    if(os.path.isfile(str(user_id)+".csv")):return
    f = open(str(message.chat.id)+".csv", "w")
    f.write("D,Date,Time,TODO\n")
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
            if not row[0] or row[1]=='Date':continue
            bot.send_message(message.chat.id, row[1]+' в '+row[2]+' '+row[3])


@bot.message_handler(commands=['add'])
def set_task(message):
    now = datetime.datetime.now()  # Get the current date
    bot.send_message(
        message.from_user.id,
        "Выберите дату",
        reply_markup=calendar.create_calendar(
            name=calendar_CB.prefix,
            year=now.year,
            month=now.month,
        ),
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_CB.prefix))
def add_one_time(call: CallbackQuery):
    name, action, year, month, day = call.data.split(calendar_CB.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    match action:
        case 'DAY':
            task_date = date.strftime('%d.%m.%Y')
            #Write new row in csv
            with open(str(call.from_user.id)+'.csv', mode='a') as file:
                write = csv.writer(file, delimiter=',' , quotechar=' ', quoting=csv.QUOTE_NONE)
                write.writerow(['ND',task_date,'TIME','TASK'])

            msg = bot.send_message(
                chat_id=call.from_user.id,
                text=f"You have chosen {task_date}. В какое время нужно прислать напоминание?",
                reply_markup=ReplyKeyboardRemove(),
            )
            bot.register_next_step_handler(msg, set_time)
        case 'CANCEL':
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"Отмена",
                reply_markup=ReplyKeyboardRemove(),
            )

#Set time for new row
def set_time(message):
    file_name = str(message.chat.id)+'.csv'
    with open(file_name, mode='r+') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith('ND'):
                lines[i] = line.replace('TIME',message.text)
        file.seek(0)
        file.writelines(lines)
    file.close()
    msg = bot.send_message(message.chat.id, "О чем напомнить?")
    bot.register_next_step_handler(msg, set_task_name)

#Set task for new row
def set_task_name(message):
    file_name = str(message.chat.id)+'.csv'
    with open(file_name, mode='r+') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith('ND'):
                lines[i] = line.replace('TASK', message.text).replace('ND', 'D')
                # lines[i] = line.replace('ND', 'D')
        file.seek(0)
        file.writelines(lines)
    file.close()

@bot.message_handler(commands=['delete'])
def delete_task(message):
    f = open(str(message.chat.id)+".csv", "r")
    f.close()


bot.infinity_polling()