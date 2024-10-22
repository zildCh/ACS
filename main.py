
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import adcModule

# Константы
T_max = 14.2  # Максимальная температура при нагреве (В вольтах)
T_min = 6.9  # Минимальная температура при охлаждении (температура окружающей среды) (В вольтах)
b_H = 0.05  # Коэффициент нагрева
b_0 = 0.05  # Коэффициент охлаждения
T_control_accuracy = 4  # Точность управления
# Период опроса
polling_period = 0.81  # Период опроса в секундах


# Функции нагрева и охлаждения
def heating_function(current_voltage):
    return current_voltage + b_H * (T_max - current_voltage)

def cooling_function(current_voltage):
    return current_voltage - b_0 * (current_voltage - T_min)

# Данные датчиков (начальные значения)
sensors = [{"current_voltage": min(6.9 + 0.4 * i, 11.4),
            "target_temp": min(140.0 + 5 * i, 180.0),  # Ограничиваем target_temp до 180
            "heating": True,
            "matrix_operational": True,
            "punch_operational": True,
            "prev_temp": min(100 + 5 * i, 160)}
           for i in range(24)]
# Инициализация графиков
fig = plt.figure(figsize=(18, 16))
gs = fig.add_gridspec(6, 5, width_ratios=[1, 1, 1, 1, 1])
info_ax = fig.add_subplot(gs[:, 0])  # Ось для отображения информации
axs = [fig.add_subplot(gs[i // 4, i % 4 + 1]) for i in range(24)]

lines = []
for i in range(24):
    line, = axs[i].plot([], [], lw=2, label="Температура")
    target_line = axs[i].axhline(sensors[i]["target_temp"], color='r', linestyle='--', lw=1, label="T_уст")

    # Добавляем зоны таблетирования и аварийные зоны
    target_temp = sensors[i]["target_temp"]
    axs[i].fill_between([0, 40], target_temp - 12, target_temp + 12, color='yellow', alpha=0.2, label="Зона таблетирования")
    axs[i].fill_between([0, 40], target_temp - 30, target_temp + 30, color='red', alpha=0.2, label="Аварийная зона")

    lines.append(line)
    axs[i].set_xlim(0, 40)
    axs[i].set_ylim(60, 250)

# Временные и температурные данные для графиков
time_data = [np.arange(0, 40, 0.1) for _ in range(24)]
temp_data = [[sensor["current_voltage"]] for sensor in sensors]

# Функция для определения состояния пресс-формы
def determine_press_mold_state(sensor):
    if not sensor["matrix_operational"] or not sensor["punch_operational"]:
        return "Нерабочее"
    elif adcModule.voltage_to_temperature(sensor["current_voltage"]) < (
            sensor["target_temp"] - 30) or adcModule.voltage_to_temperature(sensor["current_voltage"]) > (
            sensor["target_temp"] + 30):
        return "Аварийное"
    elif adcModule.voltage_to_temperature(sensor["current_voltage"]) < (
            sensor["target_temp"] - 12) or adcModule.voltage_to_temperature(sensor["current_voltage"]) > (
            sensor["target_temp"] + 12):
        return "Запрет таблетирования"
    else:
        return "Рабочее"

# Фильтрация ложной информации
def filter_anomaly(sensor, new_temp):
    if abs(new_temp - sensor["prev_temp"]) > 20:
        return sensor["prev_temp"]
    sensor["prev_temp"] = new_temp
    return new_temp

# Обновление данных
def update(frame):
    info_ax.clear()
    info_ax.axis('off')
    heaters_state = []
    press_molds_state = []
    target_temp = []


    for i, sensor in enumerate(sensors):

        # Фильтрация аномальных значений
        filtered_temp = filter_anomaly(sensor, adcModule.voltage_to_temperature(sensor["current_voltage"]))
        temp_data[i].append(filtered_temp)
        # Обновляем температуру датчика в зависимости от режима (нагрев/охлаждение)
        if sensor["heating"]:
            sensor["current_voltage"] = heating_function(sensor["current_voltage"])
            if adcModule.voltage_to_temperature(sensor["current_voltage"]) >= (
                    sensor["target_temp"] + T_control_accuracy / 2):
                sensor["heating"] = False
        else:
            sensor["current_voltage"] = cooling_function(sensor["current_voltage"])
            if adcModule.voltage_to_temperature(sensor["current_voltage"]) <= (
                    sensor["target_temp"] - T_control_accuracy):
                sensor["heating"] = True



        if len(temp_data[i]) > len(time_data[i]):
            temp_data[i].pop(0)

        lines[i].set_data(time_data[i][:len(temp_data[i])], temp_data[i])
        # axs[i].set_title(
        #     f"Датчик {i + 1}: Текущая T = {filtered_temp:.1f}°C, "
        #     f"Уставка Tуст = {sensor['target_temp']}°C, "
        #     f"{'Нагрев' if sensor['heating'] else 'Охлаждение'}")

        # Определяем состояние пресс-формы
        press_mold_state = determine_press_mold_state(sensor)
        press_molds_state.append(press_mold_state)
        heaters_state.append("Включен" if sensor["heating"] else "Выключен")
        target_temp.append(sensor['target_temp'])
    # Отображение информации о нагревателях и пресс-формах на экране
    for i in range(24):
        info_ax.text(0.05, 0.95 - i * 0.04,
                     f"Датчик {i + 1}: Нагреватель: {heaters_state[i]}, "
                     f"Температура: {temp_data[i][-1]:.1f}°C\n"
                     f"Состояние пресс-формы: {press_molds_state[i]}"
                     f"Нагреватель: {press_molds_state[i]}"
                     f"Уставная температура: { target_temp[i]}",
                     fontsize=8, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.6))

    return lines

ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 500, polling_period), blit=False, repeat=False)
plt.tight_layout()
plt.legend()
plt.show()