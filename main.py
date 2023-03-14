import sys
import os
import json
from serial import Serial
from portfinder import macAddfinder
# from MemoryGame.game import memory_game 
# from TMT.a import tmt_a
# from TMT.b import tmt_b
# from DigitSpan.digit_span import * ## ㅂㅂ
# from connectroad import *
from TEMP import DigitSpan

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpinBox, QStatusBar,
    QVBoxLayout, QWidget)


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        with open("./CFG_show.json", "r", encoding='UTF-8') as cfg:
            cfg = json.load(cfg)
    
        self.RFID_MemoryGame = cfg['MemoryGame']
        self.RFID_TMTA = cfg['TMTA']
        self.RFID_TMTB = cfg['TMTB']
        self.RFID_DIGITSPAN = cfg['DIGITSPAN']
        self.RFID_CONNECTROAD = cfg['ConnectRoad']
        self.RFID_BTMACID = cfg['BTMACID']
        
        hc06_port = macAddfinder(macAddress=self.RFID_BTMACID)
        self.arduino = Serial(port=hc06_port, baudrate=9600, timeout=0.5)

        self.setupUi(self)
        self.pushButton.clicked.connect(self.button1Function)
        self.pushButton_2.clicked.connect(self.button2Function)
        self.pushButton_3.clicked.connect(self.button3Function)
        self.pushButton_4.clicked.connect(self.button4Function)
        self.pushButton_5.clicked.connect(self.button5Function)
        self.pushButton_6.clicked.connect(self.button6Function)
        self.pushButton_7.clicked.connect(self.button7Function)
        self.pushButton_8.clicked.connect(self.button8Function)

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(900, 600))
        MainWindow.setMaximumSize(QSize(900, 600))
        self.actionConnections = QAction(MainWindow)
        self.actionConnections.setObjectName(u"actionConnections")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 140, 901, 411))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButton = QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_3.addWidget(self.pushButton)

        self.comboBox = QComboBox(self.horizontalLayoutWidget)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_3.addWidget(self.comboBox)

        self.spinBox_5 = QSpinBox(self.horizontalLayoutWidget)
        self.spinBox_5.setObjectName(u"spinBox_5")
        self.spinBox_5.setMaximumSize(QSize(100, 16777215))
        self.spinBox_5.setMinimum(2)
        self.spinBox_5.setMaximum(30)
        self.spinBox_5.setValue(15)

        self.horizontalLayout_3.addWidget(self.spinBox_5)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.pushButton_2 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_4.addWidget(self.pushButton_2)

        self.comboBox_2 = QComboBox(self.horizontalLayoutWidget)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName(u"comboBox_2")

        self.horizontalLayout_4.addWidget(self.comboBox_2)

        self.spinBox_4 = QSpinBox(self.horizontalLayoutWidget)
        self.spinBox_4.setObjectName(u"spinBox_4")
        self.spinBox_4.setMaximumSize(QSize(100, 16777215))
        self.spinBox_4.setMinimum(2)
        self.spinBox_4.setMaximum(10)
        self.spinBox_4.setValue(4)

        self.horizontalLayout_4.addWidget(self.spinBox_4)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.pushButton_3 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout_6.addWidget(self.pushButton_3)

        self.comboBox_3 = QComboBox(self.horizontalLayoutWidget)
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.setObjectName(u"comboBox_3")
        self.comboBox_3.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_6.addWidget(self.comboBox_3)

        self.spinBox = QSpinBox(self.horizontalLayoutWidget)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMaximumSize(QSize(50, 16777215))
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(6)

        self.horizontalLayout_6.addWidget(self.spinBox)

        self.spinBox_2 = QSpinBox(self.horizontalLayoutWidget)
        self.spinBox_2.setObjectName(u"spinBox_2")
        self.spinBox_2.setMaximumSize(QSize(50, 16777215))
        self.spinBox_2.setMinimum(1)
        self.spinBox_2.setMaximum(66)

        self.horizontalLayout_6.addWidget(self.spinBox_2)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.pushButton_4 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.horizontalLayout_7.addWidget(self.pushButton_4)

        self.comboBox_4 = QComboBox(self.horizontalLayoutWidget)
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.setObjectName(u"comboBox_4")
        self.comboBox_4.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_7.addWidget(self.comboBox_4)

        self.spinBox_3 = QSpinBox(self.horizontalLayoutWidget)
        self.spinBox_3.setObjectName(u"spinBox_3")
        self.spinBox_3.setMaximumSize(QSize(50, 16777215))
        self.spinBox_3.setMinimum(3)
        self.spinBox_3.setMaximum(7)
        self.spinBox_3.setValue(5)

        self.horizontalLayout_7.addWidget(self.spinBox_3)

        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.pushButton_5 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.horizontalLayout_8.addWidget(self.pushButton_5)

        self.comboBox_5 = QComboBox(self.horizontalLayoutWidget)
        self.comboBox_5.setObjectName(u"comboBox_5")
        self.comboBox_5.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout_8.addWidget(self.comboBox_5)

        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.pushButton_6 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_6.setObjectName(u"pushButton_6")

        self.horizontalLayout_9.addWidget(self.pushButton_6)

        self.comboBox_6 = QComboBox(self.horizontalLayoutWidget)
        self.comboBox_6.setObjectName(u"comboBox_6")
        self.comboBox_6.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout_9.addWidget(self.comboBox_6)

        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.pushButton_7 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_7.setObjectName(u"pushButton_7")

        self.horizontalLayout_10.addWidget(self.pushButton_7)

        self.comboBox_7 = QComboBox(self.horizontalLayoutWidget)
        self.comboBox_7.setObjectName(u"comboBox_7")
        self.comboBox_7.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout_10.addWidget(self.comboBox_7)

        self.verticalLayout_2.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.pushButton_8 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_8.setObjectName(u"pushButton_8")

        self.horizontalLayout_11.addWidget(self.pushButton_8)

        self.comboBox_8 = QComboBox(self.horizontalLayoutWidget)
        self.comboBox_8.setObjectName(u"comboBox_8")
        self.comboBox_8.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout_11.addWidget(self.comboBox_8)

        self.verticalLayout_2.addLayout(self.horizontalLayout_11)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(200, 50, 500, 50))
        font = QFont()
        font.setFamily(u"Algerian")
        font.setPointSize(36)
        self.label.setFont(font)
        self.label.setFrameShape(QFrame.NoFrame)
        self.label.setAlignment(Qt.AlignCenter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 22))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.actionConnections)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionConnections.setText(QCoreApplication.translate("MainWindow", u"Connections", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"TMT", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"A", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"B", None))

        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"DIGIT SPAN", None))
        self.comboBox_2.setItemText(0, QCoreApplication.translate("MainWindow", u"Forward", None))
        self.comboBox_2.setItemText(1, QCoreApplication.translate("MainWindow", u"Backward", None))
        self.comboBox_2.setItemText(2, QCoreApplication.translate("MainWindow", u"Mixed", None))

        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"MEMORY MATCH GAME", None))
        self.comboBox_3.setItemText(0, QCoreApplication.translate("MainWindow", u"Animal", None))
        self.comboBox_3.setItemText(1, QCoreApplication.translate("MainWindow", u"Fruit", None))
        self.comboBox_3.setItemText(2, QCoreApplication.translate("MainWindow", u"Furniture", None))

        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"CONNECT ROAD", None))
        self.comboBox_4.setItemText(0, QCoreApplication.translate("MainWindow", u"Easy", None))
        self.comboBox_4.setItemText(1, QCoreApplication.translate("MainWindow", u"Normal", None))
        self.comboBox_4.setItemText(2, QCoreApplication.translate("MainWindow", u"Hard", None))

        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"scan test", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\ud504\ub85c\uc81d\ud2b8\uba85", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\uc124\uc815", None))
    # retranslateUi

    def restart(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

    # TMT A,B
    def button1Function(self):
        print(f'button: 1, event: {self.comboBox.currentText()}, {self.spinBox_5.value()}')
        # if self.comboBox.currentText() == 'A':
        #     tmt_a(arduino=self.arduino, cnt=self.spinBox_5.value(), rfid_map=self.RFID_TMTA)
        #     self.restart()
        # else:
        #     tmt_b(arduino=self.arduino, cnt=self.spinBox_5.value(), rfid_map=self.RFID_TMTB)
        #     self.restart()

    # MEMORT MATCH GAME
    def button3Function(self):
        print(f'button: 3, event: {self.comboBox_3.currentText()}, value: ({self.spinBox.value()}, {self.spinBox_2.value()})')
        # if (self.spinBox.value() * self.spinBox_2.value()) % 2 == 0:
        #     memory_game(arduino=self.arduino, rfid_map=self.RFID_MemoryGame, imageset=self.comboBox_3.currentText(), 
        #                 gameColumns=self.spinBox.value(), gameRows=self.spinBox_2.value())
        #     self.restart()

    # DIGIT_SPAN
    def button2Function(self):
        print(f'button: 2, event: {self.comboBox_2.currentText()}, value: {self.spinBox_4.value()}')
        # digit_span(self.arduino, self.spinBox_4.value(), rfid_map=self.RFID_DIGITSPAN)
        ds = DigitSpan(arduino= self.arduino, rfid_map = self.RFID_DIGITSPAN, 
                  category = 'Forward',  num_cards = self.spinBox_4.value())
        self.setCentralWidget(ds)
        # self.restart()

    # CONNECT ROAD
    def button4Function(self):
        print(f'button: 4, event: {self.comboBox_4.currentText()}, value: {self.spinBox_3.value()}')
        # ConnectRoad(arduino = self.arduino, rfid_map = self.RFID_CONNECTROAD, 
        #             level = self.comboBox_4.currentText(), cnt = self.spinBox_3.value())
        # cr.show()
        # self.restart()

# temp
    def button5Function(self):
        print(f'button: 5, event: {self.comboBox_5.currentText()}')
    def button6Function(self):
        print(f'button: 6, event: {self.comboBox_6.currentText()}')
    def button7Function(self):
        print(f'button: 7, event: {self.comboBox_7.currentText()}')

    # SCAN TEST
    def button8Function(self):
        print(f'button: 8, event: {self.comboBox_8.currentText()}')






def main():
    app = QApplication(sys.argv)
    win = Ui_MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
