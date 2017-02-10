
"""
This script pre-processes YEI-3space IMU data.

Accelerometer and gyroscope data are re-oriented as follows:

With LED facing forward, default is X right, Y up, Z forward

Change to:

X = forward
Y = right
Z = down

Also Euler angles are calculated, with the original axes.
Angles are calculated in degrees.


"""



import pandas as pd
import math


"""
fieldnames = ['count','q1','q2','q3','q4','AccelRawX','AccelRawY','AccelRawZ','GyroRawX','GyroRawY','GyroRawZ']

X = forward
Y = right
Z = down

LED facing forward, X right, Y up, Z forward
WX =-wz; WY =-wx; WZ = wy;
AX = az; AY = ax; AZ =-ay;

"""

# Quaternion to Euler conversion

def quat_to_euler_theta(row):
	return math.degrees(math.asin(2*(row['q2'] * row['q1'] - row['q3'] * row['q4'])))
def quat_to_euler_phi(row):
	num = 2 * (row['q2'] * row['q3'] + row['q1'] * row['q4']) 
	denom = 1 - 2 * (pow(row['q1'], 2) + pow(row['q2'], 2))
	return math.degrees(math.atan2(num, denom))
def quat_to_euler_psi(row):
	num = 2 * (row['q1'] * row['q2'] + row['q3'] * row['q4']) 
	denom = 1 - 2 * (pow(row['q2'], 2) + pow(row['q3'], 2))
	return math.degrees(math.atan2(num, denom))

# Euler Radian to Degrees
def pitch_degrees(row):
	return math.degrees(row['pitch'])

def reorient_accel_x(row):
	return row['AccelRawZ']
def reorient_accel_y(row):
	return row['AccelRawX']
def reorient_accel_z(row):
	return -row['AccelRawY']

def reorient_gyro_x(row):
	return -row['GyroRawZ']
def reorient_gyro_y(row):
	return -row['GyroRawX']
def reorient_gyro_z(row):
	return row['GyroRawY']

def main():

	filename = raw_input('Enter filename: ')
	df = pd.DataFrame.from_csv(filename)
	
	

	# Re-orient gyroscope data - UNITS???

	df['GyroX'] = df.apply(lambda row: reorient_gyro_x(row), axis = 1)
	df['GyroY'] = df.apply(lambda row: reorient_gyro_y(row), axis = 1)
	df['GyroZ'] = df.apply(lambda row: reorient_gyro_z(row), axis = 1)

	# Add Euler angles

	df['pitch_deg'] = df.apply(lambda row: pitch_degrees(row), axis = 1)

	#df['theta'] = df.apply(lambda row: quat_to_euler_theta(row), axis = 1)
	#df['phi'] = df.apply(lambda row: quat_to_euler_phi(row), axis = 1)
	#df['psi'] = df.apply(lambda row: quat_to_euler_psi(row), axis =1)

	# Re-orient accelerometer data - in g's

	df['AccelX'] = df.apply(lambda row: reorient_accel_x(row), axis = 1)
	df['AccelY'] = df.apply(lambda row: reorient_accel_y(row), axis = 1)
	df['AccelZ'] = df.apply(lambda row: reorient_accel_z(row), axis = 1)


	# Save new CSV file with preprocessed Accel, Gyro, and Euler ONLY
	filename_list = filename.rsplit('.')
	new_name = filename_list[0] + "PRC" + ".csv"
	df.to_csv(new_name)


if __name__ == '__main__':
	main()