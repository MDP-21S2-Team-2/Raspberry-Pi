import time
import sys

from rpiMultiprocess import *

if __name__ == "__main__":

    print("RPi - Program is starting")
    if len(sys.argv) > 1:
        imgRec = int(sys.argv[1])
    else:
        imgRec = 0
    program = RaspberryPi(imgRec)
    
    try:
        program.startProgram()
        while True:
            pass
    
    except KeyboardInterrupt:
        print("RPi - Ending the program")
        program.disconnect()
        print("Rpi - Exiting")
    