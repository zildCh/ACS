import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import math

# Константы
T_max = 300  # Максимальная температура при нагреве
T_min = 30  # Минимальная температура при охлаждении (температура окружающей среды)
b_H = 0.05  # Коэффициент нагрева
b_0 = 0.05  # Коэффициент охлаждения
T_control_accuracy = 4  # Точность управления
A = 150  # Максимальная температура при нагреве (возможно, можно поменять на T_max)
B = 20   # Температура окружающей среды при охлаждении (возможно, можно поменять на T_min)

# Функции нагрева и охлаждения      !придумал chatgpt работает
def heating_function(current_temp):
    return current_temp + b_H * (T_max - current_temp)


def cooling_function(current_temp):
    return current_temp - b_0 * (current_temp - T_min)

# Данные датчиков (начальные значения)
sensors = [
    {"current_temp": 90.0, "target_temp": 100.0, "heating": True},
    {"current_temp": 100.8, "target_temp": 110.0, "heating": True},
    {"current_temp": 66.9, "target_temp": 120.0, "heating": True},
    {"current_temp": 64.3, "target_temp": 130.0, "heating": True},
]

# Инициализация графиков
fig, axs = plt.subplots(2, 2, figsize=(10, 8))
lines = []
target_lines = []
for i in range(4):
    line, = axs[i // 2, i % 2].plot([], [], lw=2, label="Температура")
    target_line = axs[i // 2, i % 2].axhline(sensors[i]["target_temp"], color='r', linestyle='--', lw=1, label="T_уст")
    lines.append(line)
    target_lines.append(target_line)
    axs[i // 2, i % 2].set_xlim(0, 40)
    axs[i // 2, i % 2].set_ylim(0, 160)

# Временные и температурные данные для графиков
time_data = [np.arange(0, 40, 0.1) for _ in range(4)]
temp_data = [[sensor["current_temp"]] for sensor in sensors]


# Обновление данных Опрос датчиков
def update(frame):
    for i, sensor in enumerate(sensors):
        # Обновляем температуру датчика в зависимости от режима (нагрев/охлаждение)
        if sensor["heating"]:
            sensor["current_temp"] = heating_function(sensor["current_temp"])
            if sensor["current_temp"] >= (sensor["target_temp"] + T_control_accuracy / 2):
                sensor["heating"] = False
        else:
            sensor["current_temp"] = cooling_function(sensor["current_temp"])
            if sensor["current_temp"] <= (sensor["target_temp"] - T_control_accuracy):
                sensor["heating"] = True

        # Обновляем данные графика
        temp_data[i].append(sensor["current_temp"])
        if len(temp_data[i]) > len(time_data[i]):
            temp_data[i].pop(0)

        lines[i].set_data(time_data[i][:len(temp_data[i])], temp_data[i])
        axs[i // 2, i % 2].set_title(f"Датчик {i + 1}: Текущая T = {sensor['current_temp']:.1f}°C, "
                                     f"Уставка Tуст = {sensor['target_temp']}°C, "
                                     f"{'Нагрев' if sensor['heating'] else 'Охлаждение'}")

    return lines


ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 500, 0.1), blit=False, repeat=False)
plt.tight_layout()
plt.legend()
plt.show()