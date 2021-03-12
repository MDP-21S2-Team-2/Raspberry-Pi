import sys
import serial
import time

from configuration import *

class ArduinoInterface():
    
    def __init__(self):
        self.baudRate = BAUD_RATE
        self.servo = 0
        self.servoTemp = 0
        self.connection = False
        
    def isConnected (self):
        return self.isConnected
    
    def setConnection(self, state):
        self.connection = state

    def connectToArduino (self):
        try:
            while True:
                #Attempting to connect to Arduino
                print ("Arduino - Connecting to Arduino")
                self.servo = serial.Serial(SERVO_PORT, self.baudRate)

                if self.servo != 0:
                    print ("Arduino - Connected")
                    self.setConnection(True)
                    break

                # self.servo = serial.Serial(SERVO_PORT1, self.baudRate)
                # if self.servo != 0:
                #     print ("Arduino - Connected")
                #     self.setConnection(True)
                #     break

        except Exception as e:
            print ("Arduino - Caught error:")
            print(str(e))
            print ("Arduino - Connection failed")
            raise e

    def disconnectFromArduino (self):
        try:
            self.servo.close()
            self.setConnection(False)
            print("Arduino - Disconnected")

        except Exception as e:
            print ("Arduino - Caught error:")
            print(str(e))
            print ("Arduino - Disconnection failed")
            raise e

    def sendToArduino (self, string):
        try:
            encodedString = string.encode()
            self.servo.write(encodedString)
            print ("Arduino - Sent to Arduino: %s" % string)
		
        except Exception as e:
            print ("Arduino - Caught error:")
            print(str(e))
            raise e

    def receiveFromArduino (self):
        try:
            string = self.servo.readline()
            # decodedString = string.decode('utf-8')
            # decodedString = str(decodedString)
            if len(string) > 0:
                print ("Arduino - Received from Arduino: %s" % string)
                return string

        except Exception as e:
            print ("Arduino - Caught error:")
            print(str(e))