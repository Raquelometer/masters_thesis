import threespace as ts_api
import time
import sys
import serial.tools.list_ports
import matplotlib.pyplot as plt
import OSC
from OSC import OSCMessage


c = OSC.OSCClient()
c.connect(('127.0.0.1', 7400))
oscmsg = OSC.OSCMessage()
gesture = OSC.OSCMessage()
gesNum = OSC.OSCMessage()

oscmsg.setAddress("/startup")
gesture.setAddress("/gesType")
gesNum.setAddress("/gesNum")

filter_flag = ts_api.TSS_FIND_ALL_KNOWN^ts_api.TSS_FIND_DNG
com_port = "/dev/cu.usbmodem1411"

device = ts_api.TSUSBSensor(com_port=com_port)

## If a connection to the COM port fails, None is returned.
if device is not None:
	print(device)
	## Set the stream slots for getting the tared orientation of the device as a
	## quaternion, the raw component data, and the button state
	#device.setStreamingSlots(   slot0='getTaredOrientationAsQuaternion',
	#							slot1='getAllRawComponentSensorData',
	#							slot2='getButtonState')
	#device.setStreamingSlots(   slot0='getTaredOrientationAsQuaternion')
	#device.setStreamingSlots( slot0 = 'getAllRawComponentSensorData')


	#disable magnetometer
	device.setCompassEnabled(enabled=False)

	#Fix orientation
	device.setAxisDirections(ts_api.generateAxisDirections("YZX", neg_z = True))
	device.setStreamingSlots( slot0 = 'getUntaredOrientationAsEulerAngles', slot1 = 'getCorrectedGyroRate')
	
	## Now we can start getting the streaming batch data from the device.
	print("==================================================")
	print("Getting the streaming batch data.")
	start_time = time.clock()
	roll_prev = 0
	num_samples = 0
	backOrFront = False
	delayTrack = 0;

	while time.clock() - start_time < 5:

		
		
		currMinPitch = 0;
		num_samples += 1
		print(device.getStreamingBatch())
		point1 = device.getStreamingBatch()
		#if point1[0] < .12:
		
		num = point1[0]
		num2 = point1[1]
		num3 = point1[2]

		#if roll_prev > 0 and num3 < 0:
			#num3 = roll_prev

		#if roll_prev < 0 and num3 > 0:
			#num3 = roll_prev

		oscmsg.append(num)
		oscmsg.append(num2)
		oscmsg.append(num3)
		c.send(oscmsg)

		


		oscmsg.pop(-1)
		oscmsg.pop(-1)
		oscmsg.pop(-1)

		#if num < -.8 and num3 > 2.0:

		#if abs(num - num3) <= 0.1 and num < 0:
		#if num < 0 and num3 <0:

		if num < -0.6:
			backOrFront = True
			"""
			gesture.append("backOrFront")
			c.send(gesture)
			gesture.pop(-1)
			"""

		if point1[5] < -5.5:
			gesture.append("inTap")
			gesNum.append(1)
			c.send(gesture)
			c.send(gesNum)
			gesture.pop(-1)
			gesNum.pop(-1)
			time.sleep(0.3)

		if point1[5] > 6.0:
			gesture.append("sideTap")
			gesNum.append(2)
			c.send(gesture)
			c.send(gesNum)
			gesture.pop(-1)
			gesNum.pop(-1)
			time.sleep(0.4)

		# daphna if num > 0.2:
		#kiran
		if num > 0.05 and num > num3:
			gesture.append("heelTap")
			gesNum.append(3)
			c.send(gesture)
			c.send(gesNum)
			gesture.pop(-1)
			gesNum.pop(-1)
			time.sleep(0.5)
		# Daphna
		#if num3 < -0.7 and num > -0.2:
		# us absolute value????
		# Kiran
		#if num3 < -0.7 and num3 < num:
		if abs(num3) > 1.2 and num > -1:
			gesture.append("sideRoll")
			gesNum.append(4)
			c.send(gesture)
			c.send(gesNum)
			gesture.pop(-1)
			gesNum.pop(-1)
			time.sleep(0.5)
		"""
		if num3 > 1:
			gesture.append("sideKick")
			c.send(gesture)
			gesture.pop(-1)
			time.sleep(0.4)
		"""

		"""
		if num < -1.2:
			gesture.append("tapBack")
			c.send(gesture)
			gesture.pop(-1)
			time.sleep(0.5)
			"""


		if(backOrFront):
			#if point1[3] < -5 and num < -1.2 and num3 > 0.5:
			delayTrack += 1

			if delayTrack >= 30:

				if num < -1.2:
					gesture.append("tapBack")
					c.send(gesture)
					gesture.pop(-1)
					time.sleep(0.5)


				elif num < -0.6:
					gesture.append("tapFront")
					c.send(gesture)
					gesture.pop(-1)

				delayTrack = 0
				backOrFront = False



			"""
			else:	
				if currMinPitch < -1.2 and num3 > 0.5:
				#if point1[3] < -5.0:
					gesture.append("tapBack")
					c.send(gesture)
					gesture.pop(-1)
					#put in a delay?
					time.sleep(0.5)
					currMinPitch = 0

		
				elif currMinPitch < -.78 and num3 < 0.25:
					# is it really front tap, or is it on the
					# way to a back tap
					# try using gyro 
					gesture.append("tapFront")
					c.send(gesture)
					gesture.pop(-1)
					#time.sleep(0.3)
					currMinPitch = 0
			backOrFront = False
			"""

		
		
		#elif num3 < 0 and num < 0 and num3 < num and num > -1.3:
	

		roll_prev = num3

			#c.send(OSCMessage("/user/Daphna", [3.0]))
		print("=======================================\n")
	## Now close the port.
	print("Num samples: ")
	print(num_samples)
	c.close()
	device.close()