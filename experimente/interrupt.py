import uasyncio as asyncio
from machine import Pin, PWM
import time
from machine import RTC

rtc = RTC()
rtc.datetime((2022, 7, 25, 1, 1, 30, 42, 0)) # set date and time


  
# Globale Variable für den Integer
counter = 0

# Funktion für den Thread
async def increment_counter():
    global counter
    print("Counter:", counter)
    print(rtc.datetime()) # get date and time
    while True:        
        counter += 1
        print("Counter:", counter)
        print(rtc.datetime()) # get date and time
        pwm_c = PWM(Pin(8), duty=512)
        # set the frequency of the buzzer to 500Hz
        pwm_c.freq(500)
        # wait for 5 seconds
        time.sleep(5)
        # stop the buzzer
        pwm_c.deinit()
        await asyncio.sleep(60)  # Warte 60 Sekunden

# Starte den Thread
loop = asyncio.get_event_loop()
loop.create_task(increment_counter())
loop.run_forever()

