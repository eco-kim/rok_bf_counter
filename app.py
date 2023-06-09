import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtTest import QTest
from bot import bf_count, bf_check, go_to_war_page, rallycount, location_check, adb_device, background_screenshot
from db import Database
import os

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.db = None
        self.bot = 0
        self.bf_list = []
        self.adb_port = None
        self.alli_name = ''
        self.back = None

    def initUI(self):        
        self.db_btn = QPushButton('DB 경로 선택')
        self.db_btn.pressed.connect(self.db_init)
        self.lbl1 = QLabel('ADB port:')
        self.le_port = QLineEdit()
        self.le_port.textChanged.connect(self.get_adb_port)
        self.lbl2 = QLabel('연맹:')        
        self.le_alli = QLineEdit()
        self.le_alli.textChanged.connect(self.get_alli_name)
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
        hbox.addWidget(self.le_port)
        hbox.addStretch(2)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.lbl2)
        hbox2.addWidget(self.le_alli)
        hbox2.addStretch(2)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        vbox.addLayout(self.btn_layout(self.db_btn))
        vbox.addLayout(self.btn_layout(self.start_btn))
        vbox.addLayout(self.btn_layout(self.stop_btn))
        vbox.addLayout(self.btn_layout(self.data_btn))
        vbox.addLayout(self.btn_layout(self.timeline_btn))
        vbox.addStretch(1)

        self.setLayout(vbox)

        self.setWindowTitle('야도측정기')
        self.setWindowIcon(QIcon('./src/BF.png'))
        self.setGeometry(300, 300, 300, 300)
        self.show()

    def get_adb_port(self):
        port = self.le_port.text()
        if port != '':
            self.adb_port = int(self.le_port.text())

    def get_alli_name(self):
        alli_name = self.le_alli.text()
        if alli_name != '':
            self.alli_name = alli_name

    def bot_start(self):
        if self.db is None:
            self.db = Database('./')
        if self.adb_port is None:
            QMessageBox.information(self, 'error', 'ADB 포트 번호를 입력해 주세요')
            return 0
        self.adb = adb_device(self.adb_port)
        if self.adb is None:
            QMessageBox.information(self, 'error', 'ADB 포트 번호를 확인해 주세요')
            return 0
        self.bot=1
        #self.wait.exit()
        rally = 0
        while self.bot==1:
            go_to_war_page(self.adb)
            self.back = background_screenshot(self.adb)
            cc = bf_check(self.back) #집결 있는지 확인
            if not cc:
                rally = 0 #집결이 없었음
            while not cc and self.bot==1: #집결 생길때까지 기다림
                QTest.qWait(3000)
                self.back = background_screenshot(self.adb)
                cc = bf_check(self.back)
                QApplication.processEvents()
            if self.bot==0: #멈춤버튼 누름
                break
            
            if rally==0: ##집결이 없었다가 생김, 혹은 처음 켰음
                nn = rallycount(self.back) #집결 열려있는 것 개수
                _, bf_loc = bf_count(self.adb, self.db, self.back, self.alli_name, nn)
                self.bf_list.append(bf_loc)
                rally = 1
            else: ##전에 어디 한번 다녀옴
                i = location_check(self.back, self.bf_list)
                while i == -1 and self.bot==1: ##다른 좌표가 없는 경우 3초마다 확인하면서 기다림
                    QTest.qWait(3000)
                    self.back = background_screenshot(self.adb)
                    i = location_check(self.back, self.bf_list)
                    if i == 0: #집결이 다 없어짐
                        rally = 0
                        break
                    QApplication.processEvents()
                if rally == 0:
                    continue
                if self.bot==0: #멈춤버튼 누름
                    break
                _, bf_loc = bf_count(self.adb, self.db, self.back, self.alli_name, i)
                self.bf_list.append(bf_loc)
                rally = 1             
            if len(self.bf_list)>10:
                self.bf_list = self.bf_list[-10:]            
            QApplication.processEvents()       
    
    def bot_stop(self):
        self.bot=0
    
    def db_init(self):
        db_path = QFileDialog.getExistingDirectory(self, "select directory")
        if db_path != "":
            self.db_path = db_path
            self.db = Database(self.db_path)

    def data_extract(self):    
        df = self.db.data_extract()
        fname = QFileDialog.getSaveFileName(self, 'Save file', "", "excel files (*.xlsx)")
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
    try:
        os.chdir(sys._MEIPASS)
    except:
        os.chdir(os.getcwd())
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())