#14.5.23 works with devboard

from machine import Pin,ADC
from time import sleep
import time

pir_pin = Pin(7, Pin.IN)
sensor = ADC(pir_pin )
while True:
    pir_value = pir_pin.value()   
    value = sensor.read()
    print("Voltage: %.2f" % (value ) )    
    time.sleep(0.1)

    
 