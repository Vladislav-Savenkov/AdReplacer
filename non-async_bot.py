import telebot
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Пока что у меня есть всего две команды:\n /color - перевести изображение в ч/б\n /glue - склеить два фото по заданным координатам")

@bot.message_handler(commands=['color'])
def color_command(message):
    user_data[message.chat.id] = {'command': 'color'}
    bot.reply_to(message, "Отправь мне фото, чтобы я преобразовал его в черно-белое.")

@bot.message_handler(commands=['glue'])
def glue_command(message):
    user_data[message.chat.id] = {'command': 'glue', 'photos': [], 'coords': None}
    bot.reply_to(message, "Отправь мне два фото и координаты для вставки первого во второе.")

@bot.message_handler(func=lambda message: 'command' in user_data.get(message.chat.id, {}) and user_data[message.chat.id]['command'] == 'color', content_types=['photo'])
def handle_color_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    image = Image.open(BytesIO(downloaded_file))
    image_bw = image.convert('L')

    output = BytesIO()
    image_bw.save(output, format='JPEG')
    output.seek(0)
    bot.send_photo(message.chat.id, photo=output)

    del user_data[message.chat.id]

@bot.message_handler(func=lambda message: 'command' in user_data.get(message.chat.id, {}) and user_data[message.chat.id]['command'] == 'glue', content_types=['photo'])
def handle_glue_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    user_data[message.chat.id]['photos'].append(downloaded_file)
    if len(user_data[message.chat.id]['photos']) == 2:
        bot.reply_to(message, "Теперь отправь мне координаты в формате 'x, y'.")
    else:
        bot.reply_to(message, "Сначала нужно отправить два фото")

@bot.message_handler(func=lambda message: 'command' in user_data.get(message.chat.id, {}) and user_data[message.chat.id]['command'] == 'glue' and ',' in message.text)
def handle_coords(message):
    try:
        coords = tuple(map(int, message.text.split(',')))
        user_data[message.chat.id]['coords'] = coords
        process_images(message.chat.id)
    except ValueError:
        bot.reply_to(message, "Неправильный формат координат. Используйте 'x, y'.")

def process_images(chat_id):
    try:
        photo1 = Image.open(BytesIO(user_data[chat_id]['photos'][0]))
        photo2 = Image.open(BytesIO(user_data[chat_id]['photos'][1]))

        if photo1.mode != 'RGBA':
            photo1 = photo1.convert('RGBA')
        if photo2.mode != 'RGBA':
            photo2 = photo2.convert('RGBA')

        photo1 = photo1.resize((int(photo1.width/2), int(photo1.height/2)))

        photo2.paste(photo1, user_data[chat_id]['coords'], photo1)

        output = BytesIO()
        photo2.save(output, format='PNG')
        output.seek(0)
        bot.send_photo(chat_id, photo=output)
    except Exception as e:
        bot.reply_to(chat_id, "Произошла ошибка при обработке изображений.")
    finally:
        if chat_id in user_data:
            del user_data[chat_id]


bot.polling(none_stop=True)