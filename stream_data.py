import redis
import threespace as ts_api
import time
import sys
import csv
import serial.tools.list_ports

def get_comport():
	
	port_found = False
	com_port = "0000"

	options = serial.tools.list_ports.comports()
	print options

	# TODO this should possibly match vid as well
	for port in options:

		#TODO check cross mac functionality...
		if port[2] == "USB VID:PID=2476:1010 SNR=None":
			com_port = port[0]
			port_found = True
			print ("device found: " + com_port)
			return com_port

	if port_found == False:
		print ("Device not found")
		return None

def data_to_csv(sample, opened, name, sample_count):
	if not opened:
		with open(name, 'w') as batch_data:
		
			#Declare fieldnames
			fieldnames = ['count','q1','q2','q3','q4','AccelRawX','AccelRawY','AccelRawZ','GyroRawX','GyroRawY','GyroRawZ']

			#Set field names in the CSV file
			writer = csv.DictWriter(batch_data, fieldnames = fieldnames)

			#Create header
			writer.writeheader()

			# write sample to the file
			writer.writerow({'count' : sample_count, 'q1' : sample[0], 'q2' : sample[1], 'q3' : sample[2], 'q4' : sample[3]})
	else:
		with open(name, 'a') as batch_data:

			writer = csv.writer(batch_data)
			tuple_count = (sample_count,)
			sample_withcount = tuple_count + sample
			writer.writerow(sample_withcount)

def main(redis_client):

	listening = True
	opened = False

	# These variables determine the filename scheme
	# Counter variable keeps track of number of csv files stored per session
	subject = ''
	gesture_type = ''
	count = 0
	sample_count = 0

	# connect sensor to port on machine
	filter_flag = ts_api.TSS_FIND_ALL_KNOWN^ts_api.TSS_FIND_DNG
	com_port = get_comport()
	device = ts_api.TSUSBSensor(com_port=com_port)
	
	while listening:

		key, message = redis_client.blpop('sensor')
		streaming = True

		if message == 'QUIT':
			device.close()
			listening = False
			print("Device closed. Session ended")


		if message == 'NAME':
			subject = raw_input('Enter subject number: ')
			gesture_type = raw_input('Enter gesture type: ')
			print("Press start when ready")

		if message == 'START':

			print("Received start command")

			#filter_flag = ts_api.TSS_FIND_ALL_KNOWN^ts_api.TSS_FIND_DNG
			#com_port = get_comport()
			#device = ts_api.TSUSBSensor(com_port=com_port)

			

			if device is not None:

				print(device)

				#disable magnetometer
				device.setCompassEnabled(enabled=False)

				#set slots for quaternion and raw batch data
				device.setStreamingSlots(
					slot0='getTaredOrientationAsQuaternion', 
					slot1='getCorrectedAccelerometerVector', 
					slot2='getCorrectedGyroRate')

				print("==================================================")
				print("Getting the streaming batch data.")

				while streaming:

					message = redis_client.lpop('sensor')

					if message == 'STOP':
						#close device
						#device.close()
						streaming = False
						count = count + 1
						#listening = False
						#print("Device closed")
					elif message == 'QUIT':
						device.close()
						listening = False
						print("Device closed. Session ended")
					else:

						# write batch data to csv file here
						if count < 10:
							countstr = '0' + str(count)
						filename = subject + '_' + gesture_type + countstr + '.csv'
						sample = device.getStreamingBatch()
						
						data_to_csv(sample, opened, filename, sample_count)
						sample_count = sample_count + 1
						opened = True

						print(sample)
						print("=======================================\n")

	print("End of session")




if __name__ == '__main__':
	redis_client = redis.StrictRedis(host='localhost', port=6379)
	main(redis_client)
	