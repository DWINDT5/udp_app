import socket
import time
class UdpApplication():
    def __init__(self):
        super().__init__()
        self.__paramentInit__()
    def __paramentInit__(self):
        self.socketCreate()
        pass
    # UDP创建套接字
    def socketCreate(self):
        # 没有创建socket 才会创建套接字
        if hasattr(self,'udpSocket') == False:
            ip_port = ('192.168.1.2', 6000)
            self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udpSocket.bind(ip_port)
    # UDP关闭套接字
    def socketClose(self):
        # 没有创建socket 才会关闭套接字
        if hasattr(self, 'udpSocket') == True:  # 有创建socket
            self.udpSocket.close()
            del self.udpSocket
    # UDP发送数据 数据string-udpIp地址string——udp端口号string
    def socketSendString(self, string, udpIp, udpPort):
        # 本地如果没用此IP和端口 就尝试两次 第一次会创建 第二次才能成功绑定
        try:
            self.socketCreate()
            self.udpSocket.sendto(string, (udpIp, int(udpPort)))
        except:
            self.socketCreate()
            self.udpSocket.sendto(string, (udpIp, int(udpPort)))
        # 等待1MS 避免设备卡死
        time.sleep(0.001)
    # UDP获取接收数据 阻塞进程 必须放在线程中处理
    def socketGetRcvData(self, udpSocket):
        recvMsg = udpSocket.recvfrom(1024)  #阻塞
        recvIpPort = recvMsg[1]
        recvMsg = recvMsg[0].decode('gbk')
        return recvIpPort, recvMsg