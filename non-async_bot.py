import telebot
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os
import time

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Этот бот создан для того, чтобы заменять или перекрывать рекламу на ваших фото.\n\nВы можете сохранять свои шаблоны рекламы для частого использования, либо же отправить фото и шаблон без сохранения.\n\nВоспользуйтесь командой /help для того, чтобы узнать о командах работы с шаблонами.")
    send_funcs(message)

@bot.message_handler(commands=['edit'])
def send_funcs(message):
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton('Редактировать по сохраненному шаблону', callback_data='edit_saved')
    button2 = telebot.types.InlineKeyboardButton('Редактировать без сохранения', callback_data='edit_phantom')
    button3 = telebot.types.InlineKeyboardButton('Сохранить новый шаблон', callback_data='create_new_adfr')
    markup.add(button1)
    markup.add(button2)
    markup.add(button3)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == 'edit_saved':
        saved_edit_command(call.message)
    elif call.data == 'edit_phantom':
        phantom_edit_command(call.message)
    elif call.data == 'create_new_adfr':
        handle_save_ad_command(call.message)

@bot.message_handler(commands=['help'])
def send_info(message):
    bot.reply_to(message, "Все доступные команды бота для работы с шаблонами:\n\n/save_ad - Создать новый шаблон\n/show_ads - Посмотреть свои сохраненные шаблоны\n/remove_ad - Удалить сохраненный шаблон\n/edit - Сообщение с основными кнопками для работы с ботом")

@bot.message_handler(commands=['save_ad'])
def handle_save_ad_command(message):
    user_data[message.chat.id] = {'command': 'save_ad'}
    bot.reply_to(message, "Отправь мне фото, чтобы я сохранил его как шаблон.")

def phantom_edit_command(message):
    user_data[message.chat.id] = {'command': 'edit_phantom', 'photos': []}
    bot.reply_to(message, "Отправь мне фото и шаблон рекламы.")

def saved_edit_command(message):
    username = message.chat.username if message.chat.username else 'unknown_user'
    user_dir = os.path.join('user_photos', username)

    if os.path.exists(user_dir) and os.listdir(user_dir):
        user_data[message.chat.id] = {'command': 'edit_saved', 'photos': [], 'ad_template': None}
        bot.send_message(message.chat.id, "Выберите номер шаблона для использования:")

        for index, file_name in enumerate(sorted(os.listdir(user_dir)), start=1):
            file_path = os.path.join(user_dir, file_name)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    bot.send_photo(message.chat.id, photo=file, caption=f'Шаблон #{index}')
    else:
        bot.send_message(message.chat.id, "У вас нет сохраненных шаблонов. Используйте /save_ad для создания шаблона.")

@bot.message_handler(func=lambda message: 'command' in user_data.get(message.chat.id, {}) and user_data[message.chat.id]['command'] == 'edit_saved')
def handle_template_selection(message):
    try:
        template_number = int(message.text)
        username = message.from_user.username if message.from_user.username else 'unknown_user'
        user_dir = os.path.join('user_photos', username)

        files = sorted([f for f in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, f))])
        if 0 < template_number <= len(files):
            user_data[message.chat.id]['ad_template'] = os.path.join(user_dir, files[template_number - 1])
            bot.send_message(message.chat.id, "Теперь отправьте мне фото для обработки.")
        else:
            bot.send_message(message.chat.id, "Неправильный номер шаблона. Пожалуйста, выберите снова.")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер шаблона.")

@bot.message_handler(func=lambda message: 'command' in user_data.get(message.chat.id, {}) and user_data[message.chat.id]['command'] == 'edit_saved', content_types=['photo'])
def handle_saved_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    user_data[message.chat.id]['photos'].append(downloaded_file)
    #template = bytes(user_data[message.chat.id]['ad_template'])
    #не уверен что это так работает и при реальной работе нужно будет фиксить
    #user_data[message.chat.id]['photos'].append(template)
    if len(user_data[message.chat.id]['photos']) == 1:
        process_images(message.chat.id, 0)
    else:
        bot.reply_to(message, "Сначала нужно отправить фото")

@bot.message_handler(func=lambda message: 'command' in user_data.get(message.chat.id, {}) and user_data[message.chat.id]['command'] == 'save_ad', content_types=['photo'])
def handle_color_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    username = message.from_user.username if message.from_user.username else 'unknown_user'

    user_dir = os.path.join('user_photos', username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    file_count = len([name for name in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, name))])
    image_path = os.path.join(user_dir, f'{file_count + 1}.jpg')
    with open(image_path, 'wb') as file:
        file.write(downloaded_file)

    bot.reply_to(message, "Шаблон сохранен!")
    del user_data[message.chat.id]

@bot.message_handler(commands=['show_ads'])
def show_ads(message):
    username = message.from_user.username if message.from_user.username else 'unknown_user'
    user_dir = os.path.join('user_photos', username)

    if os.path.exists(user_dir) and os.listdir(user_dir):
        for index, file_name in enumerate(sorted(os.listdir(user_dir)), start=1):
            file_path = os.path.join(user_dir, file_name)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    bot.send_photo(message.chat.id, photo=file, caption=f'Шаблон #{index}')
    else:
        bot.reply_to(message, "У вас пока нет сохраненных шаблонов.")

@bot.message_handler(commands=['remove_ad'])
def remove_ad_command(message):
    user_data[message.chat.id] = {'command': 'remove_ad'}
    bot.reply_to(message, "Введите номер шаблона, который вы хотите удалить.")

@bot.message_handler(func=lambda message: 'command' in user_data.get(message.chat.id, {}) and user_data[message.chat.id]['command'] == 'remove_ad')
def handle_remove_ad(message):
    try:
        photo_number = int(message.text)
        username = message.from_user.username if message.from_user.username else 'unknown_user'
        user_dir = os.path.join('user_photos', username)

        if os.path.exists(user_dir):
            files = sorted([f for f in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, f))])
            if 0 < photo_number <= len(files):
                os.remove(os.path.join(user_dir, files[photo_number-1]))
                bot.reply_to(message, f"Шаблон #{photo_number} удален.")
            else:
                bot.reply_to(message, "Шаблон с таким номером не найден. Попробуйте еще раз.")
        else:
            bot.reply_to(message, "У вас пока нет сохраненных шаблонов.")

    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите корректный номер шаблона.")
    
    finally:
        if message.chat.id in user_data:
            del user_data[message.chat.id]

@bot.message_handler(func=lambda message: 'command' in user_data.get(message.chat.id, {}) and user_data[message.chat.id]['command'] == 'edit_phantom', content_types=['photo'])
def handle_phantom_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    user_data[message.chat.id]['photos'].append(downloaded_file)
    if len(user_data[message.chat.id]['photos']) == 2:
        process_images(message.chat.id, 1)
    elif len(user_data[message.chat.id]['photos']) == 1:
        bot.send_message(message.chat.id, "Ожидаю второе фото..")
    else:
        bot.reply_to(message, "Сначала нужно отправить фото и шаблон рекламы")

def process_images(chat_id, pic_flag):
    try:
        pass
        # bot.send_message(chat_id, "Обрабатываю фото...")
        # time.sleep(5)
        # k = 1 if pic_flag else 2
        # file1 = open(f"ph{k}.png", "rb")
        # bot.send_photo(chat_id, photo=file1, caption="Ваше фото с измененной рекламой!")
        # file1.close()
    except Exception as e:
        bot.reply_to(chat_id, "Произошла ошибка при обработке изображений.")
    finally:
        if chat_id in user_data:
            del user_data[chat_id]


bot.polling(none_stop=True)