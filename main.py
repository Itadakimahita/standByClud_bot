import telebot
from telebot import types
import random
import datetime

import os
from dotenv import load_dotenv

load_dotenv()

# BOT TOKEN from .env
TOKEN = os.getenv('TOKEN')

# Initialize the bot
bot = telebot.TeleBot(TOKEN)


#Telegram id of admin from .env
OWNER_USER_ID = int(os.getenv('OWNER_USER_ID'))


# Dictionary to keep track of registered users
# Here u can connect this with db
registered_users = {}


def get_names_from_dict(data):
    arr = []
    index = 1
    for i in data.keys():
        arr.append(f'{index}. ' + data[i]['name'])
        index += 1
    return arr


def create_panel():
    markup = types.InlineKeyboardMarkup()

    # Add buttons for each command
    show_all_button = types.InlineKeyboardButton("Весь список", callback_data='show_all')
    random_30_button = types.InlineKeyboardButton("Рандомные 30", callback_data='random_30')
    reset_button = types.InlineKeyboardButton("Обновить список", callback_data='reset')

    markup.row(show_all_button, random_30_button)
    markup.row(reset_button)

    return markup


def is_bot_working_now():
    current_time = datetime.datetime.now().time()
    current_day = datetime.datetime.today().weekday()

    # Check if the current time is between 6 pm on Friday and 6 pm on Saturday
    return (current_day == 4 and datetime.time(18, 0) <= current_time <= datetime.time(23, 59, 59)) or \
           (current_day == 5 and datetime.time(0, 0) <= current_time <= datetime.time(18, 0))



@bot.callback_query_handler(func=lambda call: True)
def handle_inline_buttons(call):
    user_id = call.from_user.id

    if call.data == 'show_all' and user_id == OWNER_USER_ID:
        handle_show_all(call.message)
    elif call.data == 'random_30' and user_id == OWNER_USER_ID:
        handle_random_30(call.message)
    elif call.data == 'reset' and user_id == OWNER_USER_ID:
        handle_reset(call.message)


def handle_show_all(message):
    bot.send_message(message.chat.id, "Весь список:\n" + "\n".join(get_names_from_dict(registered_users)))


def handle_random_30(message):
    random_items = random.sample(get_names_from_dict(registered_users),
                                 min(30, len(get_names_from_dict(registered_users))))
    bot.send_message(message.chat.id, "Случайные 30:\n" + "\n".join(random_items))


def handle_reset(message):
    registered_users.clear()
    bot.send_message(message.chat.id, "Список был очищен")


# Handler for the /start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id


    print(user_id)
    print(OWNER_USER_ID)

    if user_id == OWNER_USER_ID:
        bot.send_message(user_id, "Здравствуйте! Вы зашли от лица админа, выберите функцию:", reply_markup=create_panel())

    # elif not is_bot_working_now():
    #     bot.send_message(user_id, "Извините, бот сейчас не работает. Попробуйте снова в пятницу с 18:00 до субботы 18:00 по времени Алматы.")
    #     return
    
    elif user_id in registered_users:
        bot.reply_to(message, f"Вы уже зарегистрированы, {registered_users[user_id]['name']}.")
    else:
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("Я комик")
        item2=types.KeyboardButton("Не хочу быть комиком")
        item3=types.KeyboardButton("Ты кто")
        markup.add(item1)
        markup.add(item2)
        markup.add(item3)
        bot.send_message(message.chat.id,'Привет,***, я бот для записи на дневной микрофон! Нажми на кнопку «я комик», чтобы я внес тебя в список ожидания. Завтра в 21:00 бот рандомно выберет 30 юмористических дарований , которые будут выступать на дневном микрофоне!\nСписок выступающих будет на канале *** . \nЗапись идет до 00:00',reply_markup=markup)

        

@bot.message_handler(content_types='text')
def options(message):
    if message.text=="Я комик":
        bot.reply_to(message,
                     "Здравствуйте! Чтобы зарегистрироваться на \"открытый микрофон\", введите имя и фамилию, либо прозвище, под которым хотите выступать ")
        bot.register_next_step_handler(message, get_name)
    elif message.text == "Не хочу быть комиком":
        handle_cancel(message)
    elif message.text == "Ты кто":
        handle_who_are_you(message)


def handle_cancel(message):
    user_id = message.from_user.id

    if user_id not in registered_users:
        bot.reply_to(message, "Вы еще не записаны на открытый микрофон.")
    else:
        del registered_users[user_id]
        bot.reply_to(message, "Вы успешно отменили запись. Если передумаете - дайте знать!")

def handle_who_are_you(message):
    bot.send_message(message.chat.id,
                     "Важная информация:\n"
                     "- Приходите заранее\n"
                     "- Если не получается прийти, предупреждайте ведущего\n"
                     "- Готовьте не больше трех минут материала\n"
                     "- Делайте анонсы в соц. Сетях и приводите друзей\n"
                     "- Чистите зубы\n")

def get_name(message):
    user_id = message.from_user.id
    user_name = message.text

    if user_id in registered_users:
        bot.reply_to(message, f"Вы уже записаны, Завтра в 21:00 бот выберет 30 рандомных счастливчиков, которые будут выступать. Вся инфа и порядок будут в канале ведущего https://t.me/masterpingponga")
    else:
        registered_users[user_id] = {'name': user_name}
        bot.reply_to(message, f"Ты большой смельчак, {user_name}! Я поместил тебя в список на запись. Завтра в 21:00 бот выберет 30 рандомных счастливчиков, которые будут выступать. Вся инфа и порядок будут в канале ведущего https://t.me/masterpingponga")


bot.infinity_polling()
