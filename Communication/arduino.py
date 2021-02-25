import sys
import serial
import time

from configuration import *

class ArduinoInterface():
    
    def __init__(self):
        self.baudRate = BAUD_RATE
        self.servo = 0
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
                self.servo = serial.Serial(SERVO_PORT, self.baudRate, timeout=3)
                time.sleep(1)

                if(self.servo != 0):
                    print ("Arduino - Connected")
                    self.setConnection(True)
                    break

        except Exception as e:
            print ("Arduino - Caught error:")
            print(str(e))
            print ("Arduino - Connection failed")

    def disconnectFromArduino (self):
        try:
            self.servo.close()
            self.setConnection(False)
            print("Arduino - Disconnected")

        except Exception as e:
            print ("Arduino - Caught error:")
            print(str(e))
            print ("Arduino - Disconnection failed")

    def sendToArduino (self, string):
        try:
            encodedString = string.encode()
            self.servo.write(encodedString)
            print ("Arduino - Sent to Arduino: %s" % string)
		
        except Exception as e:
            print ("Arduino - Caught error:")
            print(str(e))
            print ("Arduino - Failed to send message to Arduino")
            self.connectToArduino()

    def receiveFromArduino (self):
        try:
            string = self.servo.readline()
            decodedString = string.decode('utf-8')
            decodedString = str(decodedString)
            print ("Arduino - Received from Arduino: %s" % decodedString)
            return decodedString

        except Exception as e:
            print ("Arduino - Caught error:")
            print(str(e))
            print ("Arduino - Failed to receive message from Arduino")
            self.connectToArduino()