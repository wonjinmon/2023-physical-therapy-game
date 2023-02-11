import serial
from serial import Serial
from serial.tools import list_ports 


def macAddfinder(macAddress):
    dev = list_ports.comports()
    port=[]
    result = ''
    
    for com in dev:
        port.append((com.device, com.hwid))
        
    for device in port:
        if macAddress in device[1]:
            result = str(device[0])

    print(f"Bluetooth MAC Address is {macAddress} \nDevice detected serial ports: {result}")

    return result
    