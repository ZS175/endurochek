from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
from categories import categories, calculate_progress
from recommendations import handle_recommendations, handle_complete_task
from admin import handle_admin, handle_clear_data
import json
import os

DATA_FILE = "maintenance_data.json"

ASK_HOURS, ASK_TASKS = range(2)
CURRENT_TASK = None

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {task: None for category in categories.values() for task in category["tasks"].keys()}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

maintenance_data = load_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Укажите текущие моточасы:")
    return ASK_HOURS

async def set_current_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current_hours = int(update.message.text)
        context.user_data["current_hours"] = current_hours
        await update.message.reply_text(f"Текущие моточасы установлены: {current_hours}.")
        await send_main_menu(update, context)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Введите число!")
        return ASK_HOURS

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Двигатель", callback_data="engine")],
        [InlineKeyboardButton("Подвеска", callback_data="suspension")],
        [InlineKeyboardButton("Тормоза", callback_data="brakes")],
        [InlineKeyboardButton("Колеса", callback_data="wheels")],
        [InlineKeyboardButton("Прочее", callback_data="other")],
        [InlineKeyboardButton("Рекомендации", callback_data="recommendations")],
        [InlineKeyboardButton("Администрирование", callback_data="admin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Выберите раздел:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Выберите раздел:", reply_markup=reply_markup)

async def handle_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    section_mapping = {
        "engine": "Двигатель",
        "suspension": "Подвеска",
        "brakes": "Тормоза",
        "wheels": "Колеса",
        "other": "Прочее",
        "recommendations": "Рекомендации",
        "admin": "Администрирование",
    }

    if query.data == "main_menu":
        await send_main_menu(update, context)
        return

    if query.data == "recommendations":
        await handle_recommendations(update, context, maintenance_data, categories)
        return

    if query.data == "admin":
        await handle_admin(update, context)
        return

    selected_section = section_mapping.get(query.data)
    if not selected_section:
        await query.edit_message_text("Ошибка: раздел не найден.")
        return

    tasks = categories[selected_section]["tasks"]
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

def main():
    application = Application.builder().token("7937921741:AAHcF995V_pXfv-F32qvsI-mgcVHUZ_OZAg").build()

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={ASK_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_current_hours)]},
        fallbacks=[],
    ))
    application.add_handler(CallbackQueryHandler(handle_section))
    application.add_handler(CallbackQueryHandler(handle_complete_task, pattern="^complete_.*$"))

    application.run_polling()

if __name__ == "__main__":
    main()
