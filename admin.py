import json
import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# Путь к файлу для хранения данных
DATA_FILE = "maintenance_data.json"

# Функция для очистки данных
def clear_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return {}


# Обработчик для кнопки "Администрирование"
async def handle_admin(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Очистить данные", callback_data="clear_data")],
        [InlineKeyboardButton("Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("Администрирование. Выберите действие:", reply_markup=reply_markup)


# Обработчик для кнопки "Очистить данные"
async def handle_clear_data(update, context: ContextTypes.DEFAULT_TYPE):
    clear_data()
    await update.callback_query.message.reply_text("Данные успешно очищены. Начните с команды /start.")
