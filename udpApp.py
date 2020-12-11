# gui相关库
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from window import Ui_MainWindow
import os
from udpSocket import UdpApplication
import threading, time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        # 初始化界面
        self.ui.setupUi(self)
        self.__actionBlinding__()
        self.__beBeautiful__()
        self.udpIp = '192.168.1.3'
        self.udpPort = '5000'
        self.udpInterface = UdpApplication()

    def __actionBlinding__(self):
        self.ui.openFile.clicked.connect(self.fileOpenAck)
        self.ui.actionUDP.triggered.connect(self.udpManuCreate)
    def __beBeautiful__(self):
        self.ui.openFile.setFont('楷体')
        self.ui.openFile.setIcon(QIcon('./ico/2.png'))
        self.ui.menubar.setFont('黑体')
        self.ui.actionUDP.setIcon(QIcon('./ico/1.png'))
    def fileOpenAck(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec_():  # 选择完毕
            fileNames = dialog.selectedFiles()
            self.ui.fileDir.setText(fileNames[0])
            try:
                filedHead = open(fileNames[0], 'rb',)
            except:
                self.tipErrorFileOpen()
                return
            self.fileMesgSize = os.path.getsize(fileNames[0])
            self.fileMesg = filedHead.read()
            filedHead.close()
            self.udpSendFile()
    def OpenInitFile(self):
        fileName = 'config.txt'
    def udpManuCreate(self):
        dialog = QDialog()
        dialog.setWindowTitle('UDP CONFIG')
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setWindowIcon(QIcon('./ico/1.png'))
        vtLayout = QVBoxLayout()
        layout1 = QGridLayout()
        groupBox1 = QGroupBox('目标主机')
        groupBox2 = QGroupBox('数据接收窗口(文本模式)')
        groupBox3 = QGroupBox('数据发送窗口(文本模式)')

        groupBox1.setFont('黑体')
        groupBox2.setFont('黑体')
        groupBox3.setFont('黑体')
        label1 = QLabel('UDP IP')
        label2 = QLabel('UDP 端口号')
        textEditIP = QLineEdit()
        textEditIP.setPlaceholderText('输入UDP IP')
        textEditIP.setText(self.udpIp)
        textEditPort = QLineEdit()
        textEditPort.setPlaceholderText('输入UDP 端口号')
        textEditPort.setText(self.udpPort)
        layout1.addWidget(label1, 0, 0, 1, 1)
        layout1.addWidget(textEditIP, 0, 1, 1, 2)
        layout1.addWidget(label2, 0, 4, 1, 1)
        layout1.addWidget(textEditPort, 0, 5, 1, 2)
        groupBox1.setLayout(layout1)

        self.ui.textEditRx = QTextEdit()
        self.ui.pushButtonSocketCrcRx = QPushButton('接收清空')
        self.ui.pushButtonSocketCrcRx.setFont('楷体')
        layout2 = QGridLayout()
        layout2.addWidget(self.ui.textEditRx, 0, 0, 5, 6)
        layout2.addWidget(self.ui.pushButtonSocketCrcRx, 0, 7, 1, 1)
        groupBox2.setLayout(layout2)

        self.ui.textEditTx = QTextEdit()
        self.ui.pushButtonSocketSend = QPushButton('发送数据')
        self.ui.pushButtonSocketCrcSend = QPushButton('发送清空')
        self.ui.pushButtonSocketSend.setFont('楷体')
        self.ui.pushButtonSocketCrcSend.setFont('楷体')
        layout3 = QGridLayout()
        layout3.addWidget(self.ui.textEditTx, 0, 0, 5, 6)
        layout3.addWidget(self.ui.pushButtonSocketSend, 0, 7, 1, 1)
        layout3.addWidget(self.ui.pushButtonSocketCrcSend, 4, 7, 1, 1)
        groupBox3.setLayout(layout3)

        vtLayout.addWidget(groupBox1)
        vtLayout.addWidget(groupBox2)
        vtLayout.addWidget(groupBox3)

        vtLayout.setStretch(0, 1)
        vtLayout.setStretch(1, 6)
        vtLayout.setStretch(2, 2)
        dialog.setLayout(vtLayout)

        self.ui.pushButtonSocketSend.clicked.connect(lambda :self.pushButtonSocketSendSlot(self.ui.textEditTx.toPlainText()))
        self.ui.pushButtonSocketCrcSend.clicked.connect(lambda :self.ui.textEditTx.setPlainText(''))
        self.ui.pushButtonSocketCrcRx.clicked.connect(lambda: self.ui.textEditRx.setPlainText(''))
        textEditIP.editingFinished.connect(lambda :self.setUdpIp(textEditIP.text()))
        textEditPort.editingFinished.connect(lambda: self.setUdpPort(textEditPort.text()))

        # 创建了UDP就可以开启接收线程
        self.thread1 = threading.Thread(target = self.monitorUdpRx)
        self.thread1.start()

        if dialog.exec_():
            pass
    def monitorUdpRx(self):
        while True:
            timeNow = time.strftime('%H:%M:%S', time.localtime(time.time()))
            recvIpPort, recvMesg = self.udpInterface.socketGetRcvData(self.udpInterface.udpSocket)
            res = timeNow + ' IP:' + recvIpPort[0] + ' Port:' + str(recvIpPort[1]) + ' Mesg:' + recvMesg
            self.ui.textEditRx.append(res)

    def pushButtonSocketSendSlot(self, string):
        send = bytes(string, encoding='utf-8')
        self.udpInterface.socketSendString(send, self.udpIp, self.udpPort)
    def setUdpIp(self, string):     #设置UDP 目标IP地址
        self.udpIp = string
    def setUdpPort(self, string):   #设置UDP 目标端口号
        self.udpPort = string
    def udpSendFile(self):  #UDP发送文件
        self.udpInterface.socketCreate()
        try:
            times = int(self.fileMesgSize / 1024)
            res = self.fileMesgSize % 1024
            head = b'B10000000001'
            levelUp = b'B1000011000100060004\x5a\xa5\x80\x00'
            reboot = b'B1000011000100040004\x55\xaa\x5a\xa5'
            if (times != 0):
                for i in range(0, times):
                    vp_addr = bytes(str(hex(int('8000', 16)+512*i)).rjust(4, '0'), encoding='utf-8')
                    vp_len = b'0400'
                    sand = head + vp_addr[2:] + vp_len + \
                        self.fileMesg[i*1024:(i+1)*1024]
                    self.udpInterface.socketSendString(sand, self.udpIp, self.udpPort)
            if (res != 0):
                vp_addr = bytes(str(hex(int('8000', 16) + 512 * times)).rjust(4, '0'), encoding='utf-8')
                vp_len = bytes((str(hex(res))[2:]).rjust(4, '0'), encoding='utf-8')
                sand = head + vp_addr[2:] + vp_len + \
                    self.fileMesg[times * 1024: times * 1024 + res]
                self.udpInterface.socketSendString(sand, self.udpIp, self.udpPort)
                self.udpInterface.socketSendString(levelUp, self.udpIp, self.udpPort)
                self.udpInterface.socketSendString(reboot, self.udpIp, self.udpPort)
        except:
            self.tipErrorSocketSend()

    def tipErrorFileOpen(self):
        dialog = QDialog()
        dialog.setFixedSize(120, 40)
        text = QLabel('文件打开失败')
        text.setFont('黑体')
        layout = QVBoxLayout()
        layout.addWidget(text)
        dialog.setLayout(layout)
        if dialog.exec_():
            pass

    def tipErrorSocketSend(self):
        dialog = QDialog()
        dialog.setFixedSize(120, 40)
        text = QLabel('UDP连接失败')
        text.setFont('黑体')
        layout = QVBoxLayout()
        layout.addWidget(text)
        dialog.setLayout(layout)
        if dialog.exec_():
            pass

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    MainUI = MainWindow()
    MainUI.show()
    app.exec_()
    MainUI.udpInterface.socketClose()
