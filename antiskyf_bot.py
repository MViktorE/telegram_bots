import json
import os
import datetime

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

def main() -> None:
    print("Hello 2024!")
    user_id = 10
    date = datetime.datetime.now().isoformat()  # Сохраняем дату в ISO формате
    
    if user_id not in user_data:
        user_data[user_id] = {'dates': [], 'values': []}
    
    user_data[user_id]['dates'].append(date)
    user_data[user_id]['values'].append(15.56)
    save_user_data()  # Сохраняем данные


if __name__ == '__main__':
    main()
