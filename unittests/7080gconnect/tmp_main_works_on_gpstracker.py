# 28.10.2022
# pico w deepsleep patch
# logCall, battery
# SimCom 7080G + Pico Script
# PICO Deep Sleep  Test mit DeepSleep und Normal Modus
# PICO geht entweder in den deepsleep modus oder in den normal modus
# falls verzeichnis deepsleep existiert dann deepsleep modus, sonst normal modus

# Google Doc mit Kabelbelegung https://docs.google.com/document/d/1RsIvsyK8wx0Kr5VQp8_xyVW1U5oQrc9f_jCxV8jEb8E/edit#heading=h.ysg6t5dq0tcm
# Video: https://photos.app.goo.gl/m6BXxvXsR5WaHxxM9
# ON 1(RX), 2(TX); 13 (GND) , 19 (PWR), 36 (3,3V OUT) , 38 (GND), 39 (VSYS)  â†’ AT OK, LED Blinky langsam
# wegen wifi: https://peppe8o.com/getting-started-with-wifi-on-raspberry-pi-pico-w-and-micropython/

from machine import Pin, ADC , WDT
from machine import UART

import machine
import os
import utime
import binascii
from machine import Pin
import os
#import picosleep
import json
import re
import network
import ubinascii

class WdtDummy:
  
  def feed(self):
    print("feed")



pwr14 = 4  #pin to control the power of the module
wake_up = 17   
uart_port = 0
uart_baute = 115200
#uart = machine.UART(uart_port, uart_baute, bits=8, parity=None, stop=1)
uart = UART(1, baudrate=115200,bits=8, parity=None, stop=1, tx=21, rx=47)

led = Pin(17, Pin.OUT)

if not ("count.txt" in os.listdir()):
    f = open('count.txt','w')
    f.write(str(0))

def readStatus():
    try:
        #file = open('status.json','a+')
        f = open('status.json',"r+")
        serialzed=f.read()
        #print(serialzed)   
        status = eval(serialzed)
        #print("deserialized "+status)
    except:
        status={"sleeptime":100,"lastwifis":[],"lastwifiswithgps":[],"notmoving":False}
    return status

def writeStatus(status):
    print("writeStatus")
    print(str(status))
    file = open('status.json','a+')
    f = open('status.json',"w+")
    f.write(str(status))
    return 

def logCall():
    f = open('count.txt',"r")
    x=int(f.read())
    f.close()
    print(x)
    f = open('count.txt','w')
    f.write(str(x+1))    
    f.close()
    return x+1

# zum power toggle muss offenbar 0_1_0 auf GPIO 14 gemacht werden
def toggleOnOff():
    #bei aufsteigender Flanke wird immer On Off getoggelt
    machine.Pin(pwr14, machine.Pin.OUT).value(0)
    utime.sleep(2)
    wdt.feed()
    machine.Pin(pwr14, machine.Pin.OUT).value(1)
    utime.sleep(2)
    wdt.feed()
    #print(waitResp_info()  )
    machine.Pin(pwr14, machine.Pin.OUT).value(0)
    utime.sleep(2)
    wdt.feed()
    #print(waitResp_info()  )

        
def waitResp_info():
    prvMills = utime.ticks_ms()
    info = b""
    while (utime.ticks_ms()-prvMills)<2000:        
        if uart.any():
            info = b"".join([info, uart.read(1)])
    #print(info)
    return info.replace(b'\xFE', b'').replace(b'\xFF', b'').decode()

def assertModemOn():
    c=0
    while True:
        c=c+1
        if(c>10):
            break
        uart.write( 'AT\r\n'.encode() )
        utime.sleep(2)
        wdt.feed()
        uart.write( 'AT\r\n'.encode() )
        recBuff = waitResp_info()
        #falls modem schon eingeschaltet ist
        if 'OK' in recBuff:
            print ("modem schon eingeschaltet")
            break
        else:
            print("modem ist noch ausgeschaltet -> toggleOnOff() ")
            toggleOnOff()
            utime.sleep(2)
            wdt.feed()
            
def assertModemOff():
    c=0
    while True:
        c=c+1
        if(c>10):
            break       
        uart.write( 'AT\r\n'.encode() )
        utime.sleep(2)
        wdt.feed()
        uart.write( 'AT\r\n'.encode() )
        recBuff = waitResp_info()
        #falls modem schon eingeschaltet ist
        if 'OK' in recBuff:
            print ("modem noch eingeschaltet -> toggleOnOff()")
            toggleOnOff()
            utime.sleep(2)
            wdt.feed()
            print("Erwarte 'NORMAL POWER DOWN' Message")
            utime.sleep(3)
            wdt.feed()
            print(waitResp_info() )
        else:
            print ("modem ist jetzt ausgeschaltet  ")
            break
            
        
        

def getGpsInfo(woerterbuch):
    #return "AT+CGNSINF +CGNSINF: 1,1,20220223101738.000,50.902806,6.851354,44.137,0.00,,0,,0.9,1.3,0.9,,11,,6.6,12.0 OK"
    # Coords = 50.902806,6.851354,44.137
   
    print('Start GPS session...')
    uart.write('AT+CGNSPWR=1\r\n'.encode())
    utime.sleep(2)
    wdt.feed()
    print(waitResp_info())
    woerterbuch['geocoords']=[-1.0,-1.0,-1.0]
    for i in range(1,10):
        rec_buff = b''
        uart.write( 'AT+CGNSINF\r\n'.encode() )
        utime.sleep(2)
        wdt.feed()
        rec_buff = waitResp_info()
        if ',,,,' in rec_buff:
            print('GPS is not yet ready, loop '+str(i)+': ' +rec_buff)          
            utime.sleep(1)
            wdt.feed()
            continue
        else:
           print('My GPS position '+rec_buff)           
           pattern = re.compile(r'\d+\.\d\d\d\d\d\d,\d+\.\d\d\d\d\d\d,\d+\.\d\d\d')
           x = pattern.search(rec_buff)
           #print(x.group(0))
           try:
               woerterbuch['geocoords']=json.loads("["+x.group(0)+"]")
           except:
               print("gps parse error")
           break
        
    uart.write('AT+CGNSPWR=0\r\n'.encode())
    utime.sleep(2)
    wdt.feed()
    print(waitResp_info())
    return woerterbuch
    



def mqttPublish(ccid,data,runde):
   
    for i in range(1,5):
        data["count"]=str(runde)+'.'+str(i)
        ####
        # mqtt initialisieren
        ###
        # MQTT Server info
        mqtt_host = '91.228.53.41'           
        mqtt_port = '1883'

        #uart.write(('AT+SMCONF=\"URL\",'+mqtt_host+','+mqtt_port+'\r\n').encode() )
        sendAt('AT+SMCONF=\"URL\",'+mqtt_host+','+mqtt_port,"OK")
        #sendAt('AT+SMCONF=\"USERNAME\",\"christor\"','OK',2000)
        #sendAt('AT+SMCONF=\"PASSWORD\",\"Christor#123\"','OK',2000)
        #uart.write(('AT+SMCONF=\"KEEPTIME\",600\r\n').encode() )
        sendAt('AT+SMCONF=\"KEEPTIME\",600',"OK")
        #uart.write(('AT+SMCONF=\"CLIENTID\",\"'+ccid+'\"\r\n').encode() )
        sendAt('AT+SMCONF=\"CLIENTID\",\"'+ccid+'\"',"OK")
        #uart.write(('AT+SMCONN\r\n').encode() )
        sendAt('AT+SMCONN',"OK")
        #sendAt('AT+SMSUB=\"testtopic\",1','OK',5000)
        
        ##############
        # mqtt message absenden
        ##############
        jsonStr = json.dumps(data)
        print(jsonStr)
        message=str(jsonStr)
        #verwende ccid als topic
        publishCommand = 'AT+SMPUB=\"device/'+ccid+'\",'+str(len(message))+',1,0'
        print("publish")
        
        sendAt(publishCommand,"OK")

        
        uart.write(message.encode())
        utime.sleep(2);
        wdt.feed()
        utime.sleep(2);
        wdt.feed()
        utime.sleep(2);
        wdt.feed()
        print(waitResp_info())
        print("published")
        
        
        # verbindung beende
