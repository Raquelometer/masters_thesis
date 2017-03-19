import pandas as pd
import csv
import matplotlib.pyplot as plt



def main():
	
	files_list = raw_input("Enter filename of list of files: ")
	subject_id = raw_input("Enter subject id number")


	# read CSV file & load into list
	with open(files_list, 'r') as files:
		reader = csv.reader(files)
		files = list(reader)
		#print(files)


	num_files = len(files[0])

	for x in range(len(files[0])):
		
		files[0][x] = 'subjectTests/' + subject_id + '/' + 'PRC/'+ subject_id + '_' + files[0][x] + '_PRC' + '.csv'
		print(files[0][x])

	
	axis = raw_input('Enter axis name (theta_x, theta_y, theta_z): ')

	# get number of files, then names



	df1 = pd.DataFrame.from_csv(files[0][0])
	ax = df1[axis].plot()

	for idx in range(1, num_files):
		df2 = pd.DataFrame.from_csv(files[0][idx])
		df2[axis].plot(ax = ax)


	#fig, axes = plt.subplots(nrows=1, ncols=1)
	


	leg = plt.legend()
	if leg:
		leg.draggable()
	plt.show()

if __name__ == '__main__':
	main()