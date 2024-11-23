import json
from bokeh.plotting import curdoc
from bokeh.models import ColumnDataSource, TextInput, Button, Div
from bokeh.layouts import column, row, Spacer
import math
import os

# Путь к файлу для хранения данных
DATA_FILE = "maintenance_data.json"

# Категории, интервалы обслуживания и изображения
categories = {
    'Двигатель': {
        'tasks': {
            'Замена масла': 15,
            'Чистка воздушного фильтра': 10,
            'Регулировка клапанов': 80,
        },
        'image': "engine.png",  # Локальный файл
    },
    'Подвеска': {
        'tasks': {
            'Замена масла в вилке': 50,
            'Смазка шарниров подвески': 30,
        },
        'image': "suspension.png",  # Локальный файл
    },
}

# Загрузка данных из файла
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {task: None for category in categories.values() for task in category["tasks"].keys()}

# Сохранение данных в файл
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(maintenance_data, f, indent=4)

# Сброс данных
def reset_data():
    global maintenance_data
    maintenance_data = {task: None for category in categories.values() for task in category["tasks"].keys()}
    save_data()
    for task in service_inputs.keys():
        service_inputs[task].value = ""
    update_dashboard()

# Прогрессбар
def create_progress_bar(value, max_value):
    percentage = (value / max_value) * 100 if value is not None else 0
    return f"""
    <div style="background: #e0e0e0; border-radius: 10px; width: 100%; height: 20px; position: relative;">
        <div style="background: #3b82f6; width: {percentage}%; height: 100%; border-radius: 10px;"></div>
    </div>
    """

# Основной стиль
def generate_category_block(title, image, tasks):
    image_block = f"<img src='{image}' alt='{title}' style='width: 100%; border-radius: 10px; margin-bottom: 20px;'>"
    tasks_html = "".join([
        f"<div style='margin-bottom: 10px;'><b>{task}</b>: {create_progress_bar(maintenance_data[task], interval)}</div>"
        for task, interval in tasks.items()
    ])
    return f"""
    <div style="background: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h3 style="color: #333; font-size: 20px;">{title}</h3>
        {image_block}
        <div>
            {tasks_html}
        </div>
    </div>
    """

# Генерация HTML для категорий
def generate_dashboard_html():
    html_content = ""
    for category, data in categories.items():
        html_content += generate_category_block(category, data['image'], data['tasks'])
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 1200px; margin: auto; padding: 20px; background: #f8f9fa;">
        <h1 style="color: #333; text-align: center;">Обслуживание мотоцикла</h1>
        {html_content}
    </div>
    """

# Обновление дашборда
def update_dashboard():
    global dashboard_div
    dashboard_div.text = generate_dashboard_html()

# Инициализация данных
maintenance_data = load_data()

# Поля ввода для каждой метрики
service_inputs = {
    task: TextInput(title=f"Когда было последнее '{task}'?", value=str(maintenance_data[task] or ""))
    for category in categories.values() for task in category["tasks"].keys()
}

# Ввод текущих моточасов
hours_input = TextInput(title="Введите текущее количество моточасов:")

# Кнопки управления
update_button = Button(label="Обновить данные", button_type="primary", width=300)
reset_button = Button(label="Сбросить данные", button_type="danger", width=300)

# Обработчики кнопок
def update_data():
    global current_hours
    current_hours = int(hours_input.value)
    for task, input_field in service_inputs.items():
        if input_field.value:
            maintenance_data[task] = int(input_field.value)
    save_data()
    update_dashboard()

update_button.on_click(update_data)
reset_button.on_click(reset_data)

# Инициализация главного блока
dashboard_div = Div(text=generate_dashboard_html())

# Компоновка
layout = column(
    Div(text="<h1 style='text-align: center; color: darkblue;'>Дашборд технического обслуживания</h1>"),
    row(hours_input, Spacer(width=20), update_button, reset_button),
    Spacer(height=20),
    dashboard_div
)

# Добавление в документ
curdoc().add_root(layout)
curdoc().title = "Эндуро: Техническое обслуживание"
