# New Requirements 09.10.2023
https://docs.google.com/document/d/1QbcJ9q0AnhmWYFL9N2yTIqmDUzpVPqicOUhr_ns5_PE/edit

ESP32

https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
# Enclosure 
https://www.shinyenclosure.com/
# pirmicboard_david
 repository for interchanging files and test code

## Enter Flash Mode
Bridge GND with GPIO0 via Jumper Cable
![Flashing](flashing.png)

## Write Flash

```
esptool.exe --chip esp32s3 --port COM4 write_flash -z 0 GENERIC_S3-20220618-v1.19.1.bin
```
![Flashing](writeflash.png)
* unplug from USB port
* reconnect with Putty Terminal Software ( https://www.putty.org/ )

