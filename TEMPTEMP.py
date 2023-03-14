import sys, time
from PySide6.QtWidgets import QApplication, QWidget,QVBoxLayout, QHBoxLayout, QLabel, QLCDNumber, QPushButton
from PySide6.QtCore import *
from PySide6.QtMultimedia import *
from PySide6.QtGui import *
import pygame, time, random, json
from serial import Serial


pygame.mixer.init()
correctsound = pygame.mixer.Sound("src/sounds/correct.mp3")
incorrectsound = pygame.mixer.Sound("src/sounds/incorrect.mp3")


def digitspan_game(num_ques, num_cards, arduino ,rfid_map, sounds, rightcount, wrongcount):
    idxList = list(rfid_map.values())
    assert num_ques <= len(idxList)

    randomChoices = random.sample(idxList, num_ques)
    rfid_map_keys = list(rfid_map.keys())
    arduino_input = None
    buf = ""
    i = 0
    cnt = 0
    temp_inputs =[]

    tmp =""
    for digitstr in randomChoices:
        tmp += str(digitstr)

        sounddir = sounds[digitstr]
        digitsound = pygame.mixer.Sound(sounddir)
        digitsound.play()
        time.sleep(1)
        digitsound.stop()

    running = True
    while running:
        for _ in range(num_cards):
            # 아두이노 태그
            if arduino.readable():
                arduino_input = arduino.readline().decode().strip()

            if arduino_input:
                if arduino_input != buf:
                    print(arduino_input)
                    buf = arduino_input
                    try:
                        input_index = rfid_map_keys.index(arduino_input)
                        temp_inputs.append(input_index)
                    except:
                        continue

                    # if 못맞추면~
                    if input_index != randomChoices[i]:
                        incorrectsound.play()
                        wrongcount += 1
                        print('wrong')
                        return 0
                    elif input_index == randomChoices[i]:
                        correctsound.play()
                        rightcount += 1
                        print('right')
                        return 1
                
                elif arduino_input == buf:
                    if cnt > 10:
                        buf = arduino_input
                        try:
                            input_index = rfid_map_keys.index(arduino_input)
                            temp_inputs.append(input_index)
                        except:
                            continue

                        # if 못맞추면~
                        if input_index != randomChoices[i]:
                            incorrectsound.play()
                            wrongcount += 1
                            print('right')
                            return 0
                        elif input_index == randomChoices[i]:
                            correctsound.play()
                            rightcount += 1 
                            return 1
                    else:
                        cnt += 1

                if len(temp_inputs) == len(randomChoices):
                    running = False
            
