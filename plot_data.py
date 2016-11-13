import pandas as pd
import matplotlib.pyplot as plt

def main():

	filename = raw_input('Enter filename: ')
	df = pd.DataFrame.from_csv(filename)
	df.plot()
	leg = plt.legend()
	if leg:
		leg.draggable()
	plt.show()
	
if __name__ == '__main__':
	main()
