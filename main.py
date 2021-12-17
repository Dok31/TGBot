import requests
import datetime
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove

import urllib.request
import time
import schedule

# Напишем соответствующие функции.
# Их сигнатура и поведение аналогичны обработчикам текстовых сообщений. def start(update, context):
def start(update, context):
    update.message.reply_text("Привет! Я бот-расписание. Напишите мне свое ФИО, и я пришлю расписание!")
    # Число-ключ в словаре states —
    # втором параметре ConversationHandler'а.
    return 1
    # Оно указывает, что дальше на сообщения от этого пользователя
    # должен отвечать обработчик states[1].
    # До этого момента обработчиков текстовых сообщений
    # для этого пользователя не существовало,
    # поэтому текстовые сообщения игнорировались.

def first_response(update, context):
    # Это ответ на первый вопрос.
    # Мы можем использовать его во втором вопросе.
    context.user_data['surname'] = update.message.text
    surname_name = update.message.text
    print(surname_name)
    print(surname_name)
    reply_keyboard = [['/timetable'],
                      ['/settings']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("Отлично!Если хочешь посмотреть расписание нажми tametable", reply_markup=markup)
    # update.message.reply_text(reply_markup=ReplyKeyboardRemove())
    # Следующее текстовое сообщение будет обработано
    # обработчиком states[2]

    return ConversationHandler.END



def second_response(update, context):
    # Ответ на второй вопрос.
    # Мы можем его сохранить в базе данных или переслать куда-либо.
    weather = update.message.text
    print(weather)
    print(weather)
    print(weather)


    update.message.reply_text("Спасибо за участие в опросе! Всего доброго!")
    return ConversationHandler.END
    # Константа, означающая конец диалога.
    # Все обработчики из states и fallbacks становятся неактивными.



def stop(update, context):
    ''' дает пользователю закончить опрос'''
    update.message.reply_text("Закончил опрос")
    return ConversationHandler.END


def help(update, context):
    ''' описывает работу других команд '''
    update.message.reply_text("/timetable - показывает... \n/settings - показывает настройки  ")

def timetable(update, context):
    ''' Сперва заходин на сайт руза
    потом вводит данные о вас
    и накронец выводит расписание на сегодняшний день с сайта'''
    update.message.reply_text('Расписание')
    api_server = ['https://ruz.hse.ru/api/search?term=', '&type=student']
    response = requests.get(api_server[0] + context.user_data['surname'] + api_server[1])
    json_response = response.json()
    id = json_response[0]['id']
    print(id)
    api_server = ['https://ruz.hse.ru/api/schedule/student/', '&start=', '&finish=', '&lng=1']
    now = datetime.datetime.now()
    today = str(now.year) + '.' + str(now.month) + '.' + str(now.day)
    response = requests.get(api_server[0] + id + api_server[1] + today+api_server[2] + today + api_server[3])
    print(api_server[0] + id + api_server[1] + today+api_server[2] + today + api_server[3])
    json_response = response.json()
    print(json_response)
    for i in json_response:
        update.message.reply_text(' '.join([i['discipline'],'ведет',i['lecturer_title'] ,'С',i['beginLesson'],'по', i['endLesson']]))




    reply_keyboard = [['/help'],
                      ['/week'],
                      ['/settings']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Если хочешь на неделю нажми на кнопку', reply_markup=markup)

def week(update, context):
    pass


def settings(update, context):
    reply_keyboard = [['/help'],
                      ['/timetable'],
                      ['/settings']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Настройки', reply_markup=markup)


# Определяем функцию-обработчик сообщений.
# У неё два параметра, сам бот и класс updater, принявший сообщение.
def echo(update, context):
    reply_keyboard = [['/help'],
                      ['/timetable'],
                      ['/settings']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    # У объекта класса Updater есть поле message,
    # являющееся объектом сообщения.
    # У message есть поле text, содержащее текст полученного сообщения,
    # а также метод reply_text(str),
    # отсылающий ответ пользователю, от которого получено сообщение.
    update.message.reply_text(update.message.text, reply_markup=markup)


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
    text_handler = MessageHandler(Filters.text, echo)
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
            1: [MessageHandler(Filters.text, first_response, pass_user_data = True)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(Filters.text, second_response, pass_user_data=True)]},
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


    # Запускаем dp.add_handler(CommandHandler("student", student))
    #     dp.add_handler(CommandHandler("teacher", teacher))цикл приема и обработки сообщений.
    updater.start_polling()
    # Ждём завершения приложения.
    # когда дождались, получаем резульат
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


if __name__ == '__main__':
    main()

