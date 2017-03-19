import pandas as pd
import matplotlib.pyplot as plt
import math



def main():

	filename = raw_input('Enter filename: ')
	df = pd.DataFrame.from_csv(filename)

	integrated = raw_input('Is data integrated? y/n : ')

	#df_euler = df_quat[['theta', 'phi', 'psi']]
	fig, axes = plt.subplots(nrows=4, ncols=1)
	#accel_to_plot = ['AccelX', 'AccelY', 'AccelZ']
	#gyro_to_plot = ['GyroX', 'GyroY', 'GyroZ']

	accel_to_plot = ['AccelRawX', 'AccelRawY', 'AccelRawZ']
	gyro_to_plot = ['GyroRawX', 'GyroRawY', 'GyroRawZ']
	
	euler_to_plot = ['Pitch', 'Yaw', 'Roll']

	#df_accel.plot(ax=axes[0])
	#df_gyro.plot(ax=axes[1])
	#df_euler.plot(ax=axes[2])
	
	#df.ix[:, df.columns.difference(list_to_plot)].plot(ax=axes[0])

	df.ix[:, accel_to_plot].plot(ax=axes[0])
	df.ix[:, gyro_to_plot].plot(ax=axes[1])
	df.ix[:, euler_to_plot].plot(ax=axes[2])

	if integrated == 'y':
		integrated_to_plot = ['theta_x', 'theta_y', 'theta_z']
		df.ix[:, integrated_to_plot].plot(ax = axes[3])

	leg = plt.legend()
	if leg:
		leg.draggable()
	plt.show()

if __name__ == '__main__':
	main()
