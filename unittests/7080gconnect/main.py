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
                   
def getCCID():
    #Get CCID
    uart.write("AT+CCID\r\n".encode())
    utime.sleep(2)

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

            
    return str(ccid)    

#Send AT command
def sendAt(cmd,back,timeout=1000):
    uart.write((cmd+'\r\n').encode())
    utime.sleep(2)
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
   
    sendAt("AT+CFUN=0","OK")
   
    
    #https://www.twilio.com/docs/iot/supersim/cellular-modem-knowledge-base/simcom-supersim
    #If you wish to limit comms to LTE only, i.e., no GSM, send AT+CNMP=38.
    sendAt("AT+CNMP=38","OK")      #Select LTE mode

    #https://www.twilio.com/docs/iot/supersim/cellular-modem-knowledge-base/simcom-supersim
    #Set the modemâ€™s Radio Access Technology (RAT) preference to Cat-M1 when you are connecting to LTE. To do so, issue AT+CMNB=1.
    sendAt("AT+CMNB=2","OK")       #Select NB-IoT mode,if Cat-Mï¼Œplease set to 1

    utime.sleep(2)

    sendAt("AT+CFUN=1","OK")
    utime.sleep(2)

        
    ci=0
    while True:
        ci=ci+1
        if(ci>10):
            print('------RESET Modem wont go online------\r\n')
            machine.reset()
        if sendAt("AT+CGATT?", "+CGATT: 1"):
            print('------SIM7080G is online------\r\n')
            break
        else:
            print('------SIM7080G is offline, please wait...------\r\n')
            utime.sleep(2)
            continue
        
    #AT+CSQ AT command returns the signal strength of the device.
    #https://m2msupport.net/m2msupport/atcsq-signal-quality/
    sendAt("AT+CSQ","OK")

    #AT+CPSI command is used to return UE system information.
    #https://m2msupport.net/m2msupport/atcpsi-inquiring-ue-system-information/
    sendAt("AT+CPSI?","OK")

    #AT+COPS AT command forces the mobile terminal to select and register the GSM/UMTS/EPS network.
    #The device returns the list of networks that are avaialble to connect.
    #https://m2msupport.net/m2msupport/atcops-plmn-selection/
    sendAt("AT+COPS?","OK")

    #Verify that APN is assigned using  the AT+CGNAPN comman
    sendAt("AT+CGNAPN","OK")


    #Activate a data connection: AT+CNACT=0,1
    sendAt('AT+CNACT=0,1','OK')
    #Optionally, obtain an IP address and the current connection status with
    sendAt('AT+CNACT?','OK')

    #sendAt("AT+CPSI?","OK")

def mqttPublish(ccid):
    print("mqttPublish")
   
    
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
   
    message="my test message"
    #verwende ccid als topic
    publishCommand = 'AT+SMPUB=\"device/'+ccid+'\",'+str(len(message))+',1,0'
    print("publishing")
    
    sendAt(publishCommand,"OK")

    uart.write(message.encode())
    utime.sleep(2);
    
    utime.sleep(2);
    
    utime.sleep(2);
    
    print(waitResp_info())
    print("published")
    
    
    # verbindung beenden
    uart.write( 'AT+SMDISC\r\n'.encode() )
    utime.sleep(2)
    
    print(waitResp_info())


print("assertModemOn --> Power On")
modemon=assertModemOn()
if modemon:
    print("SUCCESS MODEM ON !")
else:
    print("FAILURE !!")

ccid = getCCID()
## if ccid is printed then sim card was read succesfully
print('CCID: '+ccid)

checkNetwork()

mqttPublish(ccid)


