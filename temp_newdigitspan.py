# 옵션 forward, backward, mixed 중 택 1 ...(O)
# >> category 별 문제 셋팅 해야함

# 화면에 숫자 X , 소리만 들리도록 ...(O)

# 2자리 수 >> 3자리 수 >> 4자리 수 ,,, 오름차순
# 2자리 수에서 정답률 N % 이상이면 다음 자리 수로 난이도 증가 >>> 3개중 2개 이상 맞추면

import sys
from PySide6.QtWidgets import QApplication, QWidget,QVBoxLayout, QHBoxLayout, QLabel, QLCDNumber
from PySide6.QtCore import *
from PySide6.QtMultimedia import *
from PySide6.QtGui import *
import pygame, time, random

# def answpsorl(arduino, rfid_map, category):
#     pass


class DigitSpan(QWidget):
    # def __init__(self, arduino, rfid_map, category= 'Forward', num_cards= 3):
    def __init__(self):
        super().__init__()
        self.second = 0
        self.progresscount = 0
        self.rightcount = 0
        self.wrongcount = 0
        self.sounds = [
            "src/sounds/digit_span/zero.wav",
            "src/sounds/digit_span/one.wav",
            "src/sounds/digit_span/two.wav",
            "src/sounds/digit_span/three.wav",
            "src/sounds/digit_span/four.wav",
            "src/sounds/digit_span/five.wav",
            "src/sounds/digit_span/six.wav",
            "src/sounds/digit_span/seven.wav",
            "src/sounds/digit_span/eight.wav",
            "src/sounds/digit_span/nine.wav"]
        self.init_GameUI()
        self.gaming()


    def init_GameUI(self):
        self.setWindowTitle('Digit Span')

        timeLabel = QLabel('진행시간: ')
        progressLabel= QLabel('진행률: ')
        wrongLabel = QLabel('오답: ')

        self.time_lcd = QLCDNumber(self, 5)
        self.time_lcd.setDigitCount(5)
        self.time_lcd.setSegmentStyle(QLCDNumber.Filled)
        self.time_lcd.move(240,570)
        self.time_lcd.display(self.second)

        self.progress_lcd = QLCDNumber(5)
        self.progress_lcd.setSegmentStyle(QLCDNumber.Filled)
        # self.progress_lcd.display(self.i / len(self.randomChoices)*100)
        
        self.wrong_lcd = QLCDNumber(self, 5)
        self.wrong_lcd.setDigitCount(5)
        self.wrong_lcd.setSegmentStyle(QLCDNumber.Filled)
        self.wrong_lcd.move(700,570)
        # self.wrong_lcd.display(self.wrongcount)
        
        self.forwardmessage = QLabel("정방향 태그를 시작합니다", self)
        self.forwardmessage.setGeometry(250,100, 600,200)
        font = self.forwardmessage.font()
        font.setPointSize(30)
        self.forwardmessage.setFont(font)

        # self.backwardmessage = QLabel("역방향 태그를 시작합니다", self)
        # self.backwardmessage.setGeometry(250,100, 600,200)
        # font = self.backwardmessage.font()
        # font.setPointSize(30)
        # self.backwardmessage.setFont(font)

        # self.mixedmessage = QLabel("역방향 태그를 시작합니다", self)
        # self.mixedmessage.setGeometry(250,100, 600,200)
        # font = self.mixedmessage.font()
        # font.setPointSize(30)
        # self.mixedmessage.setFont(font)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(timeLabel)
        hbox.addStretch(2)
        hbox.addWidget(progressLabel)
        hbox.addStretch(2)
        hbox.addWidget(wrongLabel)
        hbox.addStretch(2)

        vbox = QVBoxLayout()
        vbox.addStretch(10)
        vbox.addLayout(hbox)
        vbox.addStretch(0.5)

        self.setLayout(vbox)

        self.timer = QTimer()
        self.timer.timeout.connect(self.counting)
        self.timer.start(1000)

        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.forwardmessage.hide)
        self.timer2.start(3000)

        self.resize(900, 600)
        self.show()

    def counting(self):
        self.second += 1
        self.time_lcd.display(self.second)

# num_cards = 문제 수 (3개)
    def gaming(self, arduino, rfid_map, category, num_cards=3):
        
        num_ques = 2

        pygame.mixer.init()
        forwardsound = pygame.mixer.Sound('src/sounds/digit_span/forward.mp3')
        # backwardsound = pygame.mixer.Sound('src/sounds/digit_span/backward.mp3')
        # mixedsound = 
        correctsound = pygame.mixer.Sound("src/sounds/correct.mp3")
        incorrectsound = pygame.mixer.Sound("src/sounds/incorrect.mp3")

        forwardsound.play()
        # backwardsound.play()
        # mixedsound.play

        idxList = list(rfid_map.values())
        assert num_ques <= len(idxList)

        # 랜덤한 숫자 뽑기 (0~9에서 num_que개)
        randomChoices = random.sample(idxList, num_ques)

        arduino_input = None
        buf = ""
        i = 0
        rfid_map_keys = list(rfid_map.keys())
        rfid_map_values = list(rfid_map.values())
        
        num_correct = 0
        
        digit1_check = 1
        digit2_check = 1


        # 숫자의 개수 (2,,3,,4,,5,,)
        tmp = ""
        for digitStr in randomChoices:
            tmp += str(digitStr)

            soundDir = self.sounds[digitStr]
            digitSound = pygame.mixer.Sound(soundDir)
            digitSound.play()
            time.sleep(1)
            digitSound.stop()
            # forward_inputs = []
            cnt = 0

            # 아두이노 태그
            if arduino.readable():
                arduino_input = arduino.readline().decode().strip()

            if arduino_input:
                if arduino_input != buf:
                    print(arduino_input)
                    buf = arduino_input
                    try:
                        input_index = rfid_map_keys.index(arduino_input)
                        # forward_inputs.append(input_index)
                    except:
                        continue
                    
                    if input_index == randomChoices[i]:
                        correctsound.play()
                        self.rightcount += 1
                        print('right')
                    else:
                        incorrectsound.play()
                        self.wrongcount += 1
                        print('wrong')
                    i += 1

                elif arduino_input == buf:
                    if cnt > 10:
                        buf = arduino_input
                        try:
                            input_index = rfid_map_keys.index(arduino_input)
                            # forward_inputs.append(input_index)
                        except:
                            continue

                        if input_index == randomChoices[i]:
                            correctsound.play()
                            self.rightcount += 1
                            print('right')
                        else:
                            incorrectsound.play()
                            self.wrongcount += 1
                            print('wrong')
                        cnt = 0
                        i += 1
                    else:
                        cnt += 1

            # 자릿수 마다 맞춘 문제에 대해 정답 처리
            if '별'== digit1_check and '달' == digit2_check:
                num_correct += 1
                
            
            # 2/3 이상 맞췄을 때 다음 단계로..
            if num_correct >= 2:
                num_ques += 1
                ... # 다음 단계 실행 (함수화)

            # 못 맞추면 게임 종료
            else:
                Result()



# 결과
class Result(DigitSpan):
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DigitSpan()
    ex.show()
    sys.exit(app.exec())