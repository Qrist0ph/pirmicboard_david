# function test
# makes the blue led on GPIO 17 blink
from machine import Pin
from time import sleep

led = Pin(17, Pin.OUT)
while True:
    led.on()    
    sleep(0.5)
    led.off()    
    sleep(0.5)
 