#14.5.23 works with devboard

from machine import Pin,ADC
from time import sleep
import time

pir_pin = Pin(6, Pin.IN)

while True:
    pir_value = pir_pin.value()   
    value = sensor.read()
    print("PIR Value: ",value  )    
    time.sleep(0.1)

    
 