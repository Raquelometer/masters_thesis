import threespace as ts_api
import time
import math
import sys
import redis
import thesis_utils
from three_axis_integrator import three_axis_integrator
import OSC
from OSC import OSCMessage

# clean up and comment integration, preprocess, plot_data, 'plot multiple', detecor_sim, stream_data, fft, plotconfmat?
# add README 

def main(redis_client):

	c = OSC.OSCClient()
	c.connect(('127.0.0.1', 7400))

	yawmsg = OSC.OSCMessage()
	gesture = OSC.OSCMessage()
	gesNum = OSC.OSCMessage()

	print("OSC initialized")

	yawmsg.setAddress("/yaw")
	gesture.setAddress("/gesType")
	gesNum.setAddress("/gesNum")

	# 3 times standard deviation of sensor signal at rest
	STD3x = 0.03
	sampling_rate = 20000
	
	filter_flag = ts_api.TSS_FIND_ALL_KNOWN^ts_api.TSS_FIND_DNG
	com_port = thesis_utils.get_comport()
	device = ts_api.TSUSBSensor(com_port=com_port)

	listening = True
	streaming = True

	while listening:

		key, message = redis_client.blpop('sensor')

		if message == 'NAME':
			filename = raw_input('Enter name as subjectID_description:  ')
			filename = filename + '.csv'
			print("Press start when ready")

		if message ==  "QUIT":
			device.close()
			listening = False
			print("Device closed. Session ended")
		
		if message == "START":

			streaming = True

			if device is not None:

				print(device)

				#function for device setup in utils, take in interval

				thesis_utils.setup_sensor(device, sampling_rate)

				device.startStreaming()
				device.startRecordingData()

				## Now we can start getting the streaming data from the device.
				print("==================================================")
				print("Getting the streaming data.")

				opened = False

				delayCounter = 0

				sample_count = 0

				integrator = three_axis_integrator()

				# Variables for the medial rotation gesture
				mr_counter = 0

				integrator_YAW = 0

				curr_degrees_z = 0

				mr_check = False
				diff_check = 0

				deltaT = (1.0/50.0)
				#prevTime = time.time()

				streamYaw = False

				while streaming:

					message = redis_client.lpop('sensor')

					if message == 'STOP':
						
						streaming = False
						
						sample_count = 0
						opened = False
						
						print("Not streaming. Enter new filename")

					elif message == 'QUIT':
						device.close()
						listening = False
						print("Device closed. Session ended")

					else: 
						
						point1 = device.getLatestStreamData(40000)[1]
						
						# Handle writing to CSV
						thesis_utils.data_to_csv(point1, opened, filename, sample_count)

						# maybe this can happen inside CSV function anyway
						sample_count = sample_count + 1
						opened = True

						# counts a delay without calling sleep function
						# this is for data collection purposes

						if delayCounter > 0:
							delayCounter = thesis_utils.delay_counter(delayCounter)

						#actual data stuff starts here
						
						gyro_x = point1[0]
						gyro_y = point1[1]
						gyro_z = point1[2]
						
						if abs(gyro_z) > STD3x and not streamYaw and delayCounter == 0:
						#if gyro_z < -0.03 and not streamYaw:
							integrator.integrating_z  = True
							
						if integrator.integrating_z:

							integrator.theta_z += gyro_z * deltaT
							degrees_z = math.degrees(integrator.theta_z)

							# If an inward rotation of the foot is detected
							if degrees_z < -40 and degrees_y < 27 and degrees_x < 35:

								# Start checking if it's a full in/out rotation
								mr_check = True
								
							if mr_check:
								# retroactivley check was degrees_z a minimum?if not, reset!
								# positive crossing - find maximum
								# how to check if it DIDN'T cross??? and then reset?? GET OUT OF MRCHECK
								# add another counter??

								# give performer time to return to home position
								mr_counter += 1

								if mr_counter > 75:
									#reset everything
									mr_check = False
									mr_counter = 0

									integrator.reset_all_axes()
									
									print("timout on MR")

								# positive gyro value means foot has changed direction and is rotating back to home
								# Basically this is detecting a zero crossing
								elif gyro_z > STD3x:

									if not diff_check:

										# save degrees at moment of zero crossing
										curr_degrees_z = degrees_z
										diff_check = 1

									if diff_check > 0:

										diff_check = diff_check + 1

										# allow TODO seconds for player to return to home position
										# Triggers only if foot has moved back more than 8 degrees
										# This is in order to avoid triggering if the player merely rotates
										if diff_check > 12 and abs(degrees_z - curr_degrees_z) > 8:

											mr_check = False
											mr_counter = 0
											diff_check = 0

											integrator.reset_all_axes()

											thesis_utils.gesture_to_max(c, gesture, gesNum, "medialRot", 2)

											#time.sleep(0.4)
											
											delayCounter += 1

											print('MR DETECTED')

										elif diff_check > 12 and abs(degrees_z - curr_degrees_z) < 8:

											print('NO MR DETECTED')
											mr_counter = 0

											mr_check = False

											diff_check = 0

											integrator.reset_all_axes()
											
											delayCounter = 0					

						if abs(gyro_y) > STD3x and delayCounter == 0:
							integrator.integrating_y = True

						if integrator.integrating_y:
							integrator.theta_y += gyro_y * deltaT
							degrees_y = math.degrees(integrator.theta_y)
							# check z as well? is this less ambiguous?
							if degrees_y >= 30:

								integrator.reset_all_axes()

								thesis_utils.gesture_to_max(c, gesture, gesNum, "heelTap", 3)
								
								#time.sleep(0.5)
								print("Heel Tap DETECTED")
								delayCounter += 1
								streamYaw = not streamYaw
								if not streamYaw:
									integrator_YAW = 0

						# Reset if a gesture has not been detected	

						if integrator.integrating_z and abs(gyro_z) < STD3x:
							if not mr_check:

								integrator.reset_z()
														
						# Reset here at zero crossings? Do I need this?
						if integrator.integrating_y and abs(gyro_y) < STD3x:
							integrator.reset_y()							
					
						if abs(gyro_x) > STD3x:
							if not streamYaw and delayCounter == 0:
								integrator.integrating_x = True

						if integrator.integrating_x:
							integrator.theta_x += gyro_x * deltaT
							degrees_x = math.degrees(integrator.theta_x)
							if degrees_x >= 40:

								integrator.reset_all_axes()

								thesis_utils.gesture_to_max(c, gesture, gesNum, "sideRoll", 4)					

								print("Foot roll DETECTED")
								#time.sleep(1)
								delayCounter += 1
						
						if integrator.integrating_x and abs(gyro_x) < STD3x:
							integrator.reset_x()							

						if streamYaw:
							integrator.reset_z()
							
							integrator_YAW += gyro_z * deltaT
							degrees_YAW = math.degrees(integrator_YAW)

							thesis_utils.stream_to_max(c, yawmsg, degrees_YAW)

	## Now close the port.
	c.close()
		

if __name__ == '__main__':
	redis_client = redis.StrictRedis(host='localhost', port=6379)
	main(redis_client)