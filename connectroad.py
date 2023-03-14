import sys, time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLCDNumber, QMainWindow
from PySide6.QtCore import *
from PySide6.QtMultimedia import *
from PySide6.QtGui import *
import random, json
from serial import Serial
# import pygame

# level별 데이터셋 받는 기능 설정


def check_score(img_path, answer, input_index, correct_answer, 
                correctsound, incorrectsound, rightcount, wrongcount):
        if correct_answer == img_path:
            if input_index == answer:
                correctsound.play()
                rightcount += 1
                print('right')
            else:
                incorrectsound.play()
                wrongcount += 1
                print('wrong')


class ConnectRoad(QWidget):
    def __init__(self, arduino, rfid_map, level= 'easy', cnt= 3):
        super().__init__()
        self.piclist = ["src/examples/test1.PNG",  
                    "src/examples/test2.PNG",
                    "src/examples/test3.PNG", 
                    "src/examples/test4.PNG", 
                    "src/examples/test5.PNG",
                    "src/examples/test6.PNG",
                    "src/examples/test7.PNG", 
                    "src/examples/test8.PNG",
                    "src/examples/test9.PNG", 
                    "src/examples/test10.PNG",
                    "src/examples/test11.PNG", 
                    "src/examples/test12.PNG",
                    "src/examples/test13.PNG"]
        self.arduino = arduino
        self.rfid_map = rfid_map
        self.level = level
        self.cnt = cnt

        self.rightcount = 0
        self.wrongcount = 0

        self.initialize_game_ui(arduino, rfid_map)
        self.resize(1600,900)
        print(1)
        self.show()
        time.sleep(5)
        print(2)

    def initialize_game_ui(self, arduino, rfid_map):
        # 게임 스코어
        self.initialize_score_ui()

        # 맞춰야할 문제 
        self.initialize_question_ui()

        # 게임 진행
        self.in_game_ui(arduino, rfid_map)
        

    def initialize_score_ui(self):
        self.setWindowTitle("Connect Road")
        # 게임 스코어 띄우기
        rightLabel = QLabel("정답:")
        wrongLabel = QLabel("오답:")

        self.right_lcd = QLCDNumber(self, 5)
        self.right_lcd.setDigitCount(5)
        self.right_lcd.setSegmentStyle(QLCDNumber.Filled)
        self.right_lcd.move(430,850)

        self.wrong_lcd = QLCDNumber(self, 5)
        self.wrong_lcd.setDigitCount(5)
        self.wrong_lcd.setSegmentStyle(QLCDNumber.Filled)
        self.wrong_lcd.move(1230,850)

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(rightLabel)
        hbox1.addStretch(2)
        hbox1.addWidget(wrongLabel)
        hbox1.addStretch(1)

        # 방향사진 띄우기
        left_img = QPixmap('src/icon/LEFT.PNG')
        front_img = QPixmap('src/icon/FRONT.PNG')
        right_img = QPixmap('src/icon/RIGHT.PNG')

        left_answer = QLabel(self)
        left_answer.setPixmap(left_img)

        front_answer = QLabel(self)
        front_answer.setPixmap(front_img)

        right_answer = QLabel(self)
        right_answer.setPixmap(right_img)

        self.hbox2 = QHBoxLayout()
        self.hbox2.addStretch(1)
        self.hbox2.addWidget(left_answer)
        self.hbox2.addStretch(1)
        self.hbox2.addWidget(front_answer)
        self.hbox2.addStretch(1)
        self.hbox2.addWidget(right_answer)
        self.hbox2.addStretch(1)

        self.vbox1 = QVBoxLayout()
        self.vbox1.addStretch(12)
        self.vbox1.addLayout(self.hbox2)
        self.vbox1.addStretch(1)
        self.vbox1.addLayout(hbox1)
        self.vbox1.addStretch()

        self.setLayout(self.vbox1)
    
    def initialize_question_ui(self):
        i = random.randint(0,5)
        road_img = QPixmap(f'{self.piclist[i]}')

        self.correct_answer = self.piclist[i]
        
        # 맞춰야할 문제 띄우기
        road_answer = QLabel(self)
        road_answer.setPixmap(road_img)
        road_answer.setGeometry(500,10, 550, 550)
        
    def in_game_ui(self, arduino, rfid_map):
        pygame.mixer.init()
        correctsound = pygame.mixer.Sound("src/sounds/correct.mp3")
        incorrectsound = pygame.mixer.Sound("src/sounds/incorrect.mp3")

        rfid_map_keys = list(rfid_map.keys())
        arduino_input = None
        buf = ""

        # 아두이노 태그
        if arduino.readable():
                arduino_input = arduino.readline().decode().strip()

        if arduino_input:
            if arduino_input != buf:
                print(arduino_input)
                buf = arduino_input
                try:
                    input_index = rfid_map_keys.index(arduino_input)  
                except:
                    pass

                check_score("src/examples/test1.PNG", 1, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)
                check_score("src/examples/test2.PNG", 0, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)                
                check_score("src/examples/test3.PNG", 2, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)                
                check_score("src/examples/test4.PNG", 1, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)                
                check_score("src/examples/test5.PNG", 2, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)                
                check_score("src/examples/test6.PNG", 1, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)
                check_score("src/examples/test7.PNG", 1, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)
                check_score("src/examples/test8.PNG", 1, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)
                check_score("src/examples/test9.PNG", 0, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)
                check_score("src/examples/test10.PNG", 1, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)
                check_score("src/examples/test11.PNG", 0, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)
                check_score("src/examples/test12.PNG", 2, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)
                check_score("src/examples/test13.PNG", 0, input_index, 
                            correctsound, incorrectsound, self.rightcount, self.wrongcount)

            if self.rightcount == self.cnt:
                Result()


class Result(ConnectRoad):
    def __init__(self):
        super().__init__()
        self.resultUI()

    def resultUI(self):
        self.setWindowTitle('Show_Result')

        result_text1 = QLabel("결과", self)
        result_text2 = QLabel(f"정답 {self.rightcount}개 \t 오답 {self.wrongcount} 개", self)

        font = QFont()
        font.setPointSize(36)

        result_text1.setFont(font)
        result_text2.setFont(font)

        result_text1.setAlignment(Qt.AlignCenter)
        result_text2.setAlignment(Qt.AlignCenter)

        result_text1.setFixedSize(500,500)
        result_text2.setFixedSize(700,700)

        self.resize(1650, 950)
        self.show()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = ConnectRoad()
#     ex.show()
#     sys.exit(app.exec())