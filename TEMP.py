# 옵션 forward, backward, mixed 중 택 1 ...(O)
# >> category 별 문제 셋팅 해야함

# 화면에 숫자 X , 소리만 들리도록 ...(O)

# 2자리 수 >> 3자리 수 >> 4자리 수 ,,, 오름차순
# 2자리 수에서 정답률 N % 이상이면 다음 자리 수로 난이도 증가 >>> 3개중 2개 이상 맞추면

import sys, time
from PySide6.QtWidgets import QApplication, QWidget,QVBoxLayout, QHBoxLayout, QLabel, QLCDNumber, QPushButton, QStackedWidget
from PySide6.QtCore import *
from PySide6.QtMultimedia import *
from PySide6.QtGui import *
import  time, random, json
from serial import Serial
import playsound


class DigitSpan(QWidget):
    num_digits = 2
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

        

        self.start_sound = {
            'Forward': 'src/sounds/digit_span/forward.mp3',
            'Backward': 'src/sounds/digit_span/backward.mp3',
            'Mixed': 'src/sounds/digit_span/mixedward.mp3'
        }

        playsound.playsound(self.start_sound[self.category])
        self.init_GameUI()
        # time.sleep(10)

        # self.stacked_widget = QStackedWidget()
        # self.gaming()

    # 게임 화면 구성
    def init_GameUI(self):
        self.setWindowTitle('Digit Span')

        timeLabel = QLabel('진행시간: ')
        # progressLabel= QLabel('진행률: ')
        wrongLabel = QLabel('오답: ')

        self.time_lcd = QLCDNumber(self, 5)
        self.time_lcd.setDigitCount(5)
        self.time_lcd.setSegmentStyle(QLCDNumber.Filled)
        self.time_lcd.move(240,570)
        self.time_lcd.display(self.second)
        # self.time_lcd.show()

        # self.progress_lcd = QLCDNumber(5)
        # self.progress_lcd.setSegmentStyle(QLCDNumber.Filled)
        # self.progress_lcd.display(self.i / len(self.randomChoices)*100)
        
        self.wrong_lcd = QLCDNumber(self, 5)
        self.wrong_lcd.setDigitCount(5)
        self.wrong_lcd.setSegmentStyle(QLCDNumber.Filled)
        self.wrong_lcd.move(700,570)
        # self.wrong_lcd.display(self.wrongcount)
        # self.wrong_lcd.show()

        self.forwardmessage = QLabel("정방향 태그를 시작합니다", self)
        # self.forwardmessage.move(400, 200)
        self.forwardmessage.setGeometry(250,100, 600,200)
        font = self.forwardmessage.font()
        font.setPointSize(30)
        self.forwardmessage.setFont(font)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(timeLabel)
        hbox.addStretch(2)
        # hbox.addWidget(progressLabel)
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

        self.resize(1600, 900)
        self.show()
    # 시간 재기
    def counting(self):
        self.second += 1
        self.time_lcd.display(self.second)
    
    # 종료버튼 기능
    def btn1Function(self):
        self.ending = Result()
        self.ending.resultUI()

# 게임 구현
# 230314 19:07 이여름
    def gaming(self, num_cards=3):
        correctsound = "src/sounds/correct.mp3"
        incorrectsound = "src/sounds/incorrect.mp3"

        idxList = list(self.rfid_map.values())
        assert self.num_digits <= len(idxList) 

        rfid_map_keys = list(self.rfid_map.keys())
        arduino_input = None
        buf = ""
        i = 0
        cnt = 0
        temp_inputs = []

        wrongcount = 0

        if self.num_digits > 10:
            Result()
            return

        for _ in range(num_cards):
            # 랜덤한 숫자 뽑기 (0~9에서 num_digits개)
            randomChoices = random.sample(idxList, self.num_digits)
            category = random.choice(['Forward', 'Backward']) if self.category == 'Mixed' else self.category
            randomChoices = reversed(randomChoices) if category == 'Backward' else randomChoices

            tmp = ""
            for digitstr in randomChoices:
                # widget = QWidget()
                # self.stacked_widget.addWidget(self.init_GameUI(widget))
                tmp += str(digitstr)

                sounddir = self.sounds[digitstr]
                playsound.playsound(sounddir)
                
            # 아두이노 태그
            if self.arduino.readable():
                arduino_input = self.arduino.readline().decode().strip()

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
                    elif input_index == randomChoices[i]:
                        correctsound.play()
                        print('right')
                    # widget = QWidget()
                    # self.stacked_widget.addWidget(self.init_GameUI(widget))
                
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
                            print('wrong')
                        elif input_index == randomChoices[i]:
                            correctsound.play()
                            print('right')
                    else:
                        cnt += 1
                    # widget = QWidget()
                    # self.stacked_widget.addWidget(self.init_GameUI(widget))
            
            if wrongcount > 1:
                self.wrongcount += 1
            else:
                self.rightcount += 1
            # widget = QWidget()
            # self.stacked_widget.addWidget(self.init_GameUI(widget))

        if self.rightcount / num_cards >= 0.67:
            return self.gaming(self.num_digits+1)
        else:
            return self.gaming(self.num_digits)



# 결과
class Result(DigitSpan):
    def __init__(self):
        super().__init__()
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

        self.resize(1600, 900)
        self.show()


# # 게임 구현 
# def digitspan_game(num_ques, num_cards, arduino ,rfid_map, sounds, rightcount, wrongcount):
#     pygame.mixer.init()
#     correctsound = pygame.mixer.Sound("src/sounds/correct.mp3")
#     incorrectsound = pygame.mixer.Sound("src/sounds/incorrect.mp3")

#     idxList = list(rfid_map.values())
#     assert num_ques <= len(idxList)

#     # 랜덤한 숫자 뽑기 (0~9에서 num_que개)
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

#     for _ in range(num_cards):
#         # 아두이노 태그
#         if arduino.readable():
#             arduino_input = arduino.readline().decode().strip()

#         if arduino_input:
#             if arduino_input != buf:
#                 print(arduino_input)
#                 buf = arduino_input
#                 try:
#                     input_index = rfid_map_keys.index(arduino_input)
#                     temp_inputs.append(input_index)
#                 except:
#                     continue

#                 # if 못맞추면~
#                 if input_index != randomChoices[i]:
#                     incorrectsound.play()
#                     wrongcount += 1
#                     print('wrong')
#                     return 0
#                 elif input_index == randomChoices[i]:
#                     correctsound.play()
#                     rightcount += 1
#                     print('right')
#                     return 1
            
#             elif arduino_input == buf:
#                 if cnt > 10:
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
#                         print('right')
#                         return 0
#                     elif input_index == randomChoices[i]:
#                         correctsound.play()
#                         rightcount += 1 
#                         return 1
#                 else:
#                     cnt += 1

#             if len(temp_inputs) == len(randomChoices):
#                 return 0
        
#     return 0





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DigitSpan()
    ex.show()
    sys.exit(app.exec())






# if self.category == 'Forward':
#             self.forwardmessage = QLabel("정방향 태그를 시작합니다", self)
#             self.forwardmessage.setGeometry(250,100, 600,200)
#             font = self.forwardmessage.font()
#             font.setPointSize(30)
#             self.forwardmessage.setFont(font)
#         elif self.category == 'Backward':
#             self.backwardmessage = QLabel("역방향 태그를 시작합니다", self)
#             self.backwardmessage.setGeometry(250,100, 600,200)
#             font = self.backwardmessage.font()
#             font.setPointSize(30)
#             self.backwardmessage.setFont(font)
#         elif self.category == 'Mixed':
#             self.mixedmessage = QLabel("무작위방향 태그를 시작합니다", self)
#             self.mixedmessage.setGeometry(250,100, 600,200)
#             font = self.mixedmessage.font()
#             font.setPointSize(30)
#             self.mixedmessage.setFont(font)