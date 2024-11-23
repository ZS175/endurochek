import json
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from categories import categories, calculate_progress
from recommendations import handle_recommendations, handle_complete_task
from admin import handle_admin, handle_clear_data, handle_garage, handle_add_motorcycle, handle_motorcycle_name


# Путь к файлу для хранения данных
DATA_FILE = "maintenance_data.json"

# Глобальные переменные для ConversationHandler
ASK_HOURS, ASK_TASKS = range(2)
CURRENT_TASK = None

# Загрузка данных
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {task: None for category in categories.values() for task in category['tasks'].keys()}

# Сохранение данных
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Инициализация данных
maintenance_data = load_data()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(r"D:\PY\main.png", "rb") as photo:
        await update.message.reply_photo(photo=photo, caption=(
            "Привет! Обслуживание эндуро мотоцикла — это важный процесс, который напрямую влияет на его производительность, долговечность и безопасность. "
            "Этот Телеграм-БОТ поможет поддерживать твой мотоцикл в хорошем состоянии!"
        ))
    await update.message.reply_text("Пожалуйста, укажи текущие показания моточасов:")
    return ASK_HOURS

# Обработчик ввода текущих моточасов
async def set_current_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current_hours = int(update.message.text)
        context.user_data["current_hours"] = current_hours
        await update.message.reply_text(f"Текущие моточасы установлены: {current_hours}.\nТеперь укажите данные для задач с отсутствующими значениями.")
        missing_tasks = [task for task, value in maintenance_data.items() if value is None]

        if missing_tasks:
            global CURRENT_TASK
            CURRENT_TASK = missing_tasks[0]
            await update.message.reply_text(f"Когда был выполнен последний '{CURRENT_TASK}'? Укажите моточасы.")
            return ASK_TASKS
        else:
            await send_main_menu(update, context)
            return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите числовое значение моточасов.")
        return ASK_HOURS

# Обработчик ввода данных для задач с None
async def set_task_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_TASK

    try:
        hours = int(update.message.text)
        maintenance_data[CURRENT_TASK] = hours
        save_data(maintenance_data)
        await update.message.reply_text(f"Данные для задачи '{CURRENT_TASK}' обновлены: {hours} моточасов.")
        missing_tasks = [task for task, value in maintenance_data.items() if value is None]

        if missing_tasks:
            CURRENT_TASK = missing_tasks[0]
            await update.message.reply_text(f"Когда был выполнен последний '{CURRENT_TASK}'? Укажите моточасы.")
            return ASK_TASKS

        await send_main_menu(update, context)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите числовое значение моточасов.")
        return ASK_TASKS

# Функция для отправки главного меню
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Двигатель", callback_data="engine")],
        [InlineKeyboardButton("Подвеска", callback_data="suspension")],
        [InlineKeyboardButton("Тормоза", callback_data="brakes")],
        [InlineKeyboardButton("Колеса", callback_data="wheels")],
        [InlineKeyboardButton("Цепь", callback_data="chain")],
        [InlineKeyboardButton("Прочее", callback_data="other")],
        [InlineKeyboardButton("Рекомендации", callback_data="recommendations")],
        [InlineKeyboardButton("Администрирование", callback_data="admin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Все задачи заполнены. Выберите раздел или получите рекомендации:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Все задачи заполнены. Выберите раздел или получите рекомендации:", reply_markup=reply_markup)

# Обработчик кнопок разделов
async def handle_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    section_mapping = {
        "engine": "Двигатель",
        "suspension": "Подвеска",
        "brakes": "Тормоза",
        "wheels": "Колеса",
        "chain": "Цепь",
        "other": "Прочее",
        "recommendations": "Рекомендации",
        "admin": "Администрирование",
    }

    if query.data == "main_menu":  # Обрабатываем кнопку "Главное меню"
        await send_main_menu(update, context)
        return

    if query.data == "admin":  # Обрабатываем кнопку "Администрирование"
        await handle_admin(update, context)
        return

    if query.data == "recommendations":  # Обрабатываем кнопку "Рекомендации"
        await handle_recommendations(update, context, maintenance_data, categories)
        return

    selected_section = section_mapping.get(query.data)
    if selected_section is None:
        await query.edit_message_text("Неизвестный раздел. Попробуйте снова.")
        return

    tasks = categories[selected_section]['tasks']
    text = f"--- {selected_section} ---\n\n"
    current_hours = context.user_data.get("current_hours", 0)
    for task, interval in tasks.items():
        last_service = maintenance_data.get(task, None)
        progress = calculate_progress(last_service, interval, current_hours)
        text += f"{task}:\n  Последний сервис: {last_service}\n  Интервал: {interval} моточасов\n"
        text += f"  Использовано: [{'█' * (progress // 10)}{'-' * (10 - progress // 10)}] {progress}%\n\n"

    keyboard = [[InlineKeyboardButton("Главное меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

# Основная функция
def main():
    application = Application.builder().token("7937921741:AAHcF995V_pXfv-F32qvsI-mgcVHUZ_OZAg").build()

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_current_hours)],
            ASK_TASKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_task_data)],
        },
        fallbacks=[],
    ))
    application.add_handler(CallbackQueryHandler(handle_section, pattern="^(engine|suspension|brakes|wheels|chain|other|recommendations|admin|main_menu)$"))
    application.add_handler(CallbackQueryHandler(handle_clear_data, pattern="^clear_data$"))
    application.add_handler(CallbackQueryHandler(handle_garage, pattern="^garage$"))
    application.add_handler(CallbackQueryHandler(handle_add_motorcycle, pattern="^add_motorcycle$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_motorcycle_name))
    application.add_handler(CallbackQueryHandler(
        lambda update, context: handle_complete_task(update, context, maintenance_data, categories),
        pattern="^complete_.*$"
    ))

    application.run_polling()

if __name__ == "__main__":
    main()
