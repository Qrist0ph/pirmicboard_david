# deepsleep unit test 
# erst modem ausschalten
# dann deepsleep
# verbrauch mus unter 0.01 Ampere fallen
# messen mit einem USB Stick messgerät
import time
import machine 
from machine import UART, Pin
import utime

uart = UART(1, baudrate=115200,bits=8, parity=None, stop=1, tx=21, rx=47)
pwr = 4  #pin to control the power of the module

def waitResp_info():
    prvMills = utime.ticks_ms()
    info = b""
    while (utime.ticks_ms()-prvMills)<2000:        
        if uart.any():
            info = b"".join([info, uart.read(1)])
    print(info)
    try:
        return info.replace(b'\xFE', b'').replace(b'\xFF', b'').decode()
    except:
        print("some error")
    return 

# zum power toggle muss offenbar 0_1_0 auf GPIO 14 gemacht werden
def toggleOnOff():
    #bei aufsteigender Flanke wird immer On Off getoggelt
    machine.Pin(pwr, machine.Pin.OUT).value(0)
    utime.sleep(2)
    machine.Pin(pwr, machine.Pin.OUT).value(1)
    utime.sleep(2)
    machine.Pin(pwr, machine.Pin.OUT).value(0)
    utime.sleep(2)
    
def assertModemOn():
    c=0
    while True:
        c=c+1
        if(c>10):
            return False

        uart.write( b'AT\r\n' )
        utime.sleep(2)
        recBuff = waitResp_info()
        if 'OK' in recBuff:
            print ("modem already powered on")
            return True
        else:
            print("modem is still powered off -> toggleOnOff() ")
            toggleOnOff()          
            for i in range(1,10):
                utime.sleep(2)                
                # for some reason sometime just sending AT is not enough
                uart.write( b'AT+CGNSINF\r\n' )
                utime.sleep(2)
                recBuff = waitResp_info()
                if 'OK' in recBuff:
                    print ("modem now powered on")
                    return True
                   
      
def assertModemOff():
    c=0
    while True:
        c=c+1
        if(c>10):
            break       
        uart.write( 'AT\r\n'.encode() )
        utime.sleep(2)
       
        uart.write( 'AT\r\n'.encode() )
        recBuff = waitResp_info()
        #falls modem schon eingeschaltet ist
        if 'OK' in recBuff:
            print ("modem noch eingeschaltet -> toggleOnOff()")
            toggleOnOff()
            utime.sleep(2)
          
            print("Erwarte 'NORMAL POWER DOWN' Message")
            utime.sleep(3)
           
            print(waitResp_info() )
        else:
            print ("modem ist jetzt ausgeschaltet  ")
            break


print("assertModemOn --> Power On")
assertModemOn()

print("assertModemOff --> Power On")
assertModemOff()

#hier die deepsleep zeit anpassen
print("30 sek deepsleep")
print("jetzt müssen 0.01 Ampere gemessen werden")
machine.deepsleep(30000)
#Thonny will say
#PROBLEM IN THONNY'S BACK-END: Exception while handling 'Run' (ConnectionError: EOF).
#See Thonny's backend.log for more info.
#You may need to press "Stop/Restart" or hard-reset your MicroPython device and try again.
print("deepsleep vorbei")
print("30 sek normal sleep")
utime.sleep(30)
print("jetzt müssen 0.1 Ampere gemessen werden")
machine.reset()