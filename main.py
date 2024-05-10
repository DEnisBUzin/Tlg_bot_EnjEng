import random
import telebot

from config import TOKEN, USER, PASSWORD, DB_NAME
from work_db import UseDataBase

state_storage = telebot.StateMemoryStorage()
token_bot = TOKEN
bot = telebot.TeleBot(token_bot, state_storage=state_storage)
work_db = UseDataBase(USER, PASSWORD, DB_NAME)
buttons = []
list_other_word = []
en_word = None
ru_word = None


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово \U00002716'
    NEXT = 'Следующее слово ⏭'
    START = 'Начать \U0001F6A9'
    END = 'Вернуться в меню 🔙'


def choose_word(user_id):
    list_word = work_db.get_word(user_id)
    return random.choice(list_word)


def get_word_for_start(message):
    global buttons, list_other_word, en_word, ru_word
    buttons = []
    two_words = choose_word(message.chat.id)
    en_word = two_words[0]
    ru_word = two_words[1]
    list_other_word = [word[0] for word in work_db.get_other_word(message.chat.id, ru_word)]
    random.shuffle(list_other_word)
    other_word = [telebot.types.KeyboardButton(word) for word in list_other_word[:3]]
    buttons.append(telebot.types.KeyboardButton(en_word))
    buttons.extend(other_word)
    random.shuffle(buttons)
    keyboardSTART = telebot.types.ReplyKeyboardMarkup(row_width=2)
    keyboardSTART.row(
        buttons[0],
        buttons[1]
    )
    keyboardSTART.row(
        buttons[2],
        buttons[3]
    )
    keyboardSTART.row(
        telebot.types.KeyboardButton(Command.NEXT)
    )
    keyboardSTART.row(
        telebot.types.KeyboardButton(Command.END)
    )
    bot.send_message(message.chat.id, f"Попробуй отгадай слово - {ru_word} 🇷🇺", reply_markup=keyboardSTART)

    @bot.message_handler(func=lambda message_new: True, content_types=['text'])
    def message_reply(message_new):
        text = message_new.text
        if text == en_word:
            bot.send_message(message_new.chat.id, "Отлично\U00002705 \n Давай следующее слово!")
        else:
            bot.send_message(message_new.chat.id, "Попробуй еще раз!\U0001F92C")


def handle_message(message):
    if work_db.get_the_word(message.chat.id, message.text.lower()):
        work_db.del_the_word(message.chat.id, message.text.lower())
        bot.send_message(message.chat.id, f'Отлично! Слово 🇷🇺{message.text}🇷🇺 - удалено\U00002705',
                         reply_markup=keyboardMAIN)
    else:
        bot.send_message(message.chat.id, 'Такого слова нет в Вашем словаре!\U0001F92C', reply_markup=keyboardMAIN)


def add_words(message):
    try:
        lst_pair = message.text.split('-')
        if not work_db.get_the_word(message.chat.id, lst_pair[0].lower()):
            work_db.add_new_word(lst_pair[1].lower(), lst_pair[0].lower(), message.chat.id)
            bot.send_message(message.chat.id, f'Отлично! Пара добавлена в словарь\U00002705',
                             reply_markup=keyboardMAIN)
        else:
            bot.send_message(message.chat.id, 'Такое слово уже есть в Вашем словаре!', reply_markup=keyboardMAIN)
    except:
        bot.send_message(message.chat.id, 'Неправильный формат ввода!', reply_markup=keyboardMAIN)


keyboardMAIN = telebot.types.ReplyKeyboardMarkup(row_width=2)
keyboardMAIN.row(
    telebot.types.KeyboardButton(Command.START),
)
keyboardMAIN.row(
    telebot.types.KeyboardButton(Command.ADD_WORD),
    telebot.types.KeyboardButton(Command.DELETE_WORD)
)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Для того чтобы общаться с ботом используй кнопки\U0001F447',
                     reply_markup=keyboardMAIN)
    work_db.create_structure()
    work_db.add_new_user(message.chat.id, message.chat.first_name)


@bot.message_handler(func=lambda message: message.text == Command.END)
def back_menu(message):
    global buttons, list_other_word, en_word
    buttons.clear()
    list_other_word.clear()
    bot.send_message(message.chat.id, 'Выбери кнопку:', reply_markup=keyboardMAIN)


@bot.message_handler(func=lambda message: message.text == Command.START)
@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    get_word_for_start(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    msg = bot.send_message(message.from_user.id, 'Напиши слово на 🇷🇺Русском🇷🇺 языке которое хочешь удалить',
                           reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, handle_message)


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    msg = bot.send_message(message.from_user.id, "Напиши слово в формате '🇷🇺слово - перевод' которое хочешь "
                                                 "добавить в словарь", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, add_words)


if __name__ == '__main__':
    print('Start telegram bot...')
    print(ru_word, en_word)
    bot.polling()
