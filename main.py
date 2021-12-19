import datetime
import time
import urllib.request
from datetime import timedelta, datetime

import requests
import schedule
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CallbackContext, CommandHandler


def start(update, context):
    ''' Данная функция запускается автоматически при первом  запуске или при вводе коаманды /start
     context.user_data[homework] - массив  сохраняющий ломашнее занятие
     Отправляет сообщенеие для ученика, чтобы он активировал следющую функциую  '''
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
    ''' Данная функция позволяет закакнчивать некоторые функции '''
    update.message.reply_text("Закончил опрос")
    return ConversationHandler.END


def help(update, context):
    ''' Чтобы заработала нужно ввести команду /help
    Данная команда выводит список остальных функций '''
    update.message.reply_text(
        '/timetable - показывает расписание на день \n'
        '/settings - показывает настройки \n'
        '/week показывает расписание на неделю\n'
        'Если хочешь добавить дз напиши его в чат, если хочешь удалить напиши "/del_homework <номер дз>"\n'
        'Если хочешь узнать даты экзаменов зайди в /timetable и нажми /exams')


def timetable(update, context, *args):
    ''' Данная функция запускается при активации команды /timetable
    Выводит расписание на сегоднешний день, если есть
    api_server - переменная для создания  request запроса
    response -  перемнная, содержащая json файл, в котором записана инофрмация о ученике
    json_response - открывает файл с расширением  json
    context.user_data['id'] - добавляет данные о пользователя
    now - время сегодная
    today конвертация сегодняшнего now  формат str
    response - json файл, содержащий в себе информацию о расписании
    reply_keyboard и markup ответственен за работу и отображение <кнпок> в боте'''

    api_server = ['https://ruz.hse.ru/api/search?term=', '&type=student']
    print(args)
    if args:
        response = requests.get(api_server[0] + str(args[0]) + api_server[1])
    else:
        update.message.reply_text('Расписание')
        response = requests.get(api_server[0] + context.user_data['surname'] + api_server[1])
    json_response = response.json()

    id = json_response[0]['id']
    if args:
        return id
    context.user_data['id'] = id
    api_server = ['https://ruz.hse.ru/api/schedule/student/', '&start=', '&finish=', '&lng=1']
    now = datetime.now()
    today = str(now.year) + '.' + str(now.month) + '.' + str(now.day)
    response = requests.get(api_server[0] + id + api_server[1] + today + api_server[2] + today + api_server[3])
    json_response = response.json()
    if not args:
        if not json_response:
            update.message.reply_text('СЕГОДНЯ ПАР НЕТ!')
        for i in json_response:
            update.message.reply_text(
                ' '.join([i['discipline'], 'ведет', i['lecturer_title'], 'С', i['beginLesson'], 'по', i['endLesson']]))

        reply_keyboard = [['/exams', '/week'],
                          ['/settings', '/help']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text('Если хочешь на неделю нажми на кнопку /week', reply_markup=markup)
    return str(context.user_data['id'])


def week(update, context):
    ''' Данная функция запускается при активации команды /week
    Выводит расписание на на 7  дней, включая этот день
    api_server - переменная для создания  request запроса
    response -  перемнная, содержащая json файл, в котором записана инофрмация о ученике
    json_response - открывает файл с расширением  json
    context.user_data['id'] - добавляет данные о пользователя
    now - время сегодная
    today конвертация сегодняшнего now  формат str
    response - json файл, содержащий в себе информацию о расписании'''
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
            ' '.join(['В', i['dayOfWeekString'],  i['discipline'], 'ведет', i['lecturer_title'], 'С', i['beginLesson'], 'по', i['endLesson'], 'ссылка:', i['url1']]))

def settings(update, context):
    ''' Данная функция срабатывает при активации команды /settings
    reply_keyboard и markup - отвечают за отображение кнопок, для быстрого набора команд '''
    reply_keyboard = [['/help', '/timetable'],
                      ['/homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Если хочешь удалить запись о домашнем задании - нажми на /homework', reply_markup=markup)


def homework(update, context):
    '''Данная функция срабатывает при активации /homework
    reply_keyboard и markup- показывают какие команды будут доступны
    цикл отвечает за отправление в чат всех записанных домашних заданий'''
    reply_keyboard = [['/del_homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    for i in range(len(context.user_data['homework'])):
        update.message.reply_text(str(i + 1) + ' ' + str(context.user_data['homework'][i]))
    update.message.reply_text(
        'Если хочешь добавить домашнее задание напиши его в чат, если хочешь удалить "/del_homework <номер дз>"',
        reply_markup=markup)


def add_homework(update, context):
    '''Функция активируется при вводе текста
    reply_keyboard и markup - показывает какая команда будет доступнаи позволяет
    context.user_data - добавляет дз в массив, ключем которого является 'homework'
    update.message.reply_text - выводит сообщение об успешном добавлениии дз'''
    reply_keyboard = [['/help', '/timetable'],
                      ['/homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    context.user_data['homework'].append(update.message.text)
    update.message.reply_text('Добавил ' + str(context.user_data['homework'][-1]) + ' в список домашнего задания',
                              reply_markup=markup)


def del_homework(update, context):
    '''Функция активируется при активации /del_homework, она удаляет запись о домашнем задании по номеру
    цикл выводит оставшиеся задания
    reply_keyboard и markup - показывают какие команды будут доступны
    '''
    reply_keyboard = [['/help', '/timetable'],
                      ['/set', '/homework']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    try:
        del context.user_data['homework'][int(update.message.text.split(' ')[1]) - 1]
    except Exception:
        update.message.reply_text('Что ты делаешь')
    for i in range(len(context.user_data['homework'])):
        update.message.reply_text(
            ' '.join([str(i + 1), str(context.user_data['homework'][i])]), reply_markup=markup)




def exams(update, context):
    '''Функция активируется при активации /exem. Её функция заключается в том, чтобы показать ближайшие экзамены
    now- время сегодня
    today- сегодняшная дата
    in_three_mon -  перемнная требуемая для создания request запроса, содержит в себе дату, котрая наступит через 3 месяца
    api_server - перемнная требуемая для создания request запроса

    '''
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

        if i['kindOfWork'] == 'Экзамен Online' or i['kindOfWork'] == 'Экзамен':
            proverochka += 1
            update.message.reply_text(
                ' '.join(
                    [i['discipline'], 'принимает', i['lecturer_title'], 'С', i['beginLesson'], 'по',
                     i['endLesson']]))

def test1(name):
    return timetable(None, None, name)


def main():
    ''' функция main отвественна за работу бота
    updater - переменная имеющая ссылку на бота
    entry_points - функция ответсвенная за начало и работу функции
    updater - экземпляр класса Updater, ответственный за полученеи сообщений и регулирование работы диспечеров
    dp - диспечер, ответственный за вызов функций в зависимости от полученных сообщений
    '''
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

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

