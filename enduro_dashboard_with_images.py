import json
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, TextInput, Button, Div, Spacer
from bokeh.layouts import column, row
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
            'Осмотр и чистка свечи зажигания': 20,
            'Замена свечи зажигания': 40,
        },
        'image': "https://sc04.alicdn.com/kf/H51e8ce7322244ee6816ec54973829c5cf.png",  # Ссылка на изображение двигателя
    },
    'Подвеска': {
        'tasks': {
            'Замена масла в вилке': 50,
            'Смазка шарниров подвески': 30,
            'Регулировка заднего амортизатора': 40,
        },
        'image': "d:/py/suspension.png",  # Ссылка на изображение подвески
    },
    'Тормоза': {
        'tasks': {
            'Замена тормозной жидкости': 100,
        },
        'image': "https://moto-detal.ru/content/uploads/2019/07/133-1-1.jpg",  # Ссылка на изображение тормозов
    },
    'Колеса': {
        'tasks': {
            'Осмотр подшипников осей': 50,
            'Осмотр и замена покрышек': 80,
            'Регулировка давления в шинах': 5,
        },
        'image': "https://example.com/wheels.png",  # Ссылка на изображение колес
    },
    'Прочее': {
        'tasks': {
            'Проверка и смазка цепи': 5,
            'Проверка аккумулятора': 50,
            'Регулировка троса сцепления': 30,
        },
        'image': "https://example.com/other.png",  # Ссылка на изображение прочего
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

# Инициализация данных
maintenance_data = load_data()
progress_sources = {task: ColumnDataSource(data={'start_angle': [0], 'end_angle': [0]}) for task in maintenance_data.keys()}
current_hours = 0

# Функция для расчета прогресса
def calculate_progress(last_service, interval):
    if last_service is None:
        return 0
    elapsed = current_hours - last_service
    progress = min(1, elapsed / interval)
    return progress

# Функция для обновления прогрессбаров и рекомендаций
def update_dashboard():
    recommendations = []
    for task, interval in {task: interval for category in categories.values() for task, interval in category["tasks"].items()}.items():
        progress = calculate_progress(maintenance_data[task], interval)
        progress_sources[task].data = {'start_angle': [0], 'end_angle': [2 * math.pi * progress]}
        if progress >= 1:
            recommendations.append(f"Пора выполнить: {task}")
    # Обновляем рекомендации
    recommendations_div.text = (
        "<br>".join(recommendations)
        if recommendations
        else '<div style="font-size: 16pt; color: green;">Все в порядке! Обслуживание не требуется.</div>'
    )

# Ввод текущих моточасов
hours_input = TextInput(title="Введите текущее количество моточасов:")

# Поля ввода для каждой метрики
service_inputs = {
    task: TextInput(title=f"Когда было последнее '{task}'?", value=str(maintenance_data[task] or ""))
    for task in maintenance_data.keys()
}

# Кнопки управления
update_button = Button(label="Обновить данные", button_type="primary", width=300)
reset_button = Button(label="Сбросить данные", button_type="danger", width=300)

# Обработчик кнопок
def update_data():
    global current_hours
    current_hours = int(hours_input.value)
    for task in maintenance_data.keys():
        if service_inputs[task].value:
            maintenance_data[task] = int(service_inputs[task].value)
    save_data()
    update_dashboard()

update_button.on_click(update_data)
reset_button.on_click(reset_data)

# Прогрессбары
def create_progress_bar(source, title):
    p = figure(width=300, height=300, title=title, tools="")
    p.annular_wedge(
        x=0, y=0, inner_radius=0.4, outer_radius=0.8,
        start_angle='start_angle', end_angle='end_angle',
        color="blue", source=source, alpha=0.8
    )
    p.annular_wedge(
        x=0, y=0, inner_radius=0.4, outer_radius=0.8,
        start_angle=0, end_angle=2 * math.pi,
        color="lightgray", alpha=0.4
    )
    p.axis.visible = False
    p.grid.visible = False
    return p

progress_bars = {task: create_progress_bar(progress_sources[task], task) for task in maintenance_data.keys()}

# Компоновка по категориям
category_sections = []
for category, data in categories.items():
    tasks = data["tasks"]
    image = data["image"]
    
    # Поля ввода и прогрессбары
    inputs = row(*[service_inputs[task] for task in tasks.keys()], sizing_mode="stretch_width")
    bars = row(*[progress_bars[task] for task in tasks.keys()])
    
    # Изображение
    img_div = Div(text=f"<img src='{image}' alt='{category}' style='width:200px; height:auto;'>")
    
    # Аннотация
    annotation = Div(text=f"<div style='font-size: 18pt; color: blue;'><b>{category}</b></div>", width=900)
    
    # Секция
    section = column(
        annotation, row(img_div, Spacer(width=20), column(inputs, bars)), Spacer(height=20), background="lightblue"
    )
    category_sections.append(section)

# Рекомендации
recommendations_div = Div(
    text="""<div style="font-size: 16pt; color: green;">Введите данные для рекомендаций!</div>"""
)

# Общая структура страницы
layout = column(
    Div(text="<h1 style='color: darkblue; text-align: center;'>Дашборд для обслуживания эндуро мотоцикла</h1>"),
    hours_input,
    row(update_button, reset_button),
    Spacer(height=20),
    *category_sections,
    recommendations_div,
)

curdoc().add_root(layout)
curdoc().title = "Эндуро: Техническое обслуживание"
