import os
import threading
import time

from android import *
from arduino import *
from pc import *

class RaspberryPi():

    def __init__(self):

        #Current state of robot
        self.X = 0
        self.Y = 0
        self.state = 0
        #Current angle (0, 90, 180, 270)
        self.orient = 0

        #Define new interfaces
        self.android = AndroidInterface()
        self.arduino = ArduinoInterface()
        self.pc = PCInterface()
        
        print("RPi - Initialized all interfaces")
        
        #Initial connection
        self.android.connectToAndroid()
        self.arduino.connectToArduino()
        self.pc.connectToPC()

    def processCommand(self, string):
        tokenList = string.split("-")
        src = tokenList[0]
        dst = tokenList[1]
        command = tokenList[2:]

        return src, dst, command

    def updateInfo(self, string):
        for cmd in string:
            if cmd == 'TL':
                self.orient = (self.orient + 270) % 360

            elif cmd == 'TR':
                self.orient = (self.orient + 90) % 360

            elif cmd[0:2] == 'MF':
                if self.orient == 0:
                    self.Y += min(int(cmd[2]), 20)
                elif self.orient == 90:
                    self.X += min(int(cmd[2]), 15)
                elif self.orient == 180:
                    self.Y -= max(int(cmd[2]), 0)
                else:
                    self.X -= max(int(cmd[2]), 0)

    def getInfo(self):
        return 'INFO,' + str(self.X) + ',' + str(self.Y) + ',' + str(self.state) + ',' + str(self.orient)

    def readAndroid(self):
        if not self.android.isConnected():
            self.android.connectToAndroid()

        while True:
            string = self.android.receiveFromAndroid()
            string = str(string)

            #Get logic command from string
            src, dst, command = self.processCommand(string)
            
            if src == "AN":

                if dst == "AR":
                    self.updateInfo(command)
                    self.writeArduino(command)
                    self.writeAndroid("ACK")

                elif dst == "AL":
                    self.writePC(command)
                    self.writeAndroid("ACK")

            else:
                print("RPi - Error from readAndroid")
            
            time.sleep(1)

    def writeAndroid(self, string=''):
        if self.android.isConnected() and string:
            self.android.sendToAndroid(string)
            return True
        
        return False

    def readArduino(self):
        if not self.arduino.isConnected():
            self.arduino.connectToArduino()

        while True:
            string = self.arduino.receiveFromArduino()
            string = str(string)

            #Get logic command from string
            src, dst, command = self.processCommand(string)
            
            if src == "AR":

                if dst == "AN":
                    self.writeAndroid(command)

                elif dst == "AL":
                    self.writePC(command)
                
                self.writeArduino("ACK")
            
            else:
                print("RPi - Error from readArduino")
            
            time.sleep(1)

    def writeArduino(self, string=''):
        if self.arduino.isConnected() and string:
            self.arduino.sendToArduino(string)
            return True

        return False

    def readPC(self):
        if not self.pc.isConnected():
            self.pc.connectToPC()

        while True:
            string = self.pc.receiveFromPC()
            string = str(string)

            #Get logic command from string
            src, dst, command = self.processCommand(string)
            
            if src == "AL":

                if dst == "AR":
                    self.updateInfo(command)
                    self.writeArduino(command)
                        
                elif dst == "AN":
                    self.writeAndroid(command)
                
                self.writePC("ACK")
            
            else:
                print("RPi - Error from readPC")
            
            time.sleep(1)

    def writePC(self, string=''):
        if self.pc.isConnected() and string:
            self.pc.sendToPC(string)
            return True
        
        return False

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