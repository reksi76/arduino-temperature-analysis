import matplotlib.pyplot as plt 
import numpy as np 
import re 
from collections import deque
from matplotlib.animation import FuncAnimation
import serial
import time

ser = serial.Serial('COM5', 9600, timeout = 1)

raw_data = deque(maxlen=100)
smooth_data = deque(maxlen=100)
N = 50

alpha = 0.2
last_smooth = None

fig, ax = plt.subplots()

def update(frame):
	global last_smooth

	line = ser.readline().decode(errors='ignore').strip()
	match = re.search(r'\d+\.?\d+', line)

	if match:
		value = float(match.group())

		if not (20 < value < 40):
			return

		raw_data.append(value)

		if last_smooth is None:
			smooth = value 

		else:
			smooth = alpha * value + (1-alpha) * last_smooth

		last_smooth = smooth
		smooth_data.append(smooth)

		if abs(value - smooth) > 0.5:
			print(f'Anomaly detected: {value}')

	for temperature in raw_data:
		print(f'{temperature} °C')

	ax.clear()
	ax.plot(raw_data, label='Raw Data')
	ax.plot(smooth_data, label='Smoothed data')
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

