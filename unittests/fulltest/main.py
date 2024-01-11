# checking battery voltage on IO13
from machine import Pin, ADC,PWM
from time import sleep
import utime

#####################################################################################
print("##############################################################")
print("checking PIR on IO10 for 30 seconds")
print("please make movement in front of PIR")
pir_pin = Pin(10, Pin.IN)

for i in range(100*30): 
    value = pir_pin.value() 
    print("PIR Value: ",value  )    
    utime.sleep(0.1)



#####################################################################################
print("##############################################################")
print("checking buzzer on IO8")
# create pwm channel on pin P20 with a duty cycle of 50%
pwm_c = PWM(Pin(8), duty=512)
# set the frequency of the buzzer to 500Hz
pwm_c.freq(500)
# wait for 5 seconds
utime.sleep(1)
# stop the buzzer
pwm_c.deinit()
#####################################################################################
print("##############################################################")
print("checking Vin voltage on IO5")
print("buzzer will beep when cable disconnected")
sensor = ADC(Pin(5))
for i in range(10):
    vinValue = sensor.read()
    voltage = vinValue / 4095.0 * 3.3
    print(str(voltage))
    if vinValue!=4095.0:
        print("no USB Power")
        pwm_c = PWM(Pin(8), duty=512)
        pwm_c.freq(500)
        utime.sleep(1)
        pwm_c.deinit()
    else:
        print("USB power")
    sleep(0.5)
##################################################################################### 
print("##############################################################")
print("checking battery voltage on IO13")
print("please try with different battery charging levels and not battery")
sensor = ADC(Pin(13))
for i in range(10):
    vinValue = sensor.read()
    voltage = vinValue / 4095.0 * 3.3
    print(str(voltage))
    sleep(0.5)


#####################################################################################
print("##############################################################")
print("checking microphone on IO3  for 10 seconds")
sensor = ADC(Pin(3))

# Wiederholung (Endlos-Schleife)
for i in range(300): 
    value = sensor.read()
    print(str(value)+"."*int(value/10))
    sleep(0.03)
#####################################################################################
print("##############################################################")
# End testing
print("End testing")
pwm_c = PWM(Pin(8), duty=512)
pwm_c.freq(500)
utime.sleep(1)
pwm_c.deinit()


