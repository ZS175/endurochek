import json
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from categories import calculate_progress

# Путь к файлу данных
DATA_FILE = "maintenance_data.json"

# Локальная функция для загрузки данных
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}  # Возвращаем пустой словарь, если файл отсутствует
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Локальная функция для сохранения данных
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def handle_recommendations(update, context, maintenance_data, categories):
    query = update.callback_query
    await query.answer()

    current_hours = context.user_data.get("current_hours", 0)
    recommendations = []

    for section, data in categories.items():
        for task, interval in data["tasks"].items():
            last_service = maintenance_data.get(task, None)
            progress = calculate_progress(last_service, interval, current_hours)
            if progress >= 100:  # Если срок обслуживания истёк
                recommendations.append((section, task, last_service, interval, progress))

    if not recommendations:
        await query.edit_message_text("На данный момент все узлы обслужены. Рекомендаций нет.")
        return

    text = "На данный момент рекомендуется произвести обслуживание следующих узлов:\n"
    current_section = None
    keyboard = []

    for section, task, last_service, interval, progress in recommendations:
        if current_section != section:
            text += f"\n--- {section} ---\n"
            current_section = section
        text += (
            f"{task}:\n"
            f"  Последний сервис: {last_service}\n"
            f"  Интервал: {interval} моточасов\n"
            f"  Использовано: [{'█' * (progress // 10)}{'-' * (10 - progress // 10)}] {progress}%\n\n"
        )
        keyboard.append([InlineKeyboardButton(f"Выполнить {task}", callback_data=f"complete_{task}")])

    keyboard.append([InlineKeyboardButton("Главное меню", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def handle_complete_task(update, context, maintenance_data, categories):
    query = update.callback_query
    await query.answer()

    task_name = query.data.replace("complete_", "")  # Извлекаем название задачи из callback_data
    current_hours = context.user_data.get("current_hours", 0)

    if task_name in maintenance_data:
        # Обновляем данные о последнем выполнении задачи
        maintenance_data[task_name] = current_hours
        save_data(maintenance_data)

        await query.edit_message_text(
            f"Работа '{task_name}' успешно выполнена. Прогресс обновлён.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Главное меню", callback_data="main_menu")],
                [InlineKeyboardButton("Вернуться в рекомендации", callback_data="recommendations")]
            ])
        )
    else:
        await query.edit_message_text("Ошибка: задача не найдена. Попробуйте снова.")
