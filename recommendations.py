from telegram import InlineKeyboardMarkup, InlineKeyboardButton

async def handle_recommendations(update, context, maintenance_data, categories):
    query = update.callback_query
    await query.answer()

    current_hours = context.user_data.get("current_hours", 0)
    text = "На данный момент рекомендуется произвести обслуживание следующих узлов:\n\n"
    keyboard = []

    for category, data in categories.items():
        category_text = f"--- {category} ---\n"
        category_tasks = data['tasks']
        tasks_to_recommend = []

        for task, interval in category_tasks.items():
            last_service = maintenance_data.get(task, None)
            if last_service is not None and (current_hours - last_service) >= (interval - 5):
                tasks_to_recommend.append(task)

        if tasks_to_recommend:
            for task in tasks_to_recommend:
                category_text += f"{task}\n"
                keyboard.append([InlineKeyboardButton(f"Выполнить {task}", callback_data=f"complete_{task}")])

        if tasks_to_recommend:
            text += category_text + "\n"

    keyboard.append([InlineKeyboardButton("Главное меню", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup)
