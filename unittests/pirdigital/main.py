#14.5.23 works with devboard

from machine import Pin,ADC
from time import sleep
import time

pir_pin = Pin(10, Pin.IN)

while True: 
    value = pir_pin.value() 
    print("PIR Value: ",value  )    
    time.sleep(0.1)

    
 
