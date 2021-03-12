import socket
import sys

from configuration import *

class PCInterface(object):

    def __init__(self):
        self.host = WIFI_IP
        self.port = WIFI_PORT
        self.connection = False
        self.serverSocket = None
        self.clientSocket = None

        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.host, self.port))
        self.serverSocket.listen(3)

    def isConnected(self):
        return self.connection
    
    def setConnection(self, state):
        self.connection = state

    def connectToPC(self):
        try:
            
            print("WiFi - Port binded. Port: " + str(self.port))

            print ("WiFi - Waiting for connection")

            self.clientSocket, self.address = self.serverSocket.accept()
            print ("WiFi - Connection succeeded")
            print ("WiFi - Connected to PC with the IP Address: ", str(self.address))
            self.setConnection(True)

        except Exception as error:
            print("WiFi - Caught error: " + str(error))
            self.connection = False
            raise error

    def disconnectFromPC(self):
        try:
            if self.clientSocket:
                self.clientSocket.close()
                self.clientSocket = None
                print ("WiFi - Closing client socket")

            # if self.serverSocket:
            #     self.serverSocket.close()
            #     print ("WiFi - Closing server socket")

            self.setConnection(False)

        except Exception as e:
            print("WiFi - Caught error:")
            print(str(e))

            print ("WiFi - Disconnection failed")
            raise e

    def sendToPC (self, string):
        if self.clientSocket != None:
            try:
                string = str(string) + '\n'
                encodedString = string.encode()
                self.clientSocket.sendto(encodedString, self.address)
                print ('WiFi - Sent to PC: ' + string)

            except Exception as e:
                print("WiFi - Caught error:")
                print(str(e))
                raise e

                # print("WiFi - RPi is trying to reconnect")
                # self.connectToPC()

    def receiveFromPC (self):
        if self.clientSocket != None:
            try:
                string = self.clientSocket.recv(1024)
                if len(string) > 0:
                    decodedString = string.decode('utf-8')
                    print ("WiFi - Read from PC: %s" %(decodedString))

                    return decodedString
                else:
                    print ("WiFi - Waiting for connection")

                    self.clientSocket, self.address = self.serverSocket.accept()
                    print ("WiFi - Connection succeeded")
                    print ("WiFi - Connected to PC with the IP Address: ", str(self.address))
                    self.setConnection(True)

            except Exception as e:
                print("WiFi - Caught error:")
                print(str(e))
                self.setConnection(False)
                raise e