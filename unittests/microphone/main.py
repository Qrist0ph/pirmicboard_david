# Bibliotheken laden
# 2.9.23 Mic Running
from machine import Pin, ADC
from time import sleep

sensor = ADC(Pin(3))

# Wiederholung (Endlos-Schleife)
while True:
    value = sensor.read()
    print(str(value)+"."*int(value/10))
    sleep(0.03)



