import time
import sys

# from raspberrypi import *
from rpiMultiprocess import *
# from raspberrypiDraft import *

if __name__ == "__main__":

    print("RPi - Program is starting")
    program = RaspberryPi(int(sys.argv[1]))
    
    try:
        program.startProgram()
        while True:
            pass
    
    except KeyboardInterrupt:
        print("RPi - Ending the program")
        program.disconnect()
        print("Rpi - Exiting")
    