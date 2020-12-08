# gui相关库
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from window import Ui_MainWindow
import socket
import os
import sys
import time


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

    def __actionBlinding__(self):
        self.ui.openFile.clicked.connect(self.fileOpenAck)
        self.ui.actionUDP.triggered.connect(self.udpManuCreate)
    def __beBeautiful__(self):
        self.ui.openFile.setFont('楷体')
        self.ui.openFile.setIcon(QIcon('./ico/2.png'))
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
            print(self.fileMesgSize)
            self.fileMesg = filedHead.read()
            filedHead.close()
            self.udpSendFile()
    def udpManuCreate(self):
        dialog = QDialog()
        dialog.setWindowTitle('UDP CONFIG')
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setWindowIcon(QIcon('./ico/1.png'))
        vtLayout = QVBoxLayout()
        layout1 = QGridLayout()
        groupBox1 = QGroupBox('Socket状态')
        groupBox3 = QGroupBox('数据发送窗口(文本模式)')

        groupBox1.setFont('黑体')
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

        self.ui.textEditTx = QTextEdit()
        self.ui.pushButtonSocketSend = QPushButton('发送数据')
        self.ui.pushButtonSocketCrcSend = QPushButton('发送清空')
        self.ui.pushButtonSocketCrcRX = QPushButton('统计清空')
        self.ui.pushButtonSocketSend.setFont('楷体')
        self.ui.pushButtonSocketCrcSend.setFont('楷体')
        self.ui.pushButtonSocketCrcRX.setFont('楷体')
        layout2 = QGridLayout()
        layout2.addWidget(self.ui.textEditTx, 0, 0, 5, 6)
        layout2.addWidget(self.ui.pushButtonSocketSend, 0, 7, 1, 1)
        layout2.addWidget(self.ui.pushButtonSocketCrcSend, 2, 7, 1, 1)
        layout2.addWidget(self.ui.pushButtonSocketCrcRX, 4, 7, 1, 1)
        groupBox3.setLayout(layout2)

        vtLayout.addWidget(groupBox1)
        vtLayout.addWidget(groupBox3)

        vtLayout.setStretch(0, 1)
        vtLayout.setStretch(1, 3)
        dialog.setLayout(vtLayout)
        textEditIP.editingFinished.connect(lambda :self.setUdpIp(textEditIP.text()))
        textEditPort.editingFinished.connect(lambda: self.setUdpPort(textEditPort.text()))
        if dialog.exec_():
            pass
    def setUdpIp(self, string):
        self.udpIp = string
    def setUdpPort(self, string):
        self.udpPort = string
    def udpSendFile(self):
        ip_port = ('192.168.1.2', 6000)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(ip_port)
        try:
            times = int(self.fileMesgSize / 1024)
            res = self.fileMesgSize % 1024
            head = b'B10000000001'
            levelUp = b'B1000011000100060004\x5a\xa5\x50\x00'
            reboot = b'B1000011000100040004\x55\xaa\x5a\xa5'
            if (times != 0):
                for i in range(0, times):
                    vp_addr = bytes(
                        str(hex(int('8000', 16)+512*i)).rjust(4, '0'), encoding='utf-8')
                    vp_len = b'0400'
                    sand = head + vp_addr[2:] + vp_len + \
                        self.fileMesg[i*1024:(i+1)*1024]
                    udp_socket.sendto(
                        sand, (self.udpIp, int(self.udpPort)))
                    time.sleep(0.001)
            if (res != 0):
                vp_addr = bytes(
                    str(hex(int('8000', 16) + 512 * times)).rjust(4, '0'), encoding='utf-8')
                vp_len = bytes((str(hex(res))[2:]).rjust(
                    4, '0'), encoding='utf-8')
                sand = head + vp_addr[2:] + vp_len + \
                    self.fileMesg[times * 1024: times * 1024 + res]
                udp_socket.sendto(sand, (self.udpIp, int(self.udpPort)))
                time.sleep(0.001)
            udp_socket.sendto(levelUp, (self.udpIp, int(self.udpPort)))
            time.sleep(0.001)
            udp_socket.sendto(reboot, (self.udpIp, int(self.udpPort)))
        except:
            self.tipErrorSocketSend()
        udp_socket.close()

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
