import sys
import redis

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import *


class App(QWidget):
	
	def __init__(self, redis_client):
		self.redis_client = redis_client
		super(QWidget, self).__init__()
		self.initUI()

	def initUI(self):

		self.setWindowTitle('Data Recorder')
		self.resize(200, 200)

		startBtn = QPushButton('Start', self)
		stopBtn = QPushButton('Stop', self)
		quitBtn = QPushButton('Quit', self)
		nameBtn = QPushButton('Enter Filename', self)

		stopBtn.move(80,0)
		quitBtn.move(0, 40)
		nameBtn.move(0, 80)

		startBtn.clicked.connect(self.on_click_Start)
		stopBtn.clicked.connect(self.on_click_Stop)
		quitBtn.clicked.connect(self.on_click_Quit)
		nameBtn.clicked.connect(self.on_click_Name)

		self.show()

	@pyqtSlot()
	def on_click_Start(self):
		print('start')
		self.redis_client.rpush('sensor', 'START')
	def on_click_Stop(self):
		print('stop')
		self.redis_client.rpush('sensor', 'STOP')
	def on_click_Quit(self):
		print('quit')
		self.redis_client.rpush('sensor', 'QUIT')
	def on_click_Name(self):
		print('name')
		self.redis_client.rpush('sensor', 'NAME')



if __name__ == '__main__':
	redis_client = redis.StrictRedis(host='localhost', port=6379)
	app = QApplication(sys.argv)

	ex = App(redis_client)
	sys.exit(app.exec_())
