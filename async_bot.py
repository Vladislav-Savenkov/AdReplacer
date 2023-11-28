from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Отправь мне фото для обработки')

async def handle_photo(update: Update, context: CallbackContext) -> None:
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download('received.jpg')
    await update.message.reply_text('Фото получено, начинаю обработку...')

    # Здесь может быть ваш код для обработки изображения
    image = Image.open('received.jpg')
    image_bw = image.convert('L')
    image_bw.save('processed.jpg')

    with open('processed.jpg', 'rb') as photo:
        await update.message.reply_photo(photo)

async def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()

def run_bot():
    asyncio.run(main())

if __name__ == '__main__':
    executor = ThreadPoolExecutor(1)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, run_bot)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Остановка бота...")
        loop.stop()