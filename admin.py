from telegram import InlineKeyboardMarkup, InlineKeyboardButton

async def handle_admin(update, context):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("Очистить данные", callback_data="clear_data")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Раздел Администрирование. Выберите действие:", reply_markup=reply_markup)

async def handle_clear_data(update, context):
    global maintenance_data
    maintenance_data = {task: None for category in categories.values() for task in category["tasks"].keys()}
    await update.callback_query.edit_message_text("Данные успешно очищены.")
