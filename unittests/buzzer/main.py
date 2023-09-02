# 2.9.23
# buzzer working
import machine
from machine import Pin, PWM
import time

# create pwm channel on pin P20 with a duty cycle of 50%
pwm_c = PWM(Pin(8), duty=512)

# set the frequency of the buzzer to 500Hz
pwm_c.freq(500)

# wait for 5 seconds
time.sleep(5)

# stop the buzzer
pwm_c.deinit()

