import json
import os

# Путь к файлу для хранения гаража
GARAGE_FILE = "user_garage.json"

# Загрузка данных гаража
def load_garage():
    if os.path.exists(GARAGE_FILE):
        with open(GARAGE_FILE, "r") as f:
            return json.load(f)
    return {}

# Сохранение данных гаража
def save_garage(garage_data):
    with open(GARAGE_FILE, "w") as f:
        json.dump(garage_data, f, indent=4)

# Добавление мотоцикла в гараж
def add_motorcycle(user_id, motorcycle_name):
    garage = load_garage()
    if user_id not in garage:
        garage[user_id] = []
    garage[user_id].append(motorcycle_name)
    save_garage(garage)

# Получение списка мотоциклов
def get_motorcycles(user_id):
    garage = load_garage()
    return garage.get(user_id, [])
