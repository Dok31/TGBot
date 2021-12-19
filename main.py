import datetime
import time
import urllib.request
from datetime import timedelta, datetime

import requests
import schedule
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CallbackContext, CommandHandler


def start(update, context):
    '''Функция вызываемая началом с ней работы
        return 1 указывает, что дальше на сообщения от этого пользователя, должен отвечать обработчик states[1].
        До этого момента обработчиков текстовых сообщений для этого пользователя не существовало, поэтому текстовые сообщения игнорировались.'''

    update.message.reply_text("Привет! Я бот-расписание. Напишите мне свое ФИО, и я пришлю расписание!")
    context.user_data['homework'] = []
    return 1


def first_response(update, context):
    ''' Данная функция сама вызывается после написания сообщения после ввывода  функции start
    приниамет ФИО студента и сохраняет его
     context.user_data['surname']- Переменная, хранящая ФИО студента
     reply_keyboard и markup отвечают за кнопики с командами в боте'''

    context.user_data['surname'] = update.message.text
    surname_name = update.message.text
    reply_keyboard = [['/timetable'],
                      ['/settings']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("Отлично!Если хочешь посмотреть расписание нажми /timetable", reply_markup=markup)

    return ConversationHandler.END


def stop(update, context):
    ''' дает пользователю закончить опрос'''
    update.message.reply_text("Закончил опрос")
    return ConversationHandler.END


def help(update, context):
    ''' Описывает работу других команд '''
    update.message.reply_text(
        '/timetable - показывает расписание на день \n'
        '/settings - показывает настройки \n'
        '/week показывает расписание на неделю\n'
        'Если хочешь добавить дз напиши его в чат, если хочешь удалить напиши "/del_homework <номер дз>"\n'
        'Если хочешь узнать даты экзаменов зайди в /timetable и нажми /exams')


def timetable(update, context):
    ''' Принимает на вход значение ФИО ученика, составляя из его персональных данных и текущего дня ссылку. Из которой в свою очередь составялется новая ссылка с расписанием
     После ввывода рассписания предлагается ввывести расписсание уже на всю неделю, считая этот день первым.
     При отсутствии такого ученика ничего не будет выводится из рассписания '''

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

    reply_keyboard = [['/exams', '/week'],
                      ['/settings', '/help']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Если хочешь на неделю нажми на кнопку /week', reply_markup=markup)
    return str(context.user_data['id'])


def week(update, context):
    '''Выводит в чат расписание пар на неделю'''
    now = datetime.now()
    today = str(now.year) + '.' + str(now.month) + '.' + str(now.day)
    in_seven_days = datetime.now() + timedelta(7)
    in_seven_days = str(in_seven_days.year) + '.' + str(in_seven_days.month) + '.' + str(in_seven_days.day)
    api_server = ['https://ruz.hse.ru/api/schedule/student/', '&start=', '&finish=', '&lng=1']
    response = requests.get(
        api_server[0] + context.user_data['id'] + api_server[1] + today + api_server[2] + in_seven_days + api_server[3])
    json_response = response.json()
    for i in json_response:
        update.message.reply_text(
            ' '.join([i['discipline'], 'ведет', i['lecturer_title'], 'С', i['beginLesson'], 'по', i['endLesson']]))


def settings(update, context):
    reply_keyboard = [['/help', '/timetable'],
                      ['/homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Если хочешь удалить запись о домашнем задании - нажми на /homework', reply_markup=markup)


def homework(update, context):
    ''' Функция предлагает сделать выбор  из следующих функций
       При выборе /homework предлагается 2 параметра: добавить заадние или убрать выполненное. Вся база сохранена в подобие массива'''
    reply_keyboard = [['/del_homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    for i in range(len(context.user_data['homework'])):
        update.message.reply_text(str(i + 1) + ' ' + str(context.user_data['homework'][i]))
    update.message.reply_text(
        'Если хочешь добавить домашнее задание напиши его в чат, если хочешь удалить "/del_homework <номер дз>"',
        reply_markup=markup)


def add_homework(update, context):
    '''Добавляет запись о домашней работе'''
    reply_keyboard = [['/help', '/timetable'],
                      ['/homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    context.user_data['homework'].append(update.message.text)
    update.message.reply_text('Добавил ' + str(context.user_data['homework'][-1]) + ' в список домашнего задания',
                              reply_markup=markup)


def del_homework(update, context):
    '''Удаляет запись о домашней работе по номеру'''
    reply_keyboard = [['/help', '/timetable'],
                      ['/set', '/homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    del context.user_data['homework'][int(update.message.text.split(' ')[1]) - 1]
    for i in range(len(context.user_data['homework'])):
        update.message.reply_text(
            ' '.join([str(i + 1), str(context.user_data['homework'][i])]), reply_markup=markup)


def exams(update, context):
    '''Выводит в чат список ближайших экзаменов'''
    now = datetime.now()
    proverochka = 0
    today = str(now.year) + '.' + str(now.month) + '.' + str(now.day)
    in_three_mon = datetime.now() + timedelta(90)
    in_three_mon = str(in_three_mon.year) + '.' + str(in_three_mon.month) + '.' + str(in_three_mon.day)
    api_server = ['https://ruz.hse.ru/api/schedule/student/', '&start=', '&finish=', '&lng=1']
    response = requests.get(
        api_server[0] + context.user_data['id'] + api_server[1] + today + api_server[2] + in_three_mon + api_server[3])
    json_response = response.json()
    for i in json_response:
        if proverochka != 1:
            if i['kindOfWork'] == 'Экзамен Online' or i['kindOfWork'] == 'Экзамен':
                proverochka += 1
                update.message.reply_text(
                    ' '.join(
                        [i['discipline'], 'принимает', i['lecturer_title'], 'С', i['beginLesson'], 'по',
                         i['endLesson']]))


def main():
    ''' Функция является одной из главнейших частей, ибо она заставляет работать бота.
       Особенность: в Updater надо передать полученный от @BotFather токен.
       Работа: После получения диспетчера сообщений созадется отдельный обработчик сообщений типа Filters.text
       Следующий этап работы: после регистрации обработчика в диспетчере функция- она будет вызываться при получении сообщения с типом "текст", т. е. текстовых сообщений.
       Последующий этап: регистрируем обработчик в диспетчере. После чего начинается вход в диалог, с двумя обработчиками, фильтрующими текстовые сообщения.
       Функция :states={
                 Функция читает ответ на первый вопрос и задаёт второй.
               1: [MessageHandler(Filters.text, first_response, pass_user_data=True)]
                 Функция читает ответ на второй вопрос и завершает диалог.
           },
           fallbacks=[CommandHandler('stop', stop)]
       )
            Точка прерывания диалога. В данном случае — команда /stop. Зарегистрируем их в диспетчере рядом с регистрацией обработчиков текстовых сообщений. Первым параметром конструктора CommandHandler я
       # вляется название команды.'''
    updater = Updater('5037391482:AAHhRsvJ-MkFD-JUrdlQ87R55ump9Y6h9W0', use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(

        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(Filters.text, first_response, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("timetable", timetable))
    dp.add_handler(CommandHandler("week", week))
    dp.add_handler(CommandHandler("settings", settings))
    dp.add_handler(CommandHandler("exams", exams))
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
