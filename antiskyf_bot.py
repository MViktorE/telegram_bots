import json
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import io
import threading
import time
import schedule
import re
import logging
from datetime import datetime
from telegram import Update, bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Секретики :)
YOUR_TOKEN_HERE = os.getenv('TELEGRAM_TOKEN')
MY_CHAT_ID = os.getenv('CHAT_ID')

# Файл для хранения данных пользователей
DATA_FILE = 'user_data.json'

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция для загрузки данных из файла
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Функция для сохранения данных в файл
def save_user_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(user_data, f, sort_keys=True, indent=4)

# Загрузка старых данных при запуске
user_data = load_user_data()

def is_user_in_group(user_name: str):
    return user_name in user_data

def start(update: Update, context: CallbackContext) -> None:
    logger.info(f'In /start command')
    update.message.reply_text(ResponseUpon.Start())

def add_me(update: Update, context: CallbackContext) -> None:
    """Register new user"""
    logger.info(f'In /add_me command')
    user_name = str(update.message.from_user.first_name)
    if is_user_in_group(user_name):
        update.message.reply_text(ResponseUpon.AlreadyInTheUserList(user_name))
        return
    # Add into table
    user_data[user_name] = {'dates': [], 'values': []}
    if not handle_message(update, context):
        del user_data[user_name]
        update.message.reply_text(ResponseUpon.InvalidAddMe(user_name))
        return

    update.message.reply_text(ResponseUpon.ValidAddMe(user_name))

class ResponseUpon:
    """Содержит возможные ответы чат бота"""
    @staticmethod
    def Start() -> str:
        return \
            ('Привет!\n'
            'Отправь мне сообщения с числами, и я построю график раз в сутки!\n'
            'Но перед этим зарегистрируйся с помощью команды /add_me <начальное_значение_веса> и я внесу тебя в таблицу\n'
            'А пока ты не зарегистрировался, я тебя буду игнорировать')
    @staticmethod
    def ValidWeight(weight: float) -> str:
        return f'Получено число: {weight}.'

    @staticmethod
    def InvalidWeight(weight: float) -> str:
        return f'Значение "{weight}" не похоже на вес.'

    @staticmethod
    def NonNumericInput() -> str:
        return 'Пожалуйста, отправьте сообщение с числом.'

    @staticmethod
    def MultipleNumbers() -> str:
        return 'Похоже, что были отправлены два числа. Так не пойдет.'

    @staticmethod
    def AlreadyInTheUserList(user_name: str) -> str:
        return f'{user_name}, ты уже в участниках.'

    @staticmethod
    def ValidAddMe(user_name: str) -> str:
        return f'{user_name}, ты в списке участников.'

    @staticmethod
    def InvalidAddMe(user_name: str) -> str:
        return f'{user_name}, не получилось тебя добавить.'


class WeightUtils:
    """Проверка и валидация веса"""
    MIN_WEIGHT = 30.0
    MAX_WEIGHT = 150.0

    @staticmethod
    def is_plausible_weight(value: float) -> bool:
        """Check if the given value is within a plausible weight range."""
        return WeightUtils.MIN_WEIGHT <= value <= WeightUtils.MAX_WEIGHT

    @staticmethod
    def extract_numbers_from_text(text: str) -> list[float]:
        """Extract numbers from a text message."""
        matches = re.findall(r'(\d+(?:[.,]\d+)?)', text)
        return [float(match.replace(',', '.')) for match in matches]


def handle_message(update: Update, context: CallbackContext) -> bool:
    logger.info(f"Message received: {update.message.text}")
    logger.info(f"From: {update.message.from_user.first_name}")
    logger.info(f"His id: {update.message.from_user.id}")
    user_name = str(update.message.from_user.first_name)  # Преобразуем в строку для JSON

    # Ignore if not registered user
    if not is_user_in_group(user_name):
        logger.warning(f"{user_name} is not participant. So ignore him.")
        return False

    # Extract numbers from the message
    numbers = WeightUtils.extract_numbers_from_text(update.message.text)

    if not numbers:
        update.message.reply_text(ResponseUpon.NonNumericInput())
        return False

    # Если в сообщении больше 1 числа, то лучше выдать ошибку
    if len(numbers) > 1:
        update.message.reply_text(ResponseUpon.MultipleNumbers())
        return False

    weight = numbers[0]

    if not WeightUtils.is_plausible_weight(weight):
        update.message.reply_text(ResponseUpon.InvalidWeight(weight))
        return False

    date = datetime.now().isoformat()  # Сохраняем дату в ISO формате

    user_data[user_name]['dates'].append(date)
    user_data[user_name]['values'].append(weight)

    save_user_data()  # Сохраняем данные после обновления

    update.message.reply_text(ResponseUpon.ValidWeight(weight))

    return True

def plot_graph(context: CallbackContext) -> None:
    logger.info('Plot start')
    plt.figure(figsize=(10, 5))

    for user_id, data in user_data.items():
        if not data['values']:
            continue

        # Создаем DataFrame из данных пользователя
        df = pd.DataFrame({
            'dates': pd.to_datetime(data['dates']),
            'values': data['values']
        })

        # Строим график

        plt.plot(df['dates'], df['values'], marker='o', label=f'{user_id}')

    plt.title('Вес, кг')
    plt.xlabel('Дата')
    plt.ylabel('Значение')
    plt.grid()
    plt.legend()

    # Сохраняем график в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()  # Закрываем фигуру после сохранения

    # Отправляем график в чат
    context.bot.send_photo(chat_id=MY_CHAT_ID, photo=buf)


def main() -> int:
    updater = Updater(YOUR_TOKEN_HERE)

    # dispatcher to register command handlers
    dp = updater.dispatcher

    # user commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add_me", add_me))

    # handle messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Запускаем планировщик в отдельном потоке
    def run_scheduler():
        counter = 0
        while True:
            schedule.run_pending()
            logger.info("In scheduler")
            time.sleep(1)
            counter += 1
            if counter > 5:
                break   
                
    logger.info("Start scheduler thread")
    threading.Thread(target=run_scheduler).start()
    
    logger.info("Bot is polling..")
    updater.start_polling()

    time.sleep(3)
    plot_graph(context=updater)
    logger.info("Bot is stop polling")
    updater.stop()

    return 0  
        

if __name__ == '__main__':
    sys.exit(main())
