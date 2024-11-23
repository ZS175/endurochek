from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, TextInput, Button, Div, Spacer
from bokeh.layouts import column, row, layout
import math

# Инициализация данных обслуживания (по категориям)
categories = {
    'Двигатель': {
        'Замена масла': 15,
        'Чистка воздушного фильтра': 10,
        'Регулировка клапанов': 80,
        'Осмотр и чистка свечи зажигания': 20,
        'Замена свечи зажигания': 40,
    },
    'Подвеска': {
        'Замена масла в вилке': 50,
        'Смазка шарниров подвески': 30,
        'Регулировка заднего амортизатора': 40,
    },
    'Тормоза': {
        'Замена тормозной жидкости': 100,
    },
    'Колеса': {
        'Осмотр подшипников осей': 50,
        'Осмотр и замена покрышек': 80,
        'Регулировка давления в шинах': 5,
    },
    'Прочее': {
        'Проверка и смазка цепи': 5,
        'Проверка аккумулятора': 50,
        'Регулировка троса сцепления': 30,
    },
}

# Инициализация данных
maintenance_data = {task: None for category in categories.values() for task in category.keys()}
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
    for task, interval in {task: interval for category in categories.values() for task, interval in category.items()}.items():
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
service_inputs = {task: TextInput(title=f"Когда было последнее '{task}'?", value="") for task in maintenance_data.keys()}

# Кнопка для обновления данных
update_button = Button(label="Обновить данные", button_type="primary", width=300)

# Обработчик кнопки
def update_data():
    global current_hours
    current_hours = int(hours_input.value)
    for task in maintenance_data.keys():
        if service_inputs[task].value:
            maintenance_data[task] = int(service_inputs[task].value)
    update_dashboard()

update_button.on_click(update_data)

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
for category, tasks in categories.items():
    # Поля ввода и прогрессбары для категории
    inputs = row(*[service_inputs[task] for task in tasks.keys()], sizing_mode="stretch_width")
    bars = row(*[progress_bars[task] for task in tasks.keys()])
    
    # Аннотация для категории
    annotation = Div(text=f"<div style='font-size: 18pt; color: blue;'><b>{category}</b></div>", width=900)
    
    # Фон категории
    section = column(annotation, inputs, bars, Spacer(height=20), background="lightblue", css_classes=["category-card"])
    category_sections.append(section)

# Рекомендации
recommendations_div = Div(
    text="""<div style="font-size: 16pt; color: green;">Введите данные для рекомендаций!</div>"""
)

# Общая структура страницы
layout = column(
    Div(text="<h1 style='color: darkblue; text-align: center;'>Дашборд для обслуживания эндуро мотоцикла</h1>"),
    hours_input,
    update_button,
    Spacer(height=20),
    *category_sections,
    recommendations_div,
)

curdoc().add_root(layout)
curdoc().title = "Эндуро: Техническое обслуживание"
