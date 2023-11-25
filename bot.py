from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image
import io
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправь мне фото для обработки')

def handle_photo(update: Update, context: CallbackContext) -> None:
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('received.jpg')
    update.message.reply_text('Фото получено, начинаю обработку...')

    # Обработка изображения, можно вынести в отдельный файл
    image = Image.open('received.jpg')
    image_bw = image.convert('L')
    image_bw.save('processed.jpg')

    with open('processed.jpg', 'rb') as photo:
        update.message.reply_photo(photo)

def main() -> None:
    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()