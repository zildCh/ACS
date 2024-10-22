# Константы АЦП
V_min = 0.0  # Минимальное входное напряжение (В)
V_max = 10.0  # Максимальное входное напряжение (В)
ADC_resolution = 8  # Разрядность АЦП (8 бит)
ADC_max_value = (2 ** ADC_resolution) - 1  # Максимальное значение АЦП

# Таблица градуировки термопар (температура в градусах Цельсия и напряжение в мВ)
calibration_table = [
    # Низкие значения
    (0, 0.0), (10, 0.7), (20, 1.4), (30, 2.0), (40, 2.6),
    (50, 3.2), (60, 3.8), (70, 4.4), (80, 5.0), (90, 5.6),
    (95, 6.2),
    # Изначальные значения
    (100, 6.9), (105, 7.3), (110, 7.6), (115, 8.0), (120, 8.4),
    (125, 8.7), (130, 9.1), (135, 9.5), (140, 9.9), (145, 10.2),
    (150, 10.6), (155, 11.0), (160, 11.4), (165, 11.8), (170, 12.2),
    (175, 12.6), (180, 13.0), (185, 13.4), (190, 13.8), (195, 14.2),
    # Высокие значения
    (200, 14.6), (210, 15.4), (220, 16.2), (230, 17.0), (240, 17.8),
    (250, 18.6), (260, 19.4), (270, 20.2), (280, 21.0), (290, 21.8),
    (300, 22.6)
]

def voltage_to_temperature(voltage):
    # Проверяем, находится ли напряжение в пределах таблицы
    if voltage <= calibration_table[0][1]:
        return calibration_table[0][0]
    elif voltage >= calibration_table[-1][1]:
        return calibration_table[-1][0]

    # Ищем ближайшие точки в таблице для интерполяции (линейно кусочная интерполяция)
    for i in range(len(calibration_table) - 1):
        t1, v1 = calibration_table[i]
        t2, v2 = calibration_table[i + 1]
        if v1 <= voltage <= v2:
            # Линейная интерполяция для нахождения температуры
            temperature = t1 + (voltage - v1) * (t2 - t1) / (v2 - v1)
            return temperature

    # Если данные вне диапазона, возвращаем None
    return None

def adc_read(voltage):
    # Ограничиваем напряжение в пределах допустимого диапазона
    voltage = max(V_min, min(V_max, voltage))
    # Преобразуем напряжение в значение АЦП
    adc_value = int((voltage - V_min) / (V_max - V_min) * ADC_max_value)
    return adc_value

def adc_to_temperature(adc_value):
    # Преобразуем значение АЦП обратно в напряжение
    voltage = (adc_value / ADC_max_value) * (V_max - V_min) + V_min
    return voltage_to_temperature(voltage)

# Тестирование
test_voltages = [0.0, 2.5, 5.0, 7.5, 10.0]  # Примеры входных напряжений
for v in test_voltages:
    adc_val = adc_read(v)
    temp = adc_to_temperature(adc_val)
    print(f"Напряжение: {v:.1f} В, Значение АЦП: {adc_val}, Температура: {temp if temp is not None else 'Вне диапазона'}°C")


####################################################################################################################
#1
# РАССЧЕТЫ ДЛЯ ОТЧЕТА

# Провести аппроксимацию градуировочной характеристики датчика температуры пресс-форм кусочно-
# линейным методом, рассчитать коэффициент передачи согласующего усилителя, определить время цикла опроса датчиков.
# Определение коэффициента передачи

U_out_max = 14.2  # максимальное выходное напряжение (мВ) при 195°C
U_in_max = 10.0   # максимальное входное напряжение (мВ) (пример)
K = U_out_max / U_in_max

# Определение периода опроса датчиков
q = 0.05 # погрешность измерения (°C)
T_up = 4.0  # точность управления (°C)
epsilon = q + T_up  # общая погрешность

f_max = 5  # максимальная скорость изменения (°C/с)
delta_T = epsilon / f_max  # период опроса

print(f"Коэффициент передачи: {K:.4f}")
print(f"Период опроса датчиков: {delta_T:.4f} с")


####################################################################################################################
#2
# график градуировочной характеристики и результаты аппроксимации.
import numpy as np
import matplotlib.pyplot as plt

# Данные из градуировочной таблицы (температура, мВ)
temperature_data = np.array([
    100, 105, 110, 115, 120, 125, 130, 135, 140, 145,
    150, 155, 160, 165, 170, 175, 180, 185, 190, 195
])
voltage_data = np.array([
    6.9, 7.3, 7.6, 8.0, 8.4, 8.7, 9.1, 9.5, 9.9, 10.2,
    10.6, 11.0, 11.4, 11.8, 12.2, 12.6, 13.0, 13.4, 13.8, 14.2
])

# Аппроксимация кусочно-линейным методом
def piecewise_linear_approx(temp, voltage, x):
    for i in range(len(temp) - 1):
        t1, v1 = temp[i], voltage[i]
        t2, v2 = temp[i + 1], voltage[i + 1]
        if t1 <= x <= t2:
            # Линейная интерполяция
            return v1 + (x - t1) * (v2 - v1) / (t2 - t1)
    # Если x вне диапазона, вернуть None
    return None

# Создаем график
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(temperature_data, voltage_data, 'o-', label='Градуировочная характеристика')

# Генерируем точки для аппроксимации
approx_temps = np.linspace(100, 195, 100)
approx_voltages = [piecewise_linear_approx(temperature_data, voltage_data, t) for t in approx_temps]

# Добавляем аппроксимацию на график
ax.plot(approx_temps, approx_voltages, '--', label='Аппроксимация (кусочно-линейная)')

# Настройки графика
ax.set_xlabel('Температура (°C)')
ax.set_ylabel('Напряжение (мВ)')
ax.set_title('Градуировочная характеристика и кусочно-линейная аппроксимация')
ax.legend()
ax.grid(True)

# Показать график
plt.show()
####################################################################################################################
#3
#Временная диаграмма работы алгоритма
import matplotlib.pyplot as plt
import numpy as np
# Константы
T_max = 14.2  # Максимальная температура при нагреве (В вольтах)
T_min = 6.9  # Минимальная температура при охлаждении (температура окружающей среды) (В вольтах)
b_H = 0.05  # Коэффициент нагрева
b_0 = 0.05  # Коэффициент охлаждения
T_control_accuracy = 4  # Точность управления

# Период опроса
polling_period = 0.81 # Период опроса в секундах
total_time = 50 # Общее время моделирования (в секундах)

# Начальное состояние датчика
initial_voltage = 6.0  # Начальное напряжение
target_temp = 160.0  # Целевая температура (ограничена 180 в проекте)

# Временные данные
time_data = np.arange(0, total_time, polling_period)
temp_data = []
heater_state_data = []

# Функции нагрева и охлаждения
def heating_function(current_voltage):
    return current_voltage + b_H * (T_max - current_voltage)

def cooling_function(current_voltage):
    return current_voltage - b_0 * (current_voltage - T_min)

# Моделирование работы датчика
current_voltage = initial_voltage
heating = True

for t in time_data:
    # Обновляем температуру датчика в зависимости от режима (нагрев/охлаждение)
    if heating:
        current_voltage = heating_function(current_voltage)
        if voltage_to_temperature(current_voltage) >= (target_temp + T_control_accuracy / 2):
            heating = False
    else:
        current_voltage = cooling_function(current_voltage)
        if voltage_to_temperature(current_voltage) <= (target_temp - T_control_accuracy / 2):
            heating = True

    # Сохраняем данные
    temp_data.append(voltage_to_temperature(current_voltage))
    heater_state_data.append(1 if heating else 0)

# Построение графика
fig, ax1 = plt.subplots(figsize=(10, 6))

# График температуры
ax1.plot(time_data, temp_data, 'b-', label="Температура ")
ax1.set_xlabel("Время (секунды)")
ax1.set_ylabel("Температура (С)", color='b')
ax1.tick_params(axis='y', labelcolor='b')
ax1.set_title("Временная диаграмма работы алгоритма")

# График состояния нагревателя
ax2 = ax1.twinx()
ax2.plot(time_data, heater_state_data, 'r--', label="Состояние нагревателя (вкл/выкл)")
ax2.set_ylabel("Состояние нагревателя", color='r')
ax2.tick_params(axis='y', labelcolor='r')
ax2.set_yticks([0, 1])
ax2.set_yticklabels(['Выкл', 'Вкл'])

# Легенда и отображение графика
fig.tight_layout()
plt.show()