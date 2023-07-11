#import network
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
                   
      
      
print("assertModemOn --> Power On")
modemon=assertModemOn()
if modemon:
    print("SUCCESS !!")
else:
    print("FAILURE !!")


