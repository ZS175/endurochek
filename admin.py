from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from garage import add_motorcycle, get_motorcycles
from maintenance_bot import send_main_menu  # Импортируем функцию

# Обработчик раздела Администрирование
async def handle_admin(update, context):
    keyboard = [
        [InlineKeyboardButton("Очистить данные", callback_data="clear_data")],
        [InlineKeyboardButton("Мой гараж", callback_data="garage")],
        [InlineKeyboardButton("Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("Администрирование. Выберите действие:", reply_markup=reply_markup)

# Обработчик кнопки "Мой гараж"
async def handle_garage(update, context):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    motorcycles = get_motorcycles(user_id)

    if not motorcycles:
        await query.edit_message_text("Ваш гараж пуст. Добавьте первый мотоцикл.")
        context.user_data["await_motorcycle_name"] = True
        return

    text = "Ваши мотоциклы:\n" + "\n".join([f"- {m}" for m in motorcycles])
    keyboard = [[InlineKeyboardButton("Добавить мотоцикл", callback_data="add_motorcycle")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# Обработчик кнопки "Добавить мотоцикл"
async def handle_add_motorcycle(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите название мотоцикла для добавления.")
    context.user_data["await_motorcycle_name"] = True

# Обработчик ввода названия мотоцикла
async def handle_motorcycle_name(update, context):
    if "await_motorcycle_name" in context.user_data and context.user_data["await_motorcycle_name"]:
        user_id = str(update.message.from_user.id)
        motorcycle_name = update.message.text

        add_motorcycle(user_id, motorcycle_name)
        context.user_data["await_motorcycle_name"] = False
        await update.message.reply_text(f"Мотоцикл '{motorcycle_name}' успешно добавлен в гараж.")
        await send_main_menu(update, context)

# Обработчик кнопки "Очистить данные"
async def handle_clear_data(update, context):
    query = update.callback_query
    await query.answer()

    # Очистка всех данных пользователя
    user_id = str(query.from_user.id)
    context.user_data.clear()
    # Логика для очистки дополнительных данных в других хранилищах, если требуется
    await query.edit_message_text("Ваши данные успешно очищены.")
