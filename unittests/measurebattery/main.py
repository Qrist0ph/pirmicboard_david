# checking battery voltage on IO13
from machine import Pin, ADC
from time import sleep

sensor = ADC(Pin(6))

while True:
    vinValue = sensor.read()
    voltage = vinValue / 4095.0 * 3.3
    print(str(voltage))
    sleep(0.5)










