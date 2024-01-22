# checking battery voltage on IO13
from machine import Pin, ADC
from time import sleep
import utime
import machine

while True:
    
    #####################################################################################
    print("##############################################################")
    print("checking charging on IO11")

    chrg_pin = Pin(11, Pin.IN)

    for i in range(10*3): 
        value = chrg_pin.value() 
        print("CHRGIG Value: ",value  )    
        utime.sleep(0.1)

    #####################################################################################
    print("##############################################################")
    print("checking fully charged on IO12")

    full_pin = Pin(12, Pin.IN)

    for i in range(10*3): 
        value = full_pin.value() 
        print("CHRGED Value: ",value  )    
        utime.sleep(0.1)


    ##################################################################################### 
    print("##############################################################")
    print("checking battery voltage on IO10")
    print("please try with different battery charging levels and not battery")
    sensor = ADC(Pin(10))
    for i in range(10):
        vinValue = sensor.read()
        voltage = vinValue / 4095.0 * 3.3
        print(str(voltage))
        sleep(0.5)