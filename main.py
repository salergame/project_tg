import telebot
import psycopg2
from googletrans import Translator
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
    keyboard.add(types.KeyboardButton('/lang'))
    keyboard.add(types.KeyboardButton('/help '))
    return keyboard

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Привет! Я бот для перевода текста. Просто отправь мне текст, и я переведу его.', reply_markup=generate_keyboard())

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = (
        "Список команд:\n"
        "/start - Начать использование бота\n"
        "/lang [исходный язык] [целевой язык] - Указать языки для перевода (например, /lang ru en)\n"
        "/help - Вывести список команд"
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['lang'])
def handle_lang(message):
    try:
        _, source_language, target_language = message.text.split()
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, укажите два языка для перевода с помощью команды /lang. Например, /lang ru en')
        return

    chat_settings[message.chat.id] = {'source': source_language, 'target': target_language}

    bot.send_message(message.chat.id, f'Языки для перевода установлены: {source_language} -> {target_language}')

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_input = message.text

    if message.chat.id not in chat_settings:
        bot.send_message(message.chat.id, 'Пожалуйста, укажите язык для перевода с помощью команды /lang. Например, /lang ru en')
        return

    current_settings = chat_settings[message.chat.id]
    source_language = current_settings['source']
    target_language = current_settings['target']

    # Перевод текста
    try:
        translation = translator.translate(user_input, src=source_language, dest=target_language).text
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при переводе: {e}')
        return

    # Формируем ответ и отправляем его пользователю
    response_text = f"Перевод с {source_language.capitalize()} на {target_language.capitalize()}: {translation}"
    bot.send_message(message.chat.id, response_text, reply_markup=generate_keyboard())
none_stop=True
if __name__ == "__main__":
    bot.polling(none_stop)
