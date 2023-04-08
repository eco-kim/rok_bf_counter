import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import QEventLoop
from PyQt5.QtGui import QIcon
from PyQt5.QtTest import QTest
import pandas as pd
from bot import bf_count, bf_check, go_to_war_page
from db import Database

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.db = Database()
        self.bot = 0
        self.castle_loc = None
        self.bf_loc = None
        self.wait = QEventLoop()
        self.wait.exec() ##시작 안하고 그냥 측정기 창 껐을때 이벤트루프 빠져나가는 코드 짜야함

    def initUI(self):        
        self.lbl1 = QLabel('ADB port:')
        self.te = QLineEdit()
        self.start_btn = QPushButton('시작')
        self.start_btn.pressed.connect(self.bot_start)
        self.stop_btn = QPushButton('멈춤')
        self.stop_btn.pressed.connect(self.bot_stop)        
        self.data_btn = QPushButton('데이터 추출')
        self.data_btn.pressed.connect(self.data_extract)
        self.timeline_btn = QPushButton('타임라인 추출')
        self.timeline_btn.pressed.connect(self.timeline_extract)        

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.lbl1)
        hbox.addWidget(self.te)
        hbox.addStretch(2)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(2)
        hbox2.addWidget(self.start_btn)
        hbox2.addStretch(2)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addLayout(self.btn_layout(self.start_btn))
        vbox.addLayout(self.btn_layout(self.stop_btn))
        vbox.addLayout(self.btn_layout(self.data_btn))
        vbox.addLayout(self.btn_layout(self.timeline_btn))
        vbox.addStretch(1)

        self.setLayout(vbox)

        self.setWindowTitle('야도측정기')
        self.setWindowIcon(QIcon('./src/BF.png'))
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def bot_start(self):
        self.bot=1
        self.wait.exit()
        while self.bot==1:
            go_to_war_page()
            cc = bf_check()
            if not cc:
                rally = 0
            while not cc and self.bot==1:
                QTest.qWait(3000)
                cc = bf_check()
                QApplication.processEvents()
            if self.bot==0:
                break
            self.castle_loc, self.bf_loc = bf_count(self.db, rally, self.castle_loc, self.bf_loc)
            QApplication.processEvents()       
    
    def bot_stop(self):
        self.bot=0
    
    def data_extract(self):    
        df = self.db.data_extract()
        fname = QFileDialog.getSaveFileName(self, 'Save file', "", "excel files files (*.xlsx)")
        if fname[0] != "":
            df.to_excel(fname[0]) 
    
    def timeline_extract(self):
        df = self.db.timeline_extract()
        fname = QFileDialog.getSaveFileName(self, 'Save file', "", "excel files (*.xlsx)")
        if fname[0] != "":
            df.to_excel(fname[0])        
    
    def btn_layout(self, btn):
        hbox = QHBoxLayout()
        hbox.addStretch(2)
        hbox.addWidget(btn)
        hbox.addStretch(2)
        return hbox        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())