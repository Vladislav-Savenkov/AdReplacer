import telebot
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне фото для обработки.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Загружаем изображение с помощью PIL
        image = Image.open(BytesIO(downloaded_file))
        image_bw = image.convert('L')

        # Сохранение обработанного изображения в BytesIO объект
        processed_image = BytesIO()
        image_bw.save(processed_image, format='JPEG')
        processed_image.seek(0)

        bot.send_photo(message.chat.id, photo=processed_image)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при обработке изображения.")

bot.polling(none_stop=True)