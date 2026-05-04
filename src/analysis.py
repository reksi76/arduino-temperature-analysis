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

    # acquisition
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

    # Filering (EMA)
    if last_smooth is None:
        ema_smooth = value 

    else:
        ema_smooth = alpha * value + (1-alpha) * last_smooth

    last_smooth = ema_smooth
    ema_data.append(ema_smooth)

    # Filering (MA)
    if len(raw_data) >= window_size:
        ma_smooth = sum(list(raw_data)[-window_size:]) / window_size
        ma_data.append(ma_smooth)
    else:
        ma_smooth = value
        ma_data.append(value)

    # Error
    ema_tracking_error = abs(value - ema_smooth)
    ma_tracking_error = abs(value - ma_smooth)

    # Standard Deviasion
    if len(raw_data) > 20:
        std = np.std(raw_data)
        # print(f'EMA tracking error: {ema_tracking_error:.4f}|MA tracking error: {ma_tracking_error:.4f}|Noise Level: {std:.4f}')
    
        threshold_delta = std * 3
        if abs(value - ema_smooth) > threshold:
            print(f'Anomaly detected: {value}')
    # print(raw_data)
    # for temperature in raw_data:
        # print(f'{temperature} °C')

    prev_value = 0 
    rising = False
    start_index = None
    # Rise Time Function
    def rise_time(y):
        y = np.array(y)
        y0, y1 = y.min(), y.max()
        lo = y0 + 0.1 * (y1 - y0)
        hi = y0 + 0.9 * (y1 - y0)
    
        i_lo = np.argmax(y >= lo)
        i_hi = np.argmax(y >= hi)

        return i_hi - i_lo
    
    # beginning of the transition
    delta = value - prev_value if prev_value is not None else 0
    if not rising and abs(delta) > threshold_delta:
        rising = True
        start_index = len(raw_data) - 1 

    
    # transition ends
    if rising and delta < threshold_delta/2:
        end_index = len(raw_data) - 1 
        segment = list(raw_data)[start_index:end_index]

        if len(segment) > 5:
            rt = rise_time(segment)
            print(f'Rise time: {rt}')

        rising = False

    prev_value = value

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

