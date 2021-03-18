import os
from multiprocessing import Process, Value
from multiprocessing.managers import BaseManager
import collections
from datetime import datetime
import time

from android import *
from arduino import *
from pc import *

class DequeManager(BaseManager):
    pass
    
class DequeProxy(object):
    def __init__(self, *args):
        self.deque = collections.deque(*args)
    def __len__(self):
        return self.deque.__len__()
    def appendleft(self, x):
        self.deque.appendleft(x)
    def append(self, x):
        self.deque.append(x)
    def popleft(self):
        return self.deque.popleft()
        
DequeManager.register('DequeProxy', DequeProxy,
                      exposed=['__len__', 'append', 'appendleft', 'popleft'])

class RaspberryPi():

    def __init__(self, imgRecOn):

        # #Current state of robot (Prototype)
        # self.X = 0
        # self.Y = 0
        # self.state = 0
        # #Current angle (0, 90, 180, 270)
        # self.orient = 0

        #Check whether do image recognition or not
        self.imgRec = imgRecOn

        #Check which connection was lost
        self.connectionLost = Value('i', 0)

        #Define new interfaces
        self.arduino = ArduinoInterface()
        self.android = AndroidInterface()
        self.pc = PCInterface()
        
        print("RPi - Initialized all interfaces")
        
        #Initial connection
        self.arduino.connectToArduino()
        self.android.connectToAndroid()
        self.pc.connectToPC()
        if self.imgRec == 1:
            self.pc.connectToImg()


    def processCommand(self, string):
        tokenList = string.split("-")
        if len(tokenList) >= 2:
            dst = tokenList[0]
            command = tokenList[1]

            return dst, command
        return '', ''
    
    def formatCommand(self, source, target, command):
        return {
            'source': source,
            'target': target,
            'command': command
        }

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
        # if not self.android.isConnected():
        #     self.android.connectToAndroid()

        while True:
            try:
                string = self.android.receiveFromAndroid()
                string = str(string)
                if string is None:
                    continue
            
                self.messageDeque.append(self.formatCommand('AN', 'AL', string))
            except Exception as error:
                print('Error in process readAndroid: ' + str(error))
                break
            
            # time.sleep(1)

    def readArduino(self):
        # if not self.arduino.isConnected():
        #     self.arduino.connectToArduino()

        while True:
            try:
                string = self.arduino.receiveFromArduino()
                if string != None and len(string) > 0:
                    self.messageDeque.append(self.formatCommand('AR', 'AL', string))

            except Exception as error:
                print('Error in process readArduino : ' + str(error))
                break

    def readPC(self):
        # if not self.pc.isConnected():
        #     self.pc.connectToPC()

        while True:
            try:
                string = self.pc.receiveFromPC()
                string = str(string)
                if string is None:
                    continue

                #Get logic command from string
                target, command = self.processCommand(string)
                
                if self.imgRec == 1 and "ROBOT" in command:
                    self.messageDeque.append(self.formatCommand('AL', 'IMG', command))
                    self.messageDeque.append(self.formatCommand('AL', target, command))
                    #time.sleep(0.2)
                else:
                    self.messageDeque.append(self.formatCommand('AL', target, command))
            except Exception as error:
                print('Error in process readPC: ' + str(error))
                break    
    
    def readImg(self):
        while True:
            try:
                string = self.pc.receiveFromImgRec()
                string = str(string)
                if string is None:
                    continue
                
                if 'IMAGE' in string:
                    self.messageDeque.append(self.formatCommand('IMG', 'AN', string))
                if 'STOP' in string:
                    self.messageDeque.append(self.formatCommand('IMG', 'AL', string))
                    self.messageDeque.append(self.formatCommand('IMG', 'AR', 'T'))
            except Exception as error:
                print('Error in process readImg: ' + str(error))
                break

    def writeTarget(self, string=''):
        while True:
            source = None
            target = None
            command = None
            try:
                if len(self.messageDeque) > 0:
                    message = self.messageDeque.popleft()
                    source, target, command = message['source'], message['target'], message['command']

                    if source == 'AL':
                        if target == 'AR':
                            self.arduino.sendToArduino(command)
                        elif target == 'IMG':
                            self.pc.sendToImgRec(command)
                        elif target == 'AN':
                            self.android.sendToAndroid(command)
                            self.pc.sendToPC('ACK')

                    elif source == 'AN':
                        self.pc.sendToPC(command)
                        self.android.sendToAndroid('ACK')

                    elif source == 'AR':
                        self.pc.sendToPC(command)

                    elif source == 'IMG':
                        if target == 'AN':
                            self.android.sendToAndroid(command)
                        elif target == 'AL':
                            self.pc.sendToPC(command)
                        elif target == 'AR':
                            self.arduino.sendToArduino(command)
                            
                    else:
                        print("Invalid header: " + message)
                
            except Exception as error:
                print('Process writeTarget failed: ' + str(error))
                
                if target == 'AR':
                    self.connectionLost.value = 0
                elif target == 'AL':
                    self.connectionLost.value = 1
                elif target == 'AN':
                    self.connectionLost.value = 2
                elif target == 'IMG':
                    self.connectionLost.value = 3
                
                self.messageDeque.appendleft(message)
                
                break

    def startProgram(self):
        try:
            #Assign process
            self.manager = DequeManager()
            self.manager.start()

            self.messageDeque = self.manager.DequeProxy()

            self.readArduinoProcess = Process(target=self.readArduino)
            self.readPCProcess = Process(target=self.readPC)
            self.readAndroidProcess = Process(target=self.readAndroid)
            if self.imgRec == 1:
                self.readImgProcess = Process(target=self.readImg)
            
            self.writeTargetProcess = Process(target=self.writeTarget)

            #Running threads
            self.readArduinoProcess.start()
            self.readPCProcess.start()
            self.readAndroidProcess.start()
            if self.imgRec == 1:
                self.readImgProcess.start()
            
            self.writeTargetProcess.start()

            print('All processes started')

        except Exception as error:
            raise error

        self.allowReconnect()

    def allowReconnect(self):
        print('Please reconnect to RPi after disconnecting')
        while True:
            try:
                if not self.readArduinoProcess.is_alive():
                    self.reconnectArduino()
                    
                if not self.readPCProcess.is_alive():
                    self.reconnectPC()
                    
                if not self.readAndroidProcess.is_alive():
                    self.reconnectAndroid()

                if self.imgRec == 1 and not self.readImgProcess.is_alive():
                    self.reconnectImg()
                    
                if not self.writeTargetProcess.is_alive():
                    if self.connectionLost.value == 0:
                        self.reconnectArduino()
                    elif self.connectionLost.value == 1:
                        self.reconnectPC()
                    elif self.connectionLost.value == 2:
                        self.reconnectAndroid()
                    elif self.imgRec == 1 and self.connectionLost.value == 3:
                        self.reconnectImg()
                
                # if self.image_process is not None and not self.image_process.is_alive():
                #    self.image_process.terminate()
                    
            except Exception as error:
                print("Error during reconnection: ", error)
                raise error

    def reconnectArduino(self):
        self.arduino.disconnectFromArduino()
        
        self.readArduinoProcess.terminate()
        self.writeTargetProcess.terminate()

        self.arduino.connectToArduino()

        self.readArduinoProcess = Process(target=self.readArduino)
        self.readArduinoProcess.start()

        self.writeTargetProcess = Process(target=self.writeTarget)
        self.writeTargetProcess.start()

        print('Reconnected to Arduino')

    def reconnectPC(self):
        self.pc.disconnectFromPC()
        
        self.readPCProcess.terminate()
        self.writeTargetProcess.terminate()

        self.pc.connectToPC()

        self.readPCProcess = Process(target=self.readPC)
        self.readPCProcess.start()

        self.writeTargetProcess = Process(target=self.writeTarget)
        self.writeTargetProcess.start()

        print('Reconnected to Algorithm')

    def reconnectAndroid(self):
        self.android.disconnectFromAndroid()
        
        self.readAndroidProcess.terminate()
        self.writeTargetProcess.terminate()
        
        self.android.connectToAndroid()
        
        self.readAndroidProcess = Process(target=self.readAndroid)
        self.readAndroidProcess.start()
        
        self.writeTargetProcess = Process(target=self.writeTarget)
        self.writeTargetProcess.start()

        print('Reconnected to Android')

    def reconnectImg(self):
        self.pc.disconnectFromImgRec()

        self.readImgProcess.terminate()
        self.writeTargetProcess.terminate()

        self.pc.connectToImg()

        self.readImgProcess = Process(target=self.readImg)
        self.readImgProcess.start()

        self.writeTargetProcess = Process(target=self.writeTarget)
        self.writeTargetProcess.start()

        print('Reconnected to ImgRec')

    def disconnect(self):
        try:
            self.android.disconnectFromAndroid()
            self.arduino.disconnectFromArduino()
            self.pc.disconnectFromPC()
        except Exception as error:
            print("RPi - Caught error:" + str(error))
            raise error
