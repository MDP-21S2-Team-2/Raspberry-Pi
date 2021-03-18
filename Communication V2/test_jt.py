import serial
import time
import struct

ser = serial.Serial("/dev/ttyACM0", 115200)

#command = raw_input("Enter command: ")
#ser.write(command)

while True:
	command = raw_input("Enter command: ")
	print("Command: " + command)
	if command == 'exit':
		break
	ser.write(command)

	print("Command sent")

	while not ser.inWaiting():
		continue

	print("Data received")

	data = ser.read(ser.inWaiting())
	while '\n' not in data:  # '\n'
		while not ser.inWaiting():
			continue
		data += ser.read(1)
	print(data)

	data = ser.read(ser.inWaiting())
	while '\n' not in data:
		while not ser.inWaiting():
			continue
		data += ser.read(1)
	print(data)

#	data = ser.read(ser.inWaiting())
#	while len(data) < 10:
#	while '\n' not in data:
#		data += ser.read(1)

#	s1 = struct.unpack('<i', data[0:4])[0]
#	s2 = struct.unpack('<i', data[5:9])[0]
#	s3 = struct.unpack('<f', data[13:17])[0]
#	s4 = struct.unpack('<f', data[18:22])[0]
#	s5 = struct.unpack('<f', data[23:27])[0]
#	s6 = struct.unpack('<f', data[28:32])[0]
#	print("IR," + str(s1) + "," + str(s2) + "," + str(s3) + "," + str(s4) + "," + str(s5) + "," + str(s6))
#	print(data)
#	print("TicksL: " + str(s1) + ", TicksR: " + str(s2))

ser.close()

print("Done")
