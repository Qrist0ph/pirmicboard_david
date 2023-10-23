# checking if USB cable is connected for power supply
# assumption 3.3 means connected
# green led on when connected
# red led on when disconnected
from machine import Pin, ADC
from time import sleep

sensor = ADC(Pin(5))
green = Pin(15, Pin.OUT)
red = Pin(16, Pin.OUT)
# Wiederholung (Endlos-Schleife)

    
while True:
    vinValue = sensor.read()
    voltage = vinValue / 4095.0 * 3.3
    print(str(voltage))
    if voltage==3.3:
        green.off()
        red.on()
        print("cable connected")
    else:
        green.on()
        red.off()
    sleep(0.5)





