import socket
import sys

from configuration import *

class PCInterface(object):

    def __init__(self):
        self.host = WIFI_IP
        self.port = WIFI_PORT
        self.imagePort = IMAGE_PORT

        self.connection = False
        self.imageConnection = False

        self.serverSocket = 0
        self.clientSocket = 0

        self.serverImgSocket = 0
        self.clientImgSocket = 0

    def isConnected(self):
        return self.connection
    
    def setConnection(self, state):
        self.connection = state

    def connectToPC(self):
        try:
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serverSocket.bind((self.host, self.port))
            print("WiFi - Port binded. IP: " + str(self.host) + ". Port: " + str(self.port))

            # The number of unaccepted connections is set to 2
            self.serverSocket.listen(2)
            print ("WiFi - Waiting for connection")

            self.clientSocket, self.address = self.serverSocket.accept()
            print ("WiFi - Connection succeeded")
            print ("WiFi - Connected to PC with the IP Address: ", str(self.address))
            self.setConnection(True)

        except Exception as e:
            print("WiFi - Caught error:")
            print(str(e))

            self.connection = False

    def connectToImg(self):
        try:
            self.serverImgSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverImgSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serverImgSocket.bind((self.host, self.imagePort))
            print("WiFi - Image port binded. Port: " + str(self.imagePort))

            # The number of unaccepted connections is set to 2
            self.serverImgSocket.listen(2)
            print ("WiFi - Waiting for connection from ImgRec")

            self.clientImgSocket, self.imgAddress = self.serverImgSocket.accept()
            print ("WiFi - Connection to ImgRec succeeded")
            print ("WiFi - Connected to ImgRec with the IP Address: ", str(self.imgAddress))
            self.imageConnection = True

        except Exception as e:
            print("WiFi - Caught error:")
            print(str(e))

            print("WiFi - Connection to ImgRec failed")
            self.imageConnection = False

    def disconnectFromPC (self):
        try:
            if self.serverSocket:
                self.serverSocket.close()
                print ("WiFi - Closing server socket")

            if self.clientSocket:
                self.clientSocket.close()
                print ("WiFi - Closing client socket")

            self.setConnection(False)

        except Exception as e:
            print("WiFi - Caught error:")
            print(str(e))

            print ("WiFi - Disconnection failed")

    def disconnectFromImgRec (self):
        try:
            if self.serverImgSocket:
                self.serverImgSocket.close()
                print ("WiFi - Closing ImgRec server socket")

            if self.clientImgSocket:
                self.clientImgSocket.close()
                print ("WiFi - Closing ImgRec client socket")

            self.imageConnection = False

        except Exception as e:
            print("WiFi - Caught error:")
            print(str(e))

            print ("WiFi - ImgRec disconnection failed")

    def sendToPC (self, string):
        try:
            string = str(string) + '\n'
            encodedString = string.encode()
            self.clientSocket.sendto(encodedString, self.address)
            print ('WiFi - Sent to PC: ' + string)

        except Exception as e:
            print("WiFi - Caught error:")
            print(str(e))

            # print("WiFi - RPi is trying to reconnect")
            # self.connectToPC()

    def receiveFromPC (self):
        try:
            string = self.clientSocket.recv(1024)
            decodedString = string.decode('utf-8')
            print ("WiFi - Read from PC: %s" %(decodedString))

            return decodedString

        except Exception as e:
            print("WiFi - Caught error:")
            print(str(e))

            # print("WiFi - RPi is trying to reconnect")
            # self.connectToPC()

    def receiveFromImgRec(self):
        try:
            string = self.clientImgSocket.recv(1024)
            decodedString = string.decode('utf-8')
            print ("WiFi - Read from ImgRec: %s" %(decodedString))

            return decodedString

        except Exception as e:
            print("WiFi - Caught error:")
            print(str(e))