# -*- coding: utf-8 -*-

import random
import string
import telebot
import requests
from telebot.types import *
from datetime import datetime
from lib.config import config, SqlDataBase


user, base = {}, {}
date_now = datetime.now()
db = config(filename='lib/config.ini', section='pg3')
bot = telebot.TeleBot(config(filename='lib/config.ini', section='tg')['token'])


def keyboard_line(key):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    if key == 'start':
        menu_button = InlineKeyboardButton('Меню', callback_data='menu')
        markup = InlineKeyboardMarkup()
        markup.row(menu_button)

    elif key == 'menu':
        setting_button = InlineKeyboardButton('Настройки', callback_data='setting')
        news_button = InlineKeyboardButton('Новости', callback_data='news')
        calendar_button = InlineKeyboardButton('Календарь', callback_data='calendar')
        support_button = InlineKeyboardButton('Помощь', callback_data='support')
        markup = InlineKeyboardMarkup()
        markup.row(setting_button, news_button, calendar_button)
        markup.row(support_button)

    elif key == 'band':
        left_button = InlineKeyboardButton('<<<', callback_data='left')
        ok_button = InlineKeyboardButton('OK', callback_data='ok_call')
        right_button = InlineKeyboardButton('>>>', callback_data='right')
        back_menu_button = InlineKeyboardButton('Меню', callback_data='menu')
        markup = InlineKeyboardMarkup()
        markup.row(left_button, ok_button, right_button)
        markup.row(back_menu_button)
    return markup


def get_img(url_img):
    letters = string.ascii_lowercase
    new_name = ''.join(random.choice(letters) for i in range(5)) + '.png'
    img_url = requests.get(url_img).content
    with open(new_name, 'wb') as handler:
        handler.write(img_url)
    return new_name


def start_chat_tg(message):
    sql = f'''SELECT user_id FROM users WHERE user_id = {message.from_user.id}'''
    if not SqlDataBase(db, sql).raw():
        user['user_id'] = str(message.from_user.id)
        user['date'] = f"'{str(date_now)}'"
        user['username'] = f"'{str(message.from_user.username)}'"
        user['first_name'] = f"'{str(message.from_user.first_name)}'"
        user['language_code'] = f"'{str(message.from_user.language_code)}'"
        base['users'] = user
        SqlDataBase(base=db, request=base).insert()
    bot.delete_message(message.chat.id, message.message_id)
    base.clear()


def new_event(message, event='some_event'):
    # user['date'] = f"'{str(date_now)}'"
    # user['user_id'] = str(message.id)
    # user['action'] = f"'{event}'"
    # base['action_bot'] = user
    # SqlDataBase(base=db, request=base).insert()
    pass


@bot.message_handler(commands=['support'])
def support(message):
    bot.send_message(message.chat.id, text="support", reply_markup=keyboard_line('band'))
    new_event(message.chat, event='support_event')


@bot.message_handler(commands=['setting'])
def setting(message):
    bot.send_message(message.chat.id, text="setting", reply_markup=keyboard_line('band'))
    new_event(message.chat, event='setting_event')


@bot.message_handler(commands=['news'])
def news(message):
    sql = '''SELECT * FROM news ORDER BY date DESC LIMIT 1'''
    result = SqlDataBase(base=db, request=sql).raw()[0]
    _message = result['title'] + '\n' + result['description']
    img = get_img(result['img_url'])
    bot.send_photo(message.chat.id,
                   photo=open(img, 'rb'),
                   caption=_message,
                   reply_markup=keyboard_line('band'))
    new_event(message.chat, event='news_event')
    os.remove(img)


@bot.message_handler(commands=['calendar'])
def calendar(message):
    bot.send_message(message.chat.id, text="calendar", reply_markup=keyboard_line('band'))
    new_event(message.chat, event='calendar_event')


@bot.message_handler(commands=['menu'])
def menu(message):
    bot.send_message(message.chat.id,
                     text="Меню",
                     reply_markup=keyboard_line('menu'))
    new_event(message.chat, event='main_menu_event')


@bot.message_handler(commands=['start'])
def start(message):
    start_chat_tg(message)
    bot.send_message(message.chat.id,
                     text=f"Привет, {message.from_user.first_name}!\n"
                          "Я маленький помогатор в Телеграмме\n",
                     reply_markup=keyboard_line('start'))
    new_event(message.from_user, event='start_chat_tg')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

    if call.data == 'menu':
        bot.answer_callback_query(call.id, 'Меню')
        menu(call.message)

    elif call.data == 'support':
        bot.answer_callback_query(call.id, 'Поддержка')
        support(call.message)

    elif call.data == 'news':
        bot.answer_callback_query(call.id, 'Новости')
        news(call.message)

    elif call.data == 'setting':
        bot.answer_callback_query(call.id, 'Настройки')
        setting(call.message)

    elif call.data == 'calendar':
        bot.answer_callback_query(call.id, 'Календарь')
        calendar(call.message)

    elif call.data == 'left':
        pass
    elif call.data == 'right':
        pass
    elif call.data == 'ok_call':
        pass

    new_event(call.message.chat, event='init_callback_menu')


if __name__ == "__main__":
    bot.polling(none_stop=True)
