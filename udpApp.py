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
        self.ui.udpIp.setText('192.168.1.3')
        self.ui.udpPort.setText('5000')

    def __actionBlinding__(self):
        self.ui.openFile.clicked.connect(self.fileOpenAck)

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
            # print(self.fileMesgSize)
            self.fileMesg = filedHead.read()
            filedHead.close()
            self.udpSendFile()

    def udpSendFile(self):
        ip_port = ('192.168.1.2', 6000)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(ip_port)
        # print(self.fileMesg.encode())
        try:
            times = int(self.fileMesgSize / 1024)
            res = self.fileMesgSize % 1024
            head = b'B10000000001'
            if (times != 0):
                for i in range(0, times):
                    vp_addr = bytes(
                        str(hex(int('5000', 16)+512*i)).rjust(4, '0'), encoding='utf-8')
                    vp_len = b'0400'
                    sand = head + vp_addr[2:] + vp_len + \
                        self.fileMesg[i*1024:(i+1)*1024]
                    udp_socket.sendto(
                        sand, (self.ui.udpIp.text(), int(self.ui.udpPort.text())))
                    time.sleep(0.001)
            if (res != 0):
                vp_addr = bytes(
                    str(hex(int('5000', 16) + 512 * times)).rjust(4, '0'), encoding='utf-8')
                vp_len = bytes((str(hex(res))[2:]).rjust(
                    4, '0'), encoding='utf-8')
                sand = head + vp_addr[2:] + vp_len + \
                    self.fileMesg[times * 1024: times * 1024 + res]
                udp_socket.sendto(sand, (self.ui.udpIp.text(),
                                         int(self.ui.udpPort.text())))
                updata_cmd = b'B1000000000100060004\x5a\xa5\x50\x00'
                reboot_cmd = b'B1000000000100040004\x55\xaa\x5a\xa5'
                udp_socket.sendto(updata_cmd, (self.ui.udpIp.text(),
                                               int(self.ui.udpPort.text())))
                time.sleep(0.001)
                udp_socket.sendto(reboot_cmd, (self.ui.udpIp.text(),
                                               int(self.ui.udpPort.text())))
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
