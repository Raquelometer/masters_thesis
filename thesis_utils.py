import serial.tools.list_ports
import threespace as ts_api
import csv
import OSC
from OSC import OSCMessage

# find comport that the 3-Space USB sensor is connected to

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

# Set up sensor with your defaults, can change sampling rate
# figure out interval stuff
# List defaults

def setup_sensor(device, interval_in):

	device.setFilterMode(mode = 1)

	#disable magnetometer
	device.setCompassEnabled(enabled=False)


	#Reset orientation
	device.setAxisDirections(ts_api.generateAxisDirections("YZX", neg_z = True))

	#stream Gyro, Orientation, Accelerometer
	device.setStreamingSlots(slot0 = 'getCorrectedGyroRate', slot1 = 'getUntaredOrientationAsEulerAngles',
					slot2='getCorrectedAccelerometerVector')

	#set sampling rate
	device.setStreamingTiming(interval = interval_in, duration = 0xFFFFFFFF, delay = 0)


# Save streaming data to csv file

def data_to_csv(sample, opened, name, sample_count):
	if not opened:
		with open(name, 'w') as batch_data:
		
			#Declare fieldnames
			fieldnames = ['time','GyroRawX','GyroRawY','GyroRawZ', 'Pitch', 'Yaw', 'Roll','AccelRawX','AccelRawY','AccelRawZ']
			#Set field names in the CSV file
			writer = csv.DictWriter(batch_data, fieldnames = fieldnames)

			#Create header
			writer.writeheader()

			# write sample to the file
			writer.writerow({'time' : sample_count,  
				'GyroRawX' : sample[0], 'GyroRawY' : sample[1], 'GyroRawZ' : sample[2],
				'Pitch' : sample[3], 'Yaw' : sample[4], 'Roll' : sample[5],
				'AccelRawX' : sample[6], 'AccelRawY' : sample[7], 'AccelRawZ' : sample[8]})
	else:
		with open(name, 'a') as batch_data:

			writer = csv.writer(batch_data)
			tuple_count = (sample_count,)
			sample_withcount = tuple_count + sample
			writer.writerow(sample_withcount)

# send OSC messages to max patch

def stream_to_max(client, value_msg, value):
	value_msg.append(value)
	client.send(value_msg)
	value_msg.pop(-1)

def gesture_to_max(client, gesture_msg, number_msg, gesture, number):
	stream_to_max(client, number_msg, number)
	stream_to_max(client, gesture_msg, gesture)

def delay_counter(curr_delay):
	if curr_delay > 0:
		curr_delay += 1
		if curr_delay == 25:
			curr_delay = 0
	return curr_delay


