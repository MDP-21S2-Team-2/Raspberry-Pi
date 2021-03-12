import os
import threading
import time

from android import *
from arduino import *
from pc import *

class RaspberryPi():

    def __init__(self):

        # #Current state of robot (Prototype)
        # self.X = 0
        # self.Y = 0
        # self.state = 0
        # #Current angle (0, 90, 180, 270)
        # self.orient = 0

        #Define new interfaces
        self.android = AndroidInterface()
        self.arduino = ArduinoInterface()
        self.pc = PCInterface()
        
        print("RPi - Initialized all interfaces")
        
        #Initial connection
        self.arduino.connectToArduino()
        self.android.connectToAndroid()
        self.pc.connectToPC()

    def processCommand(self, string):
        tokenList = string.split("-")
        if len(tokenList) >= 2:
            dst = tokenList[0]
            command = tokenList[1]

            return dst, command
        return '', ''

    # #Prototype function
    # def updateInfo(self, string):
    #     for cmd in string:
    #         if cmd == 'TL':
    #             self.orient = (self.orient + 270) % 360

    #         elif cmd == 'TR':
    #             self.orient = (self.orient + 90) % 360

    #         elif cmd[0:2] == 'MF':
    #             if self.orient == 0:
    #                 self.Y += min(int(cmd[2]), 20)
    #             elif self.orient == 90:
    #                 self.X += min(int(cmd[2]), 15)
    #             elif self.orient == 180:
    #                 self.Y -= max(int(cmd[2]), 0)
    #             else:
    #                 self.X -= max(int(cmd[2]), 0)

    # #Prototype function
    # def getInfo(self):
    #     return 'INFO,' + str(self.X) + ',' + str(self.Y) + ',' + str(self.state) + ',' + str(self.orient)

    def readAndroid(self):
        if not self.android.isConnected():
            self.android.connectToAndroid()

        while True:
            string = self.android.receiveFromAndroid()
            string = str(string)
            
            self.writePC(string)
            self.writeAndroid("ACK")
            
            time.sleep(1)

    def writeAndroid(self, string=''):
        if self.android.isConnected() and string:
            self.android.sendToAndroid(string)

    def readArduino(self):
        if not self.arduino.isConnected():
            self.arduino.connectToArduino()

        while True:
            string = self.arduino.receiveFromArduino()
            string = str(string)
            if string == ' ' or string == '' or string == '/n' or string is None:
                continue
            
            self.writePC(string)
            
            time.sleep(1)

    def writeArduino(self, string=''):
        if self.arduino.isConnected() and string:
            self.arduino.sendToArduino(string)

    def readPC(self):
        if not self.pc.isConnected():
            self.pc.connectToPC()

        while True:
            string = self.pc.receiveFromPC()
            string = str(string)

            #Get logic command from string
            dst, command = self.processCommand(string)
            
            if dst == "AR":
                self.writeArduino(command)
                        
            elif dst == "AN":
                self.writeAndroid(command)
                
                self.writePC("ACK")
            
            time.sleep(0.7)

    def writePC(self, string=''):
        if self.pc.isConnected() and string:
            self.pc.sendToPC(string)

    def startProgram(self):
        #Assign threads
        readAndroidThread = threading.Thread(target= self.readAndroid, name= "readAndroid", daemon= True)
        writeAndroidThread = threading.Thread(target= self.writeAndroid, name= "writeAndroid", daemon= True)

        readArduinoThread = threading.Thread(target= self.readArduino, name= "readArduino", daemon= True)
        writeArduinoThread = threading.Thread(target= self.writeArduino, name= "writeArduino", daemon= True)

        readPCThread = threading.Thread(target= self.readPC, name= "readPC", daemon= True)
        writePCThread = threading.Thread(target= self.writePC, name= "writePC", daemon= True)

        #Running threads
        readAndroidThread.start()

        readArduinoThread.start()

        readPCThread.start()

    def disconnect(self):
        try:
            self.android.disconnectFromAndroid()
            self.arduino.disconnectFromArduino()
            self.pc.disconnectFromPC()
        except Exception as e:
            print("RPi - Caught error:")
            print(str(e))