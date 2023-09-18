# -*- coding: utf-8 -*-

import telebot
from telebot.types import *
from config.setting import *


bot = telebot.TeleBot(TOKEN_TELEGRAM)


@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, text="?")


@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = InlineKeyboardButton('Кнопка 1', callback_data='button1')
    button2 = InlineKeyboardButton('Кнопка 2', callback_data='button2')
    button3 = InlineKeyboardButton('Кнопка 3', callback_data='button3')
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


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'button1':
        bot.answer_callback_query(call.id, 'Вы выбрали кнопку 1')
    elif call.data == 'button2':
        bot.answer_callback_query(call.id, 'Вы выбрали кнопку 2')
    elif call.data == 'button3':
        bot.answer_callback_query(call.id, 'Вы выбрали кнопку 3')
    elif call.data == 'button4':
        bot.answer_callback_query(call.id, 'Вы выбрали кнопку 4')


if __name__ == "__main__":
    bot.polling(none_stop=True)
