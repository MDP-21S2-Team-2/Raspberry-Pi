import bluetooth

from configuration import *

class AndroidInterface():

    def __init__(self):
        self.serverSocket = None
        self.clientSocket = None
        self.connection = False

    def isConnected(self):
        return self.connection
    
    def setConnection(self, state):
        self.connection = state

    def connectToAndroid(self, uuid = UUID):
        try:
            self.serverSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.serverSocket.bind(('', BT_PORT))
            self.serverSocket.listen(1)

            print("Bluetooth - Waiting for connection to RFCOMM channel %d" % BT_PORT)

            self.clientSocket, clientInfo = self.serverSocket.accept()
            print ("Bluetooth - Connection succeeded")
            self.setConnection(True)
            print ("Bluetooth - Accepted connection from ", clientInfo)
            

        except Exception as e:
            print("Bluetooth - Caught error:")
            print(str(e))

            print("Bluetooth - Connection failed")
            self.setConnection(False)

            print ("Bluetooth - Closing server socket")
            self.serverSocket.close()
            raise e
            
    
    def disconnectFromAndroid(self):
        try:
            if self.clientSocket:
                self.clientSocket.close()
                print ("Bluetooth - Closing client socket")

            if self.serverSocket:
                self.serverSocket.close()
                print ("Bluetooth - Closing server socket")

            self.setConnection(False)

        except Exception as e:
            print("Bluetooth - Caught error:")
            print(str(e))

            print ("Bluetooth - Disconnection failed")
            raise e

    def sendToAndroid (self, string):
        try:
            self.clientSocket.send(string)
            print ("Bluetooth - Send to Android: %s" %(string))

        except Exception as e:
            print("Bluetooth - Caught error:")
            print(str(e))
            raise e

            # print("Bluetooth - RPi is trying to reconnect")
            # self.connectToAndroid()

    def receiveFromAndroid (self):
        try:
            string = self.clientSocket.recv(1024)
            decodedString = string.decode('utf-8')
            print("Bluetooth - Received from Android: %s" % str(decodedString))
            return (decodedString)

        except Exception as e:
            print("Bluetooth - Caught error:")
            print(str(e))
            raise e

            # print("Bluetooth - RPi is trying to reconnect")
            # self.connectToAndroid()