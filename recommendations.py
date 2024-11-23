from telegram import InlineKeyboardMarkup, InlineKeyboardButton

async def handle_recommendations(update, context, maintenance_data, categories):
    query = update.callback_query
    await query.answer()

    current_hours = context.user_data.get("current_hours", 0)
    recommendations = []

    for section, data in categories.items():
        for task, interval in data["tasks"].items():
            last_service = maintenance_data.get(task, None)
            if last_service is None or current_hours - last_service >= interval - 5:
                recommendations.append((section, task, last_service, interval))

    if not recommendations:
        await query.edit_message_text("Нет рекомендаций на данный момент.")
        return

    text = "На данный момент рекомендуется произвести обслуживание следующих узлов:\n"
    keyboard = []
    for section, task, last_service, interval in recommendations:
        text += f"\n--- {section} ---\n{task}:\n  Последний сервис: {last_service}\n  Интервал: {interval} моточасов\n"
        keyboard.append([InlineKeyboardButton(f"Выполнить {task}", callback_data=f"complete_{task}")])

    keyboard.append([InlineKeyboardButton("Главное меню", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def handle_complete_task(update, context, maintenance_data):
    query = update.callback_query
    await query.answer()

    task = query.data.replace("complete_", "")
    current_hours = context.user_data.get("current_hours", 0)
    maintenance_data[task] = current_hours

    await query.edit_message_text(f"Работа '{task}' успешно выполнена. Прогресс обновлён.")
