from machine import Pin, ADC
from time import sleep

sensor = ADC(Pin(12))

# Wiederholung (Endlos-Schleife)
while True:
    value = sensor.read()
    print(str(value)+"."*int(value/10))
    sleep(0.5)



