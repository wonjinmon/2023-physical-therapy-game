import serial
from serial import Serial
from serial.tools import list_ports
import json

from portfinder import macAddfinder

def scan(arduino):
    buf = ""

    print("scan started")
    while True:
        if arduino.readable():
            arduino_input = arduino.readline().decode().strip()
            if arduino_input:
                if arduino_input != buf:
                    print(arduino_input)
                    buf = arduino_input
                    
with open("./CFG_show.json", "r", encoding='UTF-8') as cfg:
    cfg = json.load(cfg)
    RFID_BTMACID = cfg['BTMACID']

hc06_port = macAddfinder(macAddress=RFID_BTMACID)

arduino = Serial(
    port=hc06_port,
    baudrate=9600,
    timeout=0.1)

scan(arduino)   