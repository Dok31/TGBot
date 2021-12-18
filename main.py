import datetime
import time
import urllib.request
from datetime import timedelta, datetime

import requests
import schedule
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CallbackContext, CommandHandler


def start(update, context):
    update.message.reply_text("Привет! Я бот-расписание. Напишите мне свое ФИО, и я пришлю расписание!")
    context.user_data['homework'] = []
    return 1
    # return 1 указывает, что дальше на сообщения от этого пользователя
    # должен отвечать обработчик states[1].
    # До этого момента обработчиков текстовых сообщений
    # для этого пользователя не существовало,
    # поэтому текстовые сообщения игнорировались.


def first_response(update, context):
    # Это ответ на первый вопрос.
    # Мы можем использовать его во втором вопросе.
    context.user_data['surname'] = update.message.text
    surname_name = update.message.text
    reply_keyboard = [['/timetable'],
                      ['/settings']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("Отлично!Если хочешь посмотреть расписание нажми /timetable", reply_markup=markup)
    # update.message.reply_text(reply_markup=ReplyKeyboardRemove())
    # Следующее текстовое сообщение будет обработано
    # обработчиком states[2]
    return ConversationHandler.END


def stop(update, context):
    ''' дает пользователю закончить опрос'''
    update.message.reply_text("Закончил опрос")
    return ConversationHandler.END


def help(update, context):
    ''' описывает работу других команд '''
    update.message.reply_text('/timetable - показывает расписание на день \n/settings - показывает настройки \n'
                              '/week показывает расписание на неделю\n'
                              'Если хочешь добавить дз напиши его в чат, если хочешь удалить напиши"/del_homework <номер дз>" ')


def timetable(update, context):
    ''' '''

    update.message.reply_text('Расписание')
    api_server = ['https://ruz.hse.ru/api/search?term=', '&type=student']
    response = requests.get(api_server[0] + context.user_data['surname'] + api_server[1])
    json_response = response.json()
    id = json_response[0]['id']
    context.user_data['id'] = id
    api_server = ['https://ruz.hse.ru/api/schedule/student/', '&start=', '&finish=', '&lng=1']
    now = datetime.now()
    today = str(now.year) + '.' + str(now.month) + '.' + str(now.day)
    response = requests.get(api_server[0] + id + api_server[1] + today + api_server[2] + today + api_server[3])
    json_response = response.json()
    for i in json_response:
        update.message.reply_text(
            ' '.join([i['discipline'], 'ведет', i['lecturer_title'], 'С', i['beginLesson'], 'по', i['endLesson']]))

    reply_keyboard = [['/help'],
                      ['/week'],
                      ['/settings']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Если хочешь на неделю нажми на кнопку /week', reply_markup=markup)
    return context.user_data['id']


def week(update, context):
    now = datetime.now()
    today = str(now.year) + '.' + str(now.month) + '.' + str(now.day)
    in_seven_days = datetime.now() + timedelta(7)
    in_seven_days = str(in_seven_days.year) + '.' + str(in_seven_days.month) + '.' + str(in_seven_days.day)
    api_server = ['https://ruz.hse.ru/api/schedule/student/', '&start=', '&finish=', '&lng=1']
    response = requests.get(
        api_server[0] + context.user_data['id'] + api_server[1] + today + api_server[2] + in_seven_days + api_server[3])
    json_response = response.json()
    print(
        api_server[0] + context.user_data['id'] + api_server[1] + today + api_server[2] + in_seven_days + api_server[3])
    for i in json_response:
        update.message.reply_text(
            ' '.join([i['discipline'], 'ведет', i['lecturer_title'], 'С', i['beginLesson'], 'по', i['endLesson']]))


def settings(update, context):
    reply_keyboard = [['/help', '/timetable'],
                      ['/homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Если хочешь каждый день получать расписание - нажми на /set', reply_markup=markup)


def homework(update, context):
    reply_keyboard = [['/del_homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    for i in range(len(context.user_data['homework'])):
        update.message.reply_text(str(i + 1) + ' ' + str(context.user_data['homework'][i]))
    update.message.reply_text(
        'Если хочешь добавить домашнее задание напиши его в чат, если хочешь удалить "/del_homework <номер дз>"',
        reply_markup=markup)


def add_homework(update, context):
    reply_keyboard = [['/help', '/timetable'],
                      ['/homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    context.user_data['homework'].append(update.message.text)
    update.message.reply_text('Добавил ' + str(context.user_data['homework'][-1]) + ' в список домашнего задания',
                              reply_markup=markup)


def del_homework(update, context):
    reply_keyboard = [['/help', '/timetable'],
                      ['/set', '/homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    del context.user_data['homework'][int(update.message.text.split(' ')[1]) - 1]
    for i in range(len(context.user_data['homework'])):
        update.message.reply_text(
            ' '.join([str(i + 1), str(context.user_data['homework'][i])]), reply_markup=markup)


def main():
    # Создаём объект updater.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater('5037391482:AAHhRsvJ-MkFD-JUrdlQ87R55ump9Y6h9W0', use_context=True)
    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher
    # Создаём обработчик сообщений типа Filters.text
    # из описанной выше функции echo()
    # После регистрации обработчика в диспетчере
    # эта функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    # Регистрируем обработчик в диспетчере.
    # dp.add_handler(text_handler)

    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос
        entry_points=[CommandHandler('start', start)],
        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(Filters.text, first_response, pass_user_data=True)]
            # Функция читает ответ на второй вопрос и завершает диалог.
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)

    # Зарегистрируем их в диспетчере рядом
    # с регистрацией обработчиков текстовых сообщений.
    # Первым параметром конструктора CommandHandler я
    # вляется название команды.

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("timetable", timetable))
    dp.add_handler(CommandHandler("week", week))
    dp.add_handler(CommandHandler("settings", settings))
    dp.add_handler(CommandHandler("homework", homework, pass_user_data=True))
    dp.add_handler(CommandHandler("del_homework", del_homework, pass_user_data=True, pass_chat_data=True))
    dp.add_handler(MessageHandler(Filters.text, add_homework, pass_user_data=True))

    # Запускаем dp.add_handler(CommandHandler("student", student))
    #     dp.add_handler(CommandHandler("teacher", teacher))цикл приема и обработки сообщений.
    updater.start_polling()
    # Ждём завершения приложения.
    # когда дождались, получаем резульат
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


if __name__ == '__main__':
    main()
