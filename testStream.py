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

oscmsg.setAddress("/startup")
gesture.setAddress("/gesType")

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
	device.setStreamingSlots( slot0 = 'getUntaredOrientationAsEulerAngles')
	
	## Now we can start getting the streaming batch data from the device.
	print("==================================================")
	print("Getting the streaming batch data.")
	start_time = time.clock()
	roll_prev = 0
	num_samples = 0
	while time.clock() - start_time < 3:
		num_samples += 1
		print(device.getStreamingBatch())
		point1 = device.getStreamingBatch()
		#if point1[0] < .12:
		
		num = point1[0]
		num2 = point1[1]
		num3 = point1[2]

		if roll_prev > 0 and num3 < 0:
			num3 = roll_prev

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

		if abs(num - num3) <= 0.25 and num < 0:
		#if num < 0 and num3 <0:
			gesture.append("sideTap")
			c.send(gesture)
			gesture.pop(-1)
			time.sleep(0.5)

		elif num < -1.2 and num3 > 0.6:
			gesture.append("tapBack")
			c.send(gesture)
			gesture.pop(-1)
			#put in a delay?
			time.sleep(0.5)

		
		elif num < -.79 and num3 < 0.25:
			# is it really front tap, or is it on the
			# way to a back tap
			gesture.append("tapFront")
			c.send(gesture)
			gesture.pop(-1)
			#time.sleep(0.3)

		if num > 0.2:
			gesture.append("heelTap")
			c.send(gesture)
			gesture.pop(-1)
		
		#elif num3 < 0 and num < 0 and num3 < num and num > -1.3:
	

		roll_prev = num3

			#c.send(OSCMessage("/user/Daphna", [3.0]))
		print("=======================================\n")
	## Now close the port.
	print("Num samples: ")
	print(num_samples)
	c.close()
	device.close()