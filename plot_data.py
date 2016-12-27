import pandas as pd
import matplotlib.pyplot as plt
import math

def quat_to_euler_theta(row):
	return math.asin(2*(row['q2'] * row['q1'] - row['q3'] * row['q4']))
def quat_to_euler_phi(row):
	num = 2 * (row['q2'] * row['q3'] + row['q1'] * row['q4']) 
	denom = 1 - 2 * (pow(row['q1'], 2) + pow(row['q2'], 2))
	return math.atan2(num, denom)
def quat_to_euler_psi(row):
	num = 2 * (row['q1'] * row['q2'] + row['q3'] * row['q4']) 
	denom = 1 - 2 * (pow(row['q2'], 2) + pow(row['q3'], 2))
	return math.atan2(num, denom)

def main():

	filename = raw_input('Enter filename: ')
	df = pd.DataFrame.from_csv(filename)
	
	"""
	accel_series_x = pd.Series(df['AccelRawX'])
	accel_series_y = pd.Series(df['AccelRawY'])
	accel_series_z = pd.Series(df['AccelRawZ'])
	df_accel = pd.DataFrame( {'AccelX' : accel_series_x, 'AccelY' : accel_series_y, 'AccelZ' : accel_series_z})
	

	gyro_series_x = pd.Series(df['GyroRawX'])
	gyro_series_y = pd.Series(df['GyroRawY'])
	gyro_series_z = pd.Series(df['GyroRawZ'])
	df_gyro = pd.DataFrame( {'GyroX' : gyro_series_x, 'GyroY' : gyro_series_y, 'GyroZ' : gyro_series_z})
	
	q1_series = pd.Series(df['q1'])
	q2_series = pd.Series(df['q2'])
	q3_series = pd.Series(df['q3'])
	q4_series = pd.Series(df['q4'])
	df_quat = pd.DataFrame( {'q1' : q1_series, 'q2' : q2_series, 'q3' : q3_series, 'q4' : q4_series})

	

	df['theta'] = df.apply(lambda row: quat_to_euler_theta(row), axis = 1)
	df['phi'] = df.apply(lambda row: quat_to_euler_phi(row), axis = 1)
	df['psi'] = df.apply(lambda row: quat_to_euler_psi(row), axis =1)
	"""
	#df_euler = df_quat[['theta', 'phi', 'psi']]
	fig, axes = plt.subplots(nrows=3, ncols=1)
	accel_to_plot = ['AccelX', 'AccelY', 'AccelZ']
	gyro_to_plot = ['GyroX', 'GyroY', 'GyroZ']
	euler_to_plot = ['theta', 'phi', 'psi']

	#df_accel.plot(ax=axes[0])
	#df_gyro.plot(ax=axes[1])
	#df_euler.plot(ax=axes[2])
	
	#df.ix[:, df.columns.difference(list_to_plot)].plot(ax=axes[0])

	df.ix[:, accel_to_plot].plot(ax=axes[0])
	df.ix[:, gyro_to_plot].plot(ax=axes[1])
	df.ix[:, euler_to_plot].plot(ax=axes[2])

	leg = plt.legend()
	if leg:
		leg.draggable()
	plt.show()

if __name__ == '__main__':
	main()
