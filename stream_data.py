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

def data_to_csv(sample, opened):
	if not opened:
		with open('name_x.csv', 'w') as batch_data:
		
			#Declare fieldnames
			fieldnames = ['q1','q2','q3','q4','AccelRawX','AccelRawY','AccelRawZ','GyroRawX','GyroRawY','GyroRawZ']

			#Set field names in the CSV file
			writer = csv.DictWriter(batch_data, fieldnames = fieldnames)

			#Create header
			writer.writeheader()

			# write sample to the file
			writer.writerow({'q1' : sample[0], 'q2' : sample[1], 'q3' : sample[2], 'q4' : sample[3]})
	else:
		with open('name_x.csv', 'a') as batch_data:
			
			writer = csv.writer(batch_data)

			writer.writerow(sample)

def main(redis_client):
	listening = True
	opened = False
	# need while true?
	while listening:

		key, message = redis_client.blpop('sensor')
		streaming = True

		if message == 'START':

			print("Received start command")

			filter_flag = ts_api.TSS_FIND_ALL_KNOWN^ts_api.TSS_FIND_DNG
			com_port = get_comport()
			device = ts_api.TSUSBSensor(com_port=com_port)

			

			if device is not None:

				print(device)

				#disable magnetometer
				device.setCompassEnabled(enabled=False)
				device.setStreamingSlots(slot0='getTaredOrientationAsQuaternion')
				print("==================================================")
				print("Getting the streaming batch data.")

				while streaming:

					message = redis_client.lpop('sensor')

					if message == 'STOP':
						#close device
						device.close()
						streaming = False
						listening = False
						print("Device closed")
					else:
						# write batch data to csv file here
						sample = device.getStreamingBatch()
						data_to_csv(sample, opened)
						opened = True
						print(sample)
						print("=======================================\n")

	print("End of session")




if __name__ == '__main__':
	redis_client = redis.StrictRedis(host='localhost', port=6379)
	main(redis_client)
	