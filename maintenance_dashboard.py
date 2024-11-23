from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, TextInput, Button, Div
from bokeh.layouts import column, row
from datetime import datetime
import math

# Инициализация данных
maintenance_data = {
    'oil_change': None,  # Последняя замена масла
    'air_filter': None,  # Последняя чистка воздушного фильтра
    'chain_tension': None,  # Последняя проверка натяжения цепи
}
current_hours = 0

# Настройки графиков
oil_source = ColumnDataSource(data={'start_angle': [0], 'end_angle': [0]})
air_filter_source = ColumnDataSource(data={'start_angle': [0], 'end_angle': [0]})
chain_tension_source = ColumnDataSource(data={'start_angle': [0], 'end_angle': [0]})

# Функция для расчета прогресса
def calculate_progress(last_maintenance, interval):
    if last_maintenance is None:
        return 0
    elapsed = current_hours - last_maintenance
    progress = min(1, elapsed / interval)
    return progress

# Функция для обновления данных
def update_dashboard():
    # Расчет прогресса для каждого параметра
    oil_progress = calculate_progress(maintenance_data['oil_change'], 15)
    air_filter_progress = calculate_progress(maintenance_data['air_filter'], 50)
    chain_tension_progress = calculate_progress(maintenance_data['chain_tension'], 30)
    
    # Обновляем прогрессбары
    oil_source.data = {'start_angle': [0], 'end_angle': [2 * math.pi * oil_progress]}
    air_filter_source.data = {'start_angle': [0], 'end_angle': [2 * math.pi * air_filter_progress]}
    chain_tension_source.data = {'start_angle': [0], 'end_angle': [2 * math.pi * chain_tension_progress]}
    
    # Обновляем рекомендации
    recommendations = []
    if oil_progress >= 1:
        recommendations.append("Пора заменить масло!")
    if air_filter_progress >= 1:
        recommendations.append("Пора чистить воздушный фильтр!")
    if chain_tension_progress >= 1:
        recommendations.append("Пора проверить натяжение цепи!")
    recommendations_div.text = (
        "<br>".join(recommendations)
        if recommendations
        else '<div style="font-size: 14pt; color: green;">Все в порядке!</div>'
    )

# Ввод текущих моточасов
hours_input = TextInput(title="Введите текущее количество моточасов:")
oil_input = TextInput(title="Когда была последняя замена масла?")
air_filter_input = TextInput(title="Когда была последняя чистка воздушного фильтра?")
chain_tension_input = TextInput(title="Когда была последняя проверка натяжения цепи?")

# Кнопка для обновления данных
update_button = Button(label="Обновить данные", button_type="success")

# Обработчик кнопки
def update_data():
    global current_hours
    current_hours = int(hours_input.value)
    
    # Обновляем данные обслуживания
    if oil_input.value:
        maintenance_data['oil_change'] = int(oil_input.value)
    if air_filter_input.value:
        maintenance_data['air_filter'] = int(air_filter_input.value)
    if chain_tension_input.value:
        maintenance_data['chain_tension'] = int(chain_tension_input.value)
    
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

oil_progress_bar = create_progress_bar(oil_source, "Замена масла")
air_filter_progress_bar = create_progress_bar(air_filter_source, "Воздушный фильтр")
chain_tension_progress_bar = create_progress_bar(chain_tension_source, "Натяжение цепи")

# Рекомендации
recommendations_div = Div(
    text="""<div style="font-size: 14pt; color: green;">Введите данные для рекомендаций!</div>"""
)

# Компоновка
layout = column(
    row(hours_input, oil_input, air_filter_input, chain_tension_input),
    update_button,
    row(oil_progress_bar, air_filter_progress_bar, chain_tension_progress_bar),
    recommendations_div
)

curdoc().add_root(layout)
curdoc().title = "Дашборд обслуживания мотоцикла"
