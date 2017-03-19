import pandas as pd
import matplotlib.pyplot as plt
import math
import glob

SIGMAx3 = 0.03
deltaT = 1.0/100.0

def reset(attribute_list):
	for index, elt in enumerate(attribute_list):
		attribute_list[index] = 0

def integrate(row, vals, gyro_axis):

	# if gyro value is greater than 3xStd
	# start/keep integrating
	if abs(row[gyro_axis]) > SIGMAx3:

		vals[1] += deltaT * row[gyro_axis]
		vals[2] = 1

	# if integrating and gyro is less than 3xStd
	# Start counting up to 1/5 of a second
	if(vals[2] == 1 and abs(row[gyro_axis]) <= SIGMAx3):

		vals[0] += 1

	# if "stillness" detected for over 20 samples
	# Start over
	if vals[0] >= 20:
		
		reset(vals)
		

	return vals[1]


def main():

	std_count = 0
	curr_x = 0.0
	integrating = 0

	x_vals = [std_count, curr_x, integrating]
	y_vals = x_vals
	z_vals = x_vals

	'''
	
	files = glob.glob('subjectTests/01/Raw/*.csv')

	for csvfile in files:
		
		df = pd.DataFrame.from_csv(csvfile)


		df['theta_x'] = df.apply(lambda row: integrate(row, x_vals, 'GyroRawX'), axis = 1)
		df['theta_y'] = df.apply(lambda row: integrate(row, y_vals, 'GyroRawY'), axis = 1)
		df['theta_z'] = df.apply(lambda row: integrate(row, z_vals, 'GyroRawZ'), axis = 1)

		filename_list = csvfile.rsplit('.')
		new_filename = filename_list[0] + "_PRC" + ".csv"
		df.to_csv(new_filename)

		reset(x_vals)
		reset(y_vals)
		reset(z_vals)


	'''
	filename = raw_input('Enter filename: ')
	df = pd.DataFrame.from_csv(filename)


	df['theta_x'] = df.apply(lambda row: integrate(row, x_vals, 'GyroRawX'), axis = 1)
	df['theta_y'] = df.apply(lambda row: integrate(row, y_vals, 'GyroRawY'), axis = 1)
	df['theta_z'] = df.apply(lambda row: integrate(row, z_vals, 'GyroRawZ'), axis = 1)

	filename_list = filename.rsplit('.')
	new_filename = filename_list[0] + "_PRC" + ".csv"
	df.to_csv(new_filename)
	

if __name__ == '__main__':
	main()