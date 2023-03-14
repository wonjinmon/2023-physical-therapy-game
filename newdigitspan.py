# 옵션 forward, backward, mixed 중 택 1 ...(O)
# >> category 별 문제 셋팅 해야함

# 화면에 숫자 X , 소리만 들리도록 ...(O)

# 2자리 수 >> 3자리 수 >> 4자리 수 ,,, 오름차순
# 2자리 수에서 정답률 N % 이상이면 다음 자리 수로 난이도 증가 >>> 3개중 2개 이상 맞추면

import sys, time
from PySide6.QtWidgets import QApplication, QWidget,QVBoxLayout, QHBoxLayout, QLabel, QLCDNumber, QPushButton
from PySide6.QtCore import *
from PySide6.QtMultimedia import *
from PySide6.QtGui import *
import pygame, time, random, json
from serial import Serial


class DigitSpan(QWidget):
    def __init__(self, arduino, rfid_map, category= 'Forward', num_cards= 3):
    # def __init__(self):
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
        self.arduino =arduino
        self.rfid_map = rfid_map
        self.category = category
        self.num_cards = num_cards

        self.init_GameUI()
        self.gaming(self.arduino, self.rfid_map, self.category, self.num_cards)

    # 게임 화면 구성
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

        btn1 = QPushButton(self)
        btn1.setText("그만하기")
        btn1.clicked.connect(self.btn1Function)
        
        if self.category == 'Forward':
            self.forwardmessage = QLabel("정방향 태그를 시작합니다", self)
            self.forwardmessage.setGeometry(250,100, 600,200)
            font = self.forwardmessage.font()
            font.setPointSize(30)
            self.forwardmessage.setFont(font)

        # if self.category == 'Backward':
        #     self.backwardmessage = QLabel("역방향 태그를 시작합니다", self)
        #     self.backwardmessage.setGeometry(250,100, 600,200)
        #     font = self.backwardmessage.font()
        #     font.setPointSize(30)
        #     self.backwardmessage.setFont(font)

        # if self.category == 'Mixed':
        #     self.mixedmessage = QLabel("역방향 태그를 시작합니다", self)
        #     self.mixedmessage.setGeometry(250,100, 600,200)
        #     font = self.mixedmessage.font()
        #     font.setPointSize(30)
        #     self.mixedmessage.setFont(font)

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

        # 시간 재기
        self.timer = QTimer()
        self.timer.timeout.connect(self.counting)
        self.timer.start(1000)

        # 게임 시작 알림 메세지 숨기기
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.forwardmessage.hide)
        self.timer2.start(3000)

        self.resize(1600, 900)
        self.show()

    # 시간 재기
    def counting(self):
        self.second += 1
        self.time_lcd.display(self.second)
    
    # 종료버튼 기능
    def btn1Function(self):
        self.ending = Result(self.arduino, self.rfid_map, self.rightcount, self.wrongcount)
        self.ending.resultUI()

# 게임 구현
    def gaming(self, arduino, rfid_map, category, num_cards=3):
        
        pygame.mixer.init()
        forwardsound = pygame.mixer.Sound('src/sounds/digit_span/forward.mp3')
        backwardsound = pygame.mixer.Sound('src/sounds/digit_span/backward.mp3')
        mixedsound = pygame.mixer.Sound('src/sounds/digit_span/mixedward.mp3')

        if category =='forward':
            forwardsound.play()
        if category == 'backward':
            backwardsound.play()
        if category == 'mixed':
            mixedsound.play()

        # 단계를 카운팅 (숫자의 개수 2,,3,,4,,5,,)
        step_count = 0

        #         # 다음단계로 이동
        # step_count += digitspan_game(2, 3, arduino, rfid_map, self.sounds, self.rightcount, self.wrongcount)
        # if step_count >= 2:
        #     ...


        while True:
            if step_count >= 2:
                break
            step_count += digitspan_game(3, 3, arduino, rfid_map, self.sounds, self.rightcount, self.wrongcount)

        # while True:
        #     if step_count >= 2:
        #         break
        #     step_count += digitspan_game(4, 3, arduino, rfid_map, self.sounds, self.rightcount, self.wrongcount)

        # while True:
        #     if step_count >= 2:
        #         break
        #     step_count += digitspan_game(5, 3, arduino, rfid_map, self.sounds, self.rightcount, self.wrongcount)

        # while True:
        #     if step_count >= 2:
        #         break
        #     step_count += digitspan_game(6, 3, arduino, rfid_map, self.sounds, self.rightcount, self.wrongcount)

        # while True:
        #     if step_count >= 2:
        #         break
        #     step_count += digitspan_game(7, 3, arduino, rfid_map, self.sounds, self.rightcount, self.wrongcount)

        # while True:
        #     if step_count >= 2:
        #         break
        #     step_count += digitspan_game(8, 3, arduino, rfid_map, self.sounds, self.rightcount, self.wrongcount)

        # while True:
        #     if step_count >= 2:
        #         break
        #     step_count += digitspan_game(9, 3, arduino, rfid_map, self.sounds, self.rightcount, self.wrongcount)


# 결과
class Result(DigitSpan):
    def __init__(self, arduino, rfid_map, rightcount, wrongcount):
        super().__init__(arduino, rfid_map)
        self.arduino = arduino
        self.rfid_map = rfid_map
        self.rightcount = rightcount
        self.wrongcount = wrongcount

        self.resultUI()

    def resultUI(self):
        self.setWindowTitle('Your_Result!')

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

        # 게임 멈추는 기능 추가 필요


# 게임 구현 
# def digitspan_game(num_ques, num_cards, arduino ,rfid_map, sounds, rightcount, wrongcount):
#     pygame.mixer.init()
#     correctsound = pygame.mixer.Sound("src/sounds/correct.mp3")
#     incorrectsound = pygame.mixer.Sound("src/sounds/incorrect.mp3")

#     idxList = list(rfid_map.values())
#     assert num_ques <= len(idxList)

#     randomChoices = random.sample(idxList, num_ques)
#     rfid_map_keys = list(rfid_map.keys())
#     arduino_input = None
#     buf = ""
#     i = 0
#     cnt = 0
#     temp_inputs =[]

#     tmp =""
#     for digitstr in randomChoices:
#         tmp += str(digitstr)

#         sounddir = sounds[digitstr]
#         digitsound = pygame.mixer.Sound(sounddir)
#         digitsound.play()
#         time.sleep(1)
#         digitsound.stop()

#     running = True
#     while running:
#         for _ in range(num_cards):
#             # 아두이노 태그
#             if arduino.readable():
#                 arduino_input = arduino.readline().decode().strip()

#             if arduino_input:
#                 if arduino_input != buf:
#                     print(arduino_input)
#                     buf = arduino_input
#                     try:
#                         input_index = rfid_map_keys.index(arduino_input)
#                         temp_inputs.append(input_index)
#                     except:
#                         continue

#                     # if 못맞추면~
#                     if input_index != randomChoices[i]:
#                         incorrectsound.play()
#                         wrongcount += 1
#                         print('wrong')
#                         return 0
#                     elif input_index == randomChoices[i]:
#                         correctsound.play()
#                         rightcount += 1
#                         print('right')
#                         return 1
                
#                 elif arduino_input == buf:
#                     if cnt > 10:
#                         buf = arduino_input
#                         try:
#                             input_index = rfid_map_keys.index(arduino_input)
#                             temp_inputs.append(input_index)
#                         except:
#                             continue

#                         # if 못맞추면~
#                         if input_index != randomChoices[i]:
#                             incorrectsound.play()
#                             wrongcount += 1
#                             print('right')
#                             return 0
#                         elif input_index == randomChoices[i]:
#                             correctsound.play()
#                             rightcount += 1 
#                             return 1
#                     else:
#                         cnt += 1

#                 if len(temp_inputs) == len(randomChoices):
#                     running = False

def digitspan_game(num_ques, num_cards, arduino ,rfid_map, sounds, rightcount, wrongcount):
    pygame.mixer.init()
    correctsound = pygame.mixer.Sound("src/sounds/correct.mp3")
    incorrectsound = pygame.mixer.Sound("src/sounds/incorrect.mp3")

    idxList = list(rfid_map.values())
    assert num_ques <= len(idxList)

    # 랜덤한 숫자 뽑기 (0~9에서 num_que개)
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
                return 0
        
    return 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DigitSpan()
    ex.show()
    sys.exit(app.exec())