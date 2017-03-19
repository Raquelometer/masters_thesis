import threespace as ts_api
import time
import math
import sys
import serial.tools.list_ports
import redis
import OSC
from OSC import OSCMessage

def main(redis_client):

	c = OSC.OSCClient()
	c.connect(('127.0.0.1', 7400))
	oscmsg = OSC.OSCMessage()
	gesture = OSC.OSCMessage()
	gesNum = OSC.OSCMessage()

	print("OSC initialized")

	oscmsg.setAddress("/startup")
	gesture.setAddress("/gesType")
	gesNum.setAddress("/gesNum")

	std3x = 0.03
	filter_flag = ts_api.TSS_FIND_ALL_KNOWN^ts_api.TSS_FIND_DNG

	# get comport???
	com_port = "/dev/cu.usbmodem1421"

	device = ts_api.TSUSBSensor(com_port=com_port)

	listening = True
	streaming = True

	while listening:

		key, message = redis_client.blpop('sensor')

		if message == "STOP" or message ==  "QUIT" or message == "NAME":
			device.close()
			listening = False
			print("Device closed. Session ended")

		
		if message == "START":

			streaming = True

			if device is not None:

				print(device)
				
				device.setFilterMode(mode = 1)

				#disable magnetometer
				device.setCompassEnabled(enabled=False)


				#Fix orientation
				device.setAxisDirections(ts_api.generateAxisDirections("YZX", neg_z = True))

				#stream only Gyro
				device.setStreamingSlots(slot0 = 'getCorrectedGyroRate', slot1 = 'getUntaredOrientationAsEulerAngles')

				#Fix rate
				device.setStreamingTiming(interval = 20000, duration = 0xFFFFFFFF, delay = 0)

				device.startStreaming()
				device.startRecordingData()

				## Now we can start getting the streaming data from the device.
				print("==================================================")
				print("Getting the streaming batch data.")

				
				num_samples = 0

				integrator_x = 0
				integrating_x = False
				integrator_y = 0
				integrating_y = False
				integrator_z = 0
				integrating_z = False 

				integrator_YAW = 0

				curr_degrees_z = 0

				mr_check = False
				diff_check = 0

				deltaT = 0
				prevTime = time.time()

				streamYaw = False

				while streaming:

					message = redis_client.lpop('sensor')

					if message == "QUIT":
						device.close()
						listening = False
						streaming = False
						print("device closed")

					if message == "STOP":
						
						streaming = False
						print("NOT STREAMING")

					
					deltaT = (1.0/50.0)
					num_samples += 1

					point1 = device.getLatestStreamData(40000)[1]
					
					gyro_x = point1[0]
					gyro_y = point1[1]
					gyro_z = point1[2]
					
					if abs(gyro_z) > 0.03 and not streamYaw:
					#if gyro_z < -0.03 and not streamYaw:
						integrating_z = True

					if integrating_z:

						integrator_z += gyro_z * deltaT
						degrees_z = math.degrees(integrator_z)

						if degrees_z < -5:

							mr_check = True
							#print('CHECKING')

						if mr_check:

							if gyro_z > 0.03:

								#print("MAXIMUM IS: ")
								#print(degrees_z)

								# set using heelTap and sideRoll thresholds?
								if degrees_z <= -30 and abs(degrees_y) < 25 and abs(degrees_x) < 30 and not diff_check:

									curr_degrees_z = degrees_z
									diff_check = 1

								if diff_check > 0:

									diff_check = diff_check + 1

									if diff_check > 12 and abs(degrees_z - curr_degrees_z) > 8:

										mr_check = False
										diff_check = 0
										integrator_z = 0
										integrating_z = False

										integrator_y = 0
										integrating_y = False

										integrator_x = 0
										integrating_x = False

										gesture.append("medialRot")
										gesNum.append(2)
										c.send(gesture)
										c.send(gesNum)
										gesture.pop(-1)
										gesNum.pop(-1)
										time.sleep(0.4)
										print('MR DETECTED')

									elif diff_check > 10 and abs(degrees_z - curr_degrees_z) < 8:

										print('NO MR DETECTED')

										mr_check = False

										diff_check = 0

										integrator_z = 0
										integrating_z = False

										integrator_y = 0
										integrating_y = False

										integrator_x = 0
										integrating_x = False

						'''
						if mr_check and degrees_z > -5 and degrees_z < 2:

							mr_check = False

							integrator_z = 0
							integrating_z = False

							integrator_y = 0
							integrating_y = False

							integrator_x = 0
							integrating_x = False

							gesture.append("medialRot")
							gesNum.append(2)
							c.send(gesture)
							c.send(gesNum)
							gesture.pop(-1)
							gesNum.pop(-1)
							time.sleep(0.4)
							print('MR DETECTED')
						'''

					#if abs(gyro_z) < 0.03:
						#integrating_z = False
					"""
					if gyro_z > 6.0 and not streamYaw:
						gesture.append("sideTap")
						gesNum.append(2)
						c.send(gesture)
						c.send(gesNum)
						gesture.pop(-1)
						gesNum.pop(-1)

						time.sleep(0.4)
					"""

					if abs(gyro_y) > 0.03:
						integrating_y = True

					if integrating_y:
						integrator_y += gyro_y * deltaT
						degrees_y = math.degrees(integrator_y)
						# check z as well? is this less ambiguous?
						if degrees_y > 30:

							integrator_y = 0
							integrating_y = False

							integrator_z = 0
							integrating_z = False

							integrator_x = 0
							integrating_x = False

							gesture.append("heelTap")
							gesNum.append(3)
							c.send(gesture)
							c.send(gesNum)
							gesture.pop(-1)
							gesNum.pop(-1)
							time.sleep(0.5)
							streamYaw = not streamYaw

					if integrating_z and abs(gyro_z) < 0.03:
						if not mr_check:
							integrating_z = False
							integrator_z = 0
							#print('integrator_z CLEARED')
					
					# Reset here at zero crossings? Do I need this?
					if integrating_y and abs(gyro_y) < 0.03:
						integrating_y = False
						#print(math.degrees(integrator_y))
						integrator_y = 0
						#print("===============")
						#print('integrator_y CLEARED')
				
					if abs(gyro_x) > 0.03:
						if not streamYaw:
							integrating_x = True

					if integrating_x:
						integrator_x += gyro_x * deltaT
						degrees_x = math.degrees(integrator_x)
						if degrees_x > 50:

							integrator_x = 0
							integrating_x = False

							integrator_z = 0
							integrating_z = False

							integrator_y = 0
							integrating_y = False

							gesture.append("sideRoll")
							gesNum.append(4)
							c.send(gesture)
							c.send(gesNum)
							gesture.pop(-1)
							gesNum.pop(-1)
							time.sleep(1)
						#print(math.degrees(integrator_x))
					

					if integrating_x and abs(gyro_x) < 0.03:
						integrating_x = False
						#print(math.degrees(integrator_x))
						integrator_x = 0
						#print('integrator_x CLEARED')
						#print("===============")

					if not streamYaw:
						integrator_YAW = 0

					if streamYaw:
						integrator_YAW += gyro_z * deltaT
						degrees_YAW = math.degrees(integrator_YAW)

						oscmsg.append(degrees_YAW)
						c.send(oscmsg)
						oscmsg.pop(-1)

	## Now close the port.
	c.close()
		

if __name__ == '__main__':
	redis_client = redis.StrictRedis(host='localhost', port=6379)
	main(redis_client)