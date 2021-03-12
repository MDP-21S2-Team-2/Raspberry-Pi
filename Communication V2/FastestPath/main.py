import time

from rpiMultiprocess import *

if __name__ == "__main__":

    print("RPi - Program is starting")
    program = RaspberryPi()
    
    try:
        program.startProgram()
        while True:
            pass
    
    except KeyboardInterrupt:
        print("RPi - Ending the program")
        program.disconnect()
        print("Rpi - Exiting")
    