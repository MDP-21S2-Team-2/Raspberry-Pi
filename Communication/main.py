import time

from raspberrypi import *

if __name__ == "__main__":

    print("RPi - Program is starting")
    program = RaspberryPi()
    
    try:
        program.startProgram()
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("RPi - Ending the program")
        program.disconnect()
        print("Rpi - Exiting")
    