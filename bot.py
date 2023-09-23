# -*- coding: utf-8 -*-

import telebot
from telebot.types import *
from datetime import datetime
from function.parser import *
from lib.config import config, SqlDataBase


user, base = {}, {}
today = datetime.now()
db = config(filename='lib/config.ini', section='pg3')
bot = telebot.TeleBot(config(filename='lib/config.ini', section='tg')['token'])


def new_event(message, event='some event'):
    user['date'] = f"'{str(today)}'"
    user['user_id'] = str(message.from_user.id)
    user['action'] = f"'{event}'"
    base['action_bot'] = user
    SqlDataBase(base=db, request=base).insert()


@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, text="?")
    new_event(message, event='main_menu_event')


@bot.message_handler(commands=['start', 'menu'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = InlineKeyboardButton('Настройки', callback_data='button1')
    button2 = InlineKeyboardButton('Последние новости', callback_data='button2')
    button3 = InlineKeyboardButton('Календарь', callback_data='button3')
    button4 = InlineKeyboardButton('Кнопка 4', callback_data='button4')

    markup = InlineKeyboardMarkup()
    markup.row(button1)
    markup.row(button2)
    markup.row(button3)
    markup.row(button4)

    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}!\n"
                          "Чем могу помочь?".format(message.from_user),
                     reply_markup=markup)

    sql = f'''SELECT user_id FROM users WHERE user_id = {message.from_user.id}'''
    if not SqlDataBase(db, sql).raw():
        user['user_id'] = str(message.from_user.id)
        user['date'] = f"'{str(today)}'"  # .replace(' ', '_')
        user['username'] = f"'{str(message.from_user.username)}'"
        user['first_name'] = f"'{str(message.from_user.first_name)}'"
        user['language_code'] = f"'{str(message.from_user.language_code)}'"
        base['users'] = user
        SqlDataBase(base=db, request=base).insert()
    base.clear()
    new_event(message, event='main_menu_event')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'button1':
        bot.answer_callback_query(call.id, 'Вы выбрали кнопку 1')
        new_event(call, event='setting_button')
    elif call.data == 'button2':
        bot.answer_callback_query(call.id, 'Вы выбрали кнопку 2')
        new_event(call, event='news_button')
    elif call.data == 'button3':
        bot.answer_callback_query(call.id, 'Вы выбрали кнопку 3')
        new_event(call, event='calendar_button')
    elif call.data == 'button4':
        bot.answer_callback_query(call.id, 'Вы выбрали кнопку 4')
        new_event(call, event='button_4')


if __name__ == "__main__":
    bot.polling(none_stop=True)
