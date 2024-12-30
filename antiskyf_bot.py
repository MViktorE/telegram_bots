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
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Секретики :)
YOUR_TOKEN_HERE = os.getenv('TELEGRAM_TOKEN')
MY_CHAT_ID = os.getenv('CHAT_ID')

# Файл для хранения данных пользователей
DATA_FILE = 'user_data.json'

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

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправь мне сообщения с числами, и я построю график раз в сутки!')

class ResponseUpon:
    """Содержит возможные ответы чат бота"""
    @staticmethod
    def ValidWeight(weight: float) -> str:
        return f'Получено число: {weight}'

    @staticmethod
    def InvalidWeight(weight: float) -> str:
        return f'Значение "{weight}" не похоже на вес'

    @staticmethod
    def NonNumericInput() -> str:
        return 'Пожалуйста, отправьте сообщение с числом.'

    @staticmethod
    def MultipleNumbers() -> str:
        return 'Похоже, что были отправлены два числа. Так не пойдет'


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


def handle_message(update: Update, context: CallbackContext) -> None:
    #print(update.message.from_user.first_name)
    #print(bot.get_chat_member(update.message.from_user.id))
    user_id = str(update.message.from_user.first_name)  # Преобразуем в строку для JSON
    user_message = update.message.text
    # Extract numbers from the message
    numbers = WeightUtils.extract_numbers_from_text(user_message)

    if not numbers:
        update.message.reply_text(ResponseUpon.NonNumericInput())
        return

    # Если в сообщении больше 1 числа, то лучше выдать ошибку
    if len(numbers) > 1:
        update.message.reply_text(ResponseUpon.MultipleNumbers())
        return

    weight = numbers[0]

    if not WeightUtils.is_plausible_weight(weight):
        update.message.reply_text(ResponseUpon.InvalidWeight(weight))
        return

    # Добавляем данные в словарь
    if user_id not in user_data:
        user_data[user_id] = {'dates': [], 'values': []}

    date = datetime.now().isoformat()  # Сохраняем дату в ISO формате

    user_data[user_id]['dates'].append(date)
    user_data[user_id]['values'].append(weight)

    save_user_data()  # Сохраняем данные после обновления

    update.message.reply_text(ResponseUpon.ValidWeight(weight))

def plot_graph(context: CallbackContext) -> None:
    print("plot start")
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

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))



    # Запускаем планировщик в отдельном потоке
    def run_scheduler():
        counter = 0
        while True:
            schedule.run_pending()
            print("In sheduler!!!")
            time.sleep(1)
            counter += 1
            if counter > 5:
                break   
                
    print("start tread")
    threading.Thread(target=run_scheduler).start()
    
    print("start polling")
    updater.start_polling()
    print("idle")
    # updater.idle()

    time.sleep(3)
    plot_graph(context=updater)
    print("stop")
    updater.stop()

    return 0  
        

if __name__ == '__main__':
    sys.exit(main())
