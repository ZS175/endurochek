from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, TextInput, Button, Div
from bokeh.layouts import column, row
import math

# Инициализация данных обслуживания
maintenance_data = {
    'Замена масла': None,
    'Чистка воздушного фильтра': None,
    'Замена масла в вилке': None,
    'Проверка и смазка цепи': None,
    'Смазка шарниров подвески': None,
    'Регулировка заднего амортизатора': None,
    'Замена тормозной жидкости': None,
    'Осмотр подшипников осей': None,
    'Осмотр и замена покрышек': None,
    'Регулировка давления в шинах': None,
    'Осмотр и чистка свечи зажигания': None,
    'Замена свечи зажигания': None,
    'Регулировка клапанов': None,
    'Проверка аккумулятора': None,
    'Регулировка троса сцепления': None,
}
current_hours = 0

# Настройки интервалов обслуживания (в моточасах)
service_intervals = {
    'Замена масла': 15,
    'Чистка воздушного фильтра': 10,
    'Замена масла в вилке': 50,
    'Проверка и смазка цепи': 5,
    'Смазка шарниров подвески': 30,
    'Регулировка заднего амортизатора': 40,
    'Замена тормозной жидкости': 100,
    'Осмотр подшипников осей': 50,
    'Осмотр и замена покрышек': 80,
    'Регулировка давления в шинах': 5,
    'Осмотр и чистка свечи зажигания': 20,
    'Замена свечи зажигания': 40,
    'Регулировка клапанов': 80,
    'Проверка аккумулятора': 50,
    'Регулировка троса сцепления': 30,
}

# Источники данных для прогрессбаров
progress_sources = {key: ColumnDataSource(data={'start_angle': [0], 'end_angle': [0]}) for key in service_intervals.keys()}

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
    for key, interval in service_intervals.items():
        progress = calculate_progress(maintenance_data[key], interval)
        progress_sources[key].data = {'start_angle': [0], 'end_angle': [2 * math.pi * progress]}
        if progress >= 1:
            recommendations.append(f"Пора выполнить: {key}")
    # Обновляем рекомендации
    recommendations_div.text = (
        "<br>".join(recommendations)
        if recommendations
        else '<div style="font-size: 14pt; color: green;">Все в порядке! Обслуживание не требуется.</div>'
    )

# Ввод текущих моточасов
hours_input = TextInput(title="Введите текущее количество моточасов:")
service_inputs = {
    key: TextInput(title=f"Когда было последнее '{key}'?", value="")
    for key in maintenance_data.keys()
}

# Кнопка для обновления данных
update_button = Button(label="Обновить данные", button_type="success")

# Обработчик кнопки
def update_data():
    global current_hours
    current_hours = int(hours_input.value)
    for key in service_inputs.keys():
        if service_inputs[key].value:
            maintenance_data[key] = int(service_inputs[key].value)
    update_dashboard()

update_button.on_click(update_data)

# Прогрессбары
def create_progress_bar(source, title):
    p = figure(width=300, height=300, title=title, tools="")
    p.annular_wedge(
        x=0, y=0, inner_radius=0.4, outer_radius=0.8,
        start_angle='start_angle', end_angle='end_angle',
        color="blue", source=source
    )
    p.annular_wedge(
        x=0, y=0, inner_radius=0.4, outer_radius=0.8,
        start_angle=0, end_angle=2 * math.pi,
        color="lightgray", alpha=0.3
    )
    p.axis.visible = False
    p.grid.visible = False
    return p

progress_bars = [
    create_progress_bar(progress_sources[key], key)
    for key in maintenance_data.keys()
]

# Рекомендации
recommendations_div = Div(
    text="""<div style="font-size: 14pt; color: green;">Введите данные для рекомендаций!</div>"""
)

# Компоновка
layout = column(
    row(hours_input, *service_inputs.values()),
    update_button,
    *[row(*progress_bars[i:i+3]) for i in range(0, len(progress_bars), 3)],
    recommendations_div
)

curdoc().add_root(layout)
curdoc().title = "Дашборд для эндуро мотоцикла"
