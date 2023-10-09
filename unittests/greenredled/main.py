# function test
# makes the blue led on GPIO 17 blink
from machine import Pin
from time import sleep

green = Pin(15, Pin.OUT)
red = Pin(16, Pin.OUT)
while True:
    green.on()    
    red.on()    
    sleep(2)
    green.off()    
    red.off()    
    sleep(2)
 