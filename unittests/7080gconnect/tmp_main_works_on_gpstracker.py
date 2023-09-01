#01.09.23
#Connections test
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
        
        
        # verbindung beenden
        uart.write( 'AT+SMDISC\r\n'.encode() )
        utime.sleep(2)
        wdt.feed()
        print(waitResp_info())

#Send AT command
def sendAt(cmd,back,timeout=1000):
    #rec_buff = b''
    uart.write((cmd+'\r\n').encode())
    utime.sleep(2)
    wdt.feed()
    recBuff = waitResp_info()
    
    if back in recBuff :
        print("ret 1 " + recBuff+" --")
        return 1   
    else:
        print("ret 0 " + recBuff+" --")
        return 0


def checkNetwork():
    print("checkNetwork")
    # https://m2msupport.net/m2msupport/atcfun-set-phone-functionality/
    # =1 auf volle FunktionalitÃ¤t setzen
    wdt.feed()
    sendAt("AT+CFUN=0","OK")
   
    #utime.sleep(5)
    #wdt.feed()
    #utime.sleep(15)
    #wdt.feed()
    
    #https://www.twilio.com/docs/iot/supersim/cellular-modem-knowledge-base/simcom-supersim
    #If you wish to limit comms to LTE only, i.e., no GSM, send AT+CNMP=38.
    sendAt("AT+CNMP=38","OK")      #Select LTE mode

    #https://www.twilio.com/docs/iot/supersim/cellular-modem-knowledge-base/simcom-supersim
    #Set the modemâ€™s Radio Access Technology (RAT) preference to Cat-M1 when you are connecting to LTE. To do so, issue AT+CMNB=1.
    sendAt("AT+CMNB=2","OK")       #Select NB-IoT mode,if Cat-Mï¼Œplease set to 1
 
    wdt.feed()
    utime.sleep(2)
    wdt.feed()
    
    sendAt("AT+CFUN=1","OK")
    utime.sleep(2)
    wdt.feed()
        
    sendAt("AT+CGATT=1","OK")
    utime.sleep(2)
    for i in range(1, 30):
        print("Runde "+str(i))
        if sendAt("AT+CGATT?", "+CGATT: 1"):
            print('------SIM7080G is online------\r\n')
            break
        else:
            print('------SIM7080G is offline, please wait...------\r\n')
            utime.sleep(2)
            wdt.feed()
            continue
        
    #AT+CSQ AT command returns the signal strength of the device.
    #https://m2msupport.net/m2msupport/atcsq-signal-quality/
    sendAt("AT+CSQ","OK")

    #AT+CPSI command is used to return UE system information.
    #https://m2msupport.net/m2msupport/atcpsi-inquiring-ue-system-information/
    sendAt("AT+CPSI?","OK")
    wdt.feed()

    #AT+COPS AT command forces the mobile terminal to select and register the GSM/UMTS/EPS network.
    #The device returns the list of networks that are avaialble to connect.
    #https://m2msupport.net/m2msupport/atcops-plmn-selection/
    sendAt("AT+COPS?","OK")

    #Verify that APN is assigned using  the AT+CGNAPN comman
    sendAt("AT+CGNAPN","OK")
    wdt.feed()

    #Activate a data connection: AT+CNACT=0,1
    sendAt('AT+CNACT=0,1','OK')
    #Optionally, obtain an IP address and the current connection status with
    sendAt('AT+CNACT?','OK')
    wdt.feed()
    #sendAt("AT+CPSI?","OK")
    
    
# geht bei jedem 2ten durchlauf in den deepsleep modus
def deepSleepWeiche(status):
    if ("deepsleep" in os.listdir()):
        try:
            os.remove('deepsleep')
        except:
            print("except")
        led.off()
        print("state: pico led aus und modem aus und picosleep")
        print("assertModemOff() --> Power Off")
        assertModemOff()
        
        print("picosleep "+str(status["sleeptime"]))
        utime.sleep(2)
        #hier die deepsleep zeit anpassen
        #picosleep.seconds(30)
        #picosleep.seconds(int(status["sleeptime"]))
        #machine.deepsleep(int(status["sleeptime"])*1000)
        machine.deepsleep(60000)
        print("machine reset and dann wieder normal")
        utime.sleep(2)
        machine.reset()
    else:
        print("state: normal")
        try:
            os.mkdir('deepsleep')            
        except:
            print("except mkdir")


def getWiFis():
    wlan_sta = network.WLAN(network.STA_IF)
    wlan_sta.active(True)
    networks = wlan_sta.scan()
    neunetworks=[]
    print(networks)
    for mynetwork in networks:
        neunetwork=[mynetwork[0],ubinascii.hexlify(mynetwork[1]).decode()]
        neunetworks.append(neunetwork)
        #mynetwork[1]=ubinascii.hexlify(mynetwork[1]).decode()
    return neunetworks
    
    
def getCCID():
    #Get CCID
    uart.write("AT+CCID\r\n".encode())
    utime.sleep(2)
    wdt.feed()
    ccidlong = waitResp_info()
    c=0
    ccid=""
    while True:
        c=c+1
        if(c>10):
            break
        try:
            ccid = ccidlong.splitlines()[2]
            break
        except:
            utime.sleep(2)
            wdt.feed()
            
    return str(ccid)


       
#######################################
#on off loop
while True:
    machine.Pin(16, machine.Pin.OUT).value(1)
    print("pico has just started")
    print("Sleep 10s zum start")   
    utime.sleep(10)
    machine.Pin(16, machine.Pin.OUT).value(0)
    print("PICO LED on")
    led.on()      
    
    status=readStatus()
    
    print("lastwifis")   
    print(status['lastwifis'])    
    
    print("Enable WatchDogTimer Dummy")
    wdt = WdtDummy()
    print("Running deepSleepWeiche")
    #deepSleepWeiche(status)
 
    print("Enable WatchDogTimer")
    #wdt = WDT(timeout=8000)
    
    #runde=logCall()
    # Neue Batteriespar Logik
    # falls wifis seit 5 loops beim letzen loop ==> hat sich nicht beweget
      # sleep variable auf lang setzen , annotaton auf stillstand
    # sonst
     #sleep variable auf kurz seten
    
    
  
    
    #wifis in der Umgebgug
    currentWifis=getWiFis()
    
    print("++++check sleept time "+str(currentWifis))
    print("")
    print(str(status["lastwifis"]))
    print("")
    print(currentWifis)
    print("")
    status["sleeptime"] = 100
    status["notmoving"]=False
    # falls die wifis sich nicht verändert haben sleeptime verdoppeln
    if (str(currentWifis) == str(status["lastwifis"]) ):
        print("++++double sleep")
        status["sleeptime"] = min(status["sleeptime"] * 2, 3600)
        status["notmoving"]=True
    #hier kommt die eigentliche Logik
    woerterbuch={'time':utime.localtime()}
    woerterbuch["wifis"]= currentWifis
    status["lastwifis"]=currentWifis    
    writeStatus(status)
    
    print("assertModemOn --> Power On")
    assertModemOn()    

    #check ob Modem wirklich an
    print("Sending AT to check if Modem is on")
    utime.sleep(2)
    wdt.feed()
    uart.write( 'AT\r\n'.encode() )
    utime.sleep(2)
    wdt.feed()
    print(waitResp_info()  )
        

    
    ccid = getCCID();
    print('CCID: '+ccid)
    
    uart.write("AT+CBC\r\n".encode())
    utime.sleep(2)
    wdt.feed()
    battery = waitResp_info()
    woerterbuch["battery"]=battery
    print('battery: '+battery)
    
  
    
    checkNetwork()
    
    woerterbuch["sleeptime"]=status["sleeptime"]
    woerterbuch["notmoving"]=status["notmoving"]
    mqttPublish(ccid,woerterbuch,"")
    
    
    print("Machine reset and dann picosleep")
    utime.sleep(2)
    wdt.feed()
    machine.reset()





