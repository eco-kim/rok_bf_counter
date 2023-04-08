import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QIcon
import pandas as pd


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.lbl1 = QLabel('ADB port:')
        self.te = QLineEdit()
        self.start_btn = QPushButton('시작')
        self.start_btn.pressed.connect(self.bot_start)
        self.stop_btn = QPushButton('멈춤')
        self.stop_btn.pressed.connect(self.bot_stop)        
        self.data_btn = QPushButton('데이터 추출')
        self.data_btn.pressed.connect(self.data_extract)

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
        vbox.addStretch(1)

        self.setLayout(vbox)

        self.setWindowTitle('야도측정기')
        self.setWindowIcon(QIcon('./src/BF.png'))
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def bot_start(self):
        return 1
    
    def bot_stop(self):
        return 0
    
    def data_extract(self):    
        fname = QFileDialog.getSaveFileName(self, 'Save file', "", "csv files (*.csv)")
        if fname[0] != "":
            with open(fname[0], 'w') as f:
                df = pd.DataFrame([[1,2,3]],columns=['test','test','test'])
                df.to_csv(f)
    
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