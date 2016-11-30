import pandas as pd
import matplotlib.pyplot as plt

def quat_to_euler_theta(row):
	return row['q1'] + row['q2']
def quat_to_euler_phi(row):
	return row['q3']
def quat_to_euler_psi(row):
	return row['q4']

def main():

	filename = raw_input('Enter filename: ')
	df = pd.DataFrame.from_csv(filename)
	
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

	df_quat['theta'] = df_quat.apply(lambda row: quat_to_euler_theta(row), axis = 1)
	df_quat['phi'] = df_quat.apply(lambda row: quat_to_euler_phi(row), axis = 1)
	df_quat['psi'] = df_quat.apply(lambda row: quat_to_euler_psi(row), axis =1)

	df_euler = df_quat[['theta', 'phi', 'psi']]
	fig, axes = plt.subplots(nrows=1, ncols=3)

	df_accel.plot(ax=axes[0])
	df_gyro.plot(ax=axes[1])
	df_euler.plot(ax=axes[2])
	
	leg = plt.legend()
	if leg:
		leg.draggable()
	plt.show()

if __name__ == '__main__':
	main()
