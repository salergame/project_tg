import telebot
import psycopg2
from googletrans import Translator, LANGUAGES
from telebot import types

translator = Translator()

bot = telebot.TeleBot('6718266928:AAFLv3ueIhUPg2HoD71eNxnoSyd4WW0Ei1A')
conn = psycopg2.connect(host='localhost',
                        database='telegram_translate',
                        user='postgres',
                        password='1234567')
cur = conn.cursor()
cur.execute('SELECT * FROM accounts')

chat_settings = {}

def generate_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('/start'))
    keyboard.add(types.KeyboardButton('/help'))
    keyboard.add(types.KeyboardButton('/languages'))  # Добавленная кнопка для выбора языка
    return keyboard

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Привет! Я бот для перевода текста. Просто выбери языки и отправь мне текст, и я переведу его.', reply_markup=generate_keyboard())

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = (
        "Список команд:\n"
        "/start - Начать использование бота\n"
        "/help - Вывести список команд"
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['languages'])
def handle_languages(message):
    # Получаем список поддерживаемых языков из googletrans
    supported_languages = list(LANGUAGES.values())

    # Создаем пользовательскую клавиатуру с кнопками для каждого языка
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [types.KeyboardButton(lang) for lang in supported_languages]
    keyboard.add(*buttons)

    bot.send_message(message.chat.id, 'Выбери язык, с которого нужно перевести:', reply_markup=keyboard)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_input = message.text

    if message.chat.id not in chat_settings:
        # Если пользователь еще не выбрал языки, предлагаем ему это сделать
        handle_languages(message)
        chat_settings[message.chat.id] = {'source': None, 'target': None}
        return

    current_settings = chat_settings[message.chat.id]

    if current_settings['source'] is None:
        # Если пользователь еще не выбрал исходный язык
        if user_input in LANGUAGES.values():
            current_settings['source'] = user_input
            bot.send_message(message.chat.id, f'Выбран исходный язык: {user_input}\nТеперь выбери язык, на который нужно перевести:')
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, выбери язык с помощью клавиатуры.')
    elif current_settings['target'] is None:
        # Если пользователь еще не выбрал целевой язык
        if user_input in LANGUAGES.values():
            current_settings['target'] = user_input
            bot.send_message(message.chat.id, f'Выбран целевой язык: {user_input}\nТеперь отправь текст для перевода:')
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, выбери язык с помощью клавиатуры.')
    else:
        # Перевод текста
        source_language = current_settings['source']
        target_language = current_settings['target']
        try:
            translation = translator.translate(user_input, src=source_language, dest=target_language).text
            response_text = f"Перевод с {source_language.capitalize()} на {target_language.capitalize()}:\n{translation}"
            bot.send_message(message.chat.id, response_text, reply_markup=generate_keyboard())
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка при переводе: {e}')

        # Сбрасываем настройки для следующего запроса
        chat_settings.pop(message.chat.id, None)

none_stop=True

if __name__ == "__main__":
    bot.polling(none_stop)
