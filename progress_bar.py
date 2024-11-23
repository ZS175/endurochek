from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, Title, Label
from bokeh.layouts import column
from datetime import datetime
import math

# Настройки временного диапазона
start_date = datetime(2024, 11, 20)  # Начало: 20 ноября 2024
end_date = datetime(2025, 3, 1)  # Конец: 1 марта 2025
total_days = (end_date - start_date).days  # Общее количество дней

# Источник данных для визуализации
source = ColumnDataSource(data={
    'start_angle': [0],
    'end_angle': [0],
})

# Источник для текста с процентами
text_source = ColumnDataSource(data={'percentage': ["0%"]})

# Создаем фигуру для кругового прогрессбара
p = figure(width=400, height=400, title="Прогресс выполнения", tools="")
p.add_layout(Title(text="Скоро весна...", align="center"), "below")

# Добавляем круговую диаграмму
p.annular_wedge(
    x=0, y=0, inner_radius=0.4, outer_radius=0.8,
    start_angle='start_angle', end_angle='end_angle',
    color="blue", source=source
)

# Фон для оставшейся части
p.annular_wedge(
    x=0, y=0, inner_radius=0.4, outer_radius=0.8,
    start_angle=0, end_angle=2 * math.pi,
    color="lightgray", alpha=0.3
)

# Добавляем текст с процентами в центр
label = Label(x=0, y=0, text='0%', text_align='center', text_baseline='middle', text_font_size="20pt")
p.add_layout(label)

p.axis.visible = False
p.grid.visible = False

# Функция для расчета текущего прогресса
def calculate_progress():
    current_date = datetime.now()
    elapsed_days = (current_date - start_date).days
    progress = max(0, min(1, elapsed_days / total_days))  # Доля выполненного
    return progress

# Функция для обновления графика
def update_progress():
    progress = calculate_progress()
    end_angle = 2 * math.pi * progress  # Конечный угол
    percentage_text = f"{progress * 100:.2f}%"  # Текст с процентами
    
    # Обновляем данные
    source.data = {
        'start_angle': [0],
        'end_angle': [end_angle],
    }
    
    # Обновляем текст в центре
    label.text = percentage_text
    p.title.text = f"Прогресс: {percentage_text}"

# Настраиваем обновление в реальном времени
curdoc().add_periodic_callback(update_progress, 1000)  # Обновление каждую секунду

# Компоновка и запуск приложения
layout = column(p)
curdoc().add_root(layout)
