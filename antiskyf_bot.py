import json
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
import threading
import time
import schedule
from telegram import Update, bot
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
        json.dump(user_data, f, default=str)

# Загрузка старых данных при запуске
user_data = load_user_data()


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправь мне сообщения с числами, и я построю график раз в сутки!')


def handle_message(update: Update, context: CallbackContext) -> None:

    #print(update.message.from_user.first_name)
    #print(bot.get_chat_member(update.message.from_user.id))
    user_id = str(update.message.from_user.first_name)  # Преобразуем в строку для JSON
    text = update.message.text

    try:
        number = float(text)
        date = datetime.datetime.now().isoformat()  # Сохраняем дату в ISO формате
        
        # Добавляем данные в словарь
        if user_id not in user_data:
            user_data[user_id] = {'dates': [], 'values': []}
        
        user_data[user_id]['dates'].append(date)
        user_data[user_id]['values'].append(number)
        
        save_user_data()  # Сохраняем данные после обновления
        
        update.message.reply_text(f'Получено число: {number}')
        
    except ValueError:
        update.message.reply_text('Пожалуйста, отправьте число.')


def plot_graph(context: CallbackContext) -> None:
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


def main():
    updater = Updater(YOUR_TOKEN_HERE)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    plot_graph(context=updater)

    return 0


if __name__ == '__main__':
    main()
