import sys
import serial
import time
import struct

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
                # self.servoTemp = serial.Serial(SERVO_PORT_TEMP, self.baudRate, timeout=3)
                time.sleep(0.1)

                if self.servo != 0:
                    print ("Arduino - Connected")
                    self.setConnection(True)
                    break

                self.servo = serial.Serial(SERVO_PORT1, self.baudRate)
                if self.servo != 0:
                    print ("Arduino - Connected")
                    self.setConnection(True)
                    break

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
            # print ("Arduino - Failed to send message to Arduino")
            # self.connectToArduino()

    def receiveFromArduino (self):
        try:
            string = self.servo.read(self.servo.inWaiting())
            while len(string) < 33:
                # print('Loop 1')
                # print(string)
                string += self.servo.read(1)
            # string = self.servo.readline()
            if "IR" in str(string):
                sensor1 = struct.unpack('<f', string[3:7])[0]
                sensor2 = struct.unpack('<f', string[8:12])[0]
                sensor3 = struct.unpack('<f', string[13:17])[0]
                sensor4 = struct.unpack('<f', string[18:22])[0]
                sensor5 = struct.unpack('<f', string[23:27])[0]
                sensor6 = struct.unpack('<f', string[28:32])[0]
                resultString = "IR," + str(sensor1) + "," + str(sensor2) + "," + str(sensor3) + "," + str(sensor4) + "," + str(sensor5) + "," + str(sensor6)
                print ("Arduino - Received from Arduino: %s" % resultString)
                return resultString

            # decodedString = string.decode('utf-8')
            # decodedString = str(decodedString)
            if string:
                print ("Arduino - Received from Arduino: %s" % string)
                return string

        except Exception as e:
            print ("Arduino - Caught error:")
            print(str(e))
            raise e
            # print ("Arduino - Failed to receive message from Arduino")
            # self.connectToArduino()