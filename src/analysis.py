import matplotlib.pyplot as plt 
import numpy as np 
import re 
from collections import deque
from matplotlib.animation import FuncAnimation
import serial
import time

try:
    ser = serial.Serial('COM5', 9600, timeout = 1)
    print('Sensor Connected!')
except:
    print('No Sensor Connected!')
    exit()

raw_data = deque(maxlen=100)

# Eksponential Moving Average (EMA)
ema_data = deque(maxlen=100)
# Moving Average (MA)
ma_data = deque(maxlen=100)
N = 50

alpha = 0.2
last_smooth = None
window_size = 5

fig, ax = plt.subplots()

def update(frame):
    global last_smooth 

    try:
        line = ser.readline().decode(errors='ignore').strip()

    except serial.SerialException:
        print('Sensor Disconnected!')
        return
    except Exception as e:
        print(f'Error: {e}')

    match = re.search(r'\d+\.?\d+', line)
    if not match:
        return
    value = float(match.group())

    if not (20 < value < 40):
        return

    raw_data.append(value)

    if last_smooth is None:
        smooth = value 

    else:
        smooth = alpha * value + (1-alpha) * last_smooth

    if len(raw_data) >= window_size:
        ma = sum(list(raw_data)[-window_size:]) / window_size
        ma_data.append(ma)
    else:
        ma_data.append(value)


    last_smooth = smooth
    ema_data.append(smooth)

    if abs(value - smooth) > 0.5:
        print(f'Anomaly detected: {value}')

    for temperature in raw_data:
        print(f'{temperature} °C')

    ax.clear()
    ax.plot(raw_data, label='Raw Data')
    ax.plot(ema_data, label='Eksponential Moving Average (EMA)')
    ax.plot(ma_data, label='Moving Average (MA)')
    ax.set_ylabel('Temperature (°C)')
    ax.legend()
    ax.set_title('Real-time Temperature (Sensor DS180B20)')
    ax.grid(True)

ani = FuncAnimation(fig, update, interval=200)
plt.show()

with open('data.txt', 'a') as file:
    for d in raw_data:
        file.write(f'{d}\n')

print('\nProgram finished!')
time.sleep(3)

