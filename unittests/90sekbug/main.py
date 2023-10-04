# test für 90sek PIR IRQ Bug

from machine import Pin, PWM
from time import sleep
import time
import utime

# called whenever something moves
def pir_detected(pin):
    pwm_c = PWM(Pin(8), duty=512)
    # set the frequency of the buzzer to 500Hz
    pwm_c.freq(500)
    # wait for 5 seconds
    time.sleep(0.3)
    # stop the buzzer
    pwm_c.deinit()
    print("Pin change detected:", pin)



# check for movement on interrupt
pir_pin = Pin(10, Pin.IN)
pir_pin.irq(trigger=Pin.IRQ_RISING, handler=pir_detected)

# Keep the program running
while True:
    utime.sleep(4)  # Sleep to prevent the program from exiting immediately
    print("running")
